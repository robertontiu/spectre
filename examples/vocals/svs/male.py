"""Male voices (SoulX-Singer with VocalSet prompt singers; engine/svs_soulx.py, docs/voice/VOICES.md "Male voices"):
auditions and measurements.

python3 examples/vocals/svs/male.py audition      # voices/<id>.mp3 (the catalogue line an octave down, F#3-B3, dry),
                                                  # voices/ctl-<id>-low.mp3 / -high.mp3 (B2-E3, B3-E4), measurements
python3 examples/vocals/svs/male.py mix           # the line in a small band through the standing vocal chain
                                                  # (docs/voice/MIXING.md): voices/<id>-mix.mp3, Whisper, vocal vs band
python3 examples/vocals/svs/male.py steps         # 8 / 16 / 32 sampling steps on one voice (time, Whisper, pitch)
python3 examples/vocals/svs/male.py timing        # where each note's level rises against the written start (crude)

Measurements are the catalogue's (voices.py: tilt, breathiness, F1/F2 of "are", vibrato), plus: the pitch of each
note against the score (median cents over the middle of the note), Whisper small.en word accuracy (the line's words
found in order), and how much of the signal lies above 12 kHz (the model works at 24 kHz). Results are merged into
voices/measurements.json under the voice ids and written whole to voices/male.json.
A new phrase takes about 75 s on 2 CPU threads (cached afterwards). Scratch goes to /tmp/spectre_svs/male (deleted).
"""
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
sys.path.insert(0, HERE)
import voices as V  # noqa: E402

SR = 44100
OUT = os.path.join(HERE, "voices")
TMP = "/tmp/spectre_svs/male"
WORDS = "here you are round and round".split()
RANGE_DEMOS = {"low": -19, "high": -7}  # B2-E3 and B3-E4; the audition itself is at -12 (F#3-B3)
_W = {}


def male_voices():
    from svs import voices
    vs = voices()
    return [v for v in vs["voices"] if vs["banks"][v["bank"]].get("engine") == "soulx"]


def whisper(y, sr=SR):
    """(text, share of the line's words found in order) by faster-whisper small.en."""
    import librosa
    from faster_whisper import WhisperModel
    if "m" not in _W:
        _W["m"] = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
    x = librosa.resample(np.asarray(y, dtype=np.float32), orig_sr=sr, target_sr=16000)
    segs, _ = _W["m"].transcribe(x, language="en", beam_size=5, condition_on_previous_text=False)
    text = " ".join(s.text.strip() for s in segs)
    got = "".join(c for c in text.lower() if c.isalpha() or c == " ").split()
    lcs = [[0] * (len(got) + 1) for _ in range(len(WORDS) + 1)]
    for i, a in enumerate(WORDS):
        for j, b in enumerate(got):
            lcs[i + 1][j + 1] = lcs[i][j] + 1 if a == b else max(lcs[i][j + 1], lcs[i + 1][j])
    return text, lcs[-1][-1] / len(WORDS)


def pitch_cents(y, ns):
    """Median deviation from the written note over 25-90% of each note, in cents."""
    import pyworld as pw
    f0, _ = pw.harvest(np.asarray(y, dtype=np.float64), SR, f0_floor=60, f0_ceil=800, frame_period=5.0)
    out = []
    for nt in ns:
        a, b = int((nt["t0"] + 0.25 * nt["n"]) / SR * 200), int((nt["t0"] + 0.9 * nt["n"]) / SR * 200)
        v = f0[a:b]
        v = v[v > 0]
        out.append(round(float(np.median(1200 * np.log2(v / nt["f"])))) if len(v) > 3 else None)
    return out


def above_12k_db(y):
    s = np.abs(np.fft.rfft(y)) ** 2
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    return round(float(10 * np.log10(s[fr > 12000].sum() / s.sum() + 1e-20)), 1)


def mp3(y, path):
    import soundfile as sf
    os.makedirs(TMP, exist_ok=True)
    wav = os.path.join(TMP, os.path.basename(path)[:-4] + ".wav")
    y = np.asarray(y)
    sf.write(wav, (y / max(np.abs(y).max(), 1e-9) * 0.89).T if y.ndim == 2 else y / max(np.abs(y).max(), 1e-9) * 0.89,
             SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", path], check=True)


def dry(vid, transpose, **extra):
    import singer
    ns, n = V.notes(transpose)
    t = time.time()
    y = singer.sing(dict({"source": "svs", "voice": vid, "lyrics": V.LINE, "seed": 1}, **extra), ns, n)
    return y, ns, time.time() - t


def measure(y, ns):
    m = V.measure(y, ns)
    pc = pitch_cents(y, ns)
    text, acc = whisper(y)
    m.update(pitch_cents=pc, pitch_mean_abs_cents=round(float(np.mean([abs(p) for p in pc if p is not None])), 1),
             whisper=text, whisper_words=round(acc, 2), above_12k_db=above_12k_db(y))
    return m


def save(res):
    path = os.path.join(OUT, "male.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, "w"), indent=1)
    mp = os.path.join(OUT, "measurements.json")
    allm = json.load(open(mp)) if os.path.exists(mp) else {}
    keys = ("tilt_db", "breathiness", "F1", "F2", "vibrato_cents", "attack_ms", "what")
    for k, m in res.items():
        if "tilt_db" in m and not k.startswith(("ref-", "steps-")):
            allm[k] = {kk: m.get(kk, "") for kk in keys}
    json.dump(allm, open(mp, "w"), indent=1)


def audition():
    res = {}
    for v in male_voices():
        vid, tr = v["id"], int(v.get("audition_transpose", -12))
        y, ns, sec = dry(vid, tr)
        res[vid] = dict(measure(y, ns), what=f"the catalogue line at {tr:+d} semitones (F#3-B3), dry", render_s=round(sec))
        mp3(y, os.path.join(OUT, vid + ".mp3"))
        print(vid, json.dumps(res[vid]))
        for name, t2 in RANGE_DEMOS.items():
            y, ns, sec = dry(vid, t2)
            k = f"ctl-{vid}-{name}"
            res[k] = dict(measure(y, ns), what=f"the line at {t2:+d} semitones: the {name} end of the range")
            mp3(y, os.path.join(OUT, k + ".mp3"))
            print(k, json.dumps(res[k]))
    # the same measures on the default female voice at the written pitch, for comparison
    y, ns, _ = dry("hanami", 0)
    res["ref-hanami"] = dict(measure(y, ns), what="hanami at the written pitch (F#4-B4), the same measures")
    print("ref-hanami", json.dumps(res["ref-hanami"]))
    save(res)


# ------------------------------------------------------------------------------------------------ in a mix
def project(vid, transpose, gain_db, mute=False):
    """Four bars at 100 bpm: a bar of band, the two-bar line over electric piano, bass and drums, a bar of tail.
    The vocal chain is the standing one of docs/voice/MIXING.md section 2 (hpf 100, a dip near 800 Hz, +3 dB shelf at
    8 kHz, 3:1 compression, reverb behind a 60 ms pre-delay, a quiet wide double, soft phrase edges)."""
    from hand import note_to_midi
    import librosa
    steps, t = [], 0
    for tok in V.MELODY.split():
        n, ln = tok.split(":")
        name = librosa.midi_to_note(note_to_midi(n) + transpose, unicode=False)
        steps.append(f"{t}:{name}:{ln}")
        t += int(ln)
    return {
        "title": "male voice mix check", "bpm": 100, "swing": 0.5, "seed": 1,
        "tracks": {
            "kick": {"inst": {"type": "kick"}, "humanize_ms": 0},
            "snare": {"inst": {"type": "snare"}, "humanize_ms": 0},
            "hat": {"inst": {"type": "hat"}, "gain_db": -4, "humanize_ms": 0},
            "bass": {"inst": {"type": "ebass"}, "humanize_ms": 0},
            "keys": {"inst": {"type": "ep", "bright": 0.6}, "send_reverb": 0.2, "humanize_ms": 0,
                     "fx": [{"type": "hpf", "hz": 140}]},
            "vox": {"inst": {"type": "singer", "source": "svs", "voice": vid, "seed": 1, "double": 0.2,
                             "double_pan": 0.7, "svs_fade_in_ms": 30, "svs_fade_out_ms": 120},
                    "humanize_ms": 0, "gain_db": 6, "mute": mute, "send_reverb": 0.32,
                    "reverb_predelay_ms": 60,
                    "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 800, "gain_db": -2.5, "q": 0.9},
                           {"type": "highshelf", "hz": 8000, "gain_db": 3},
                           {"type": "comp", "threshold_db": -22, "ratio": 3}, {"type": "gain", "db": gain_db}]}},
        "patterns": {
            "beat": {"bars": 1, "kick": "X.......x.x.....", "snare": "....X.......X...", "hat": "x.x.x.x.x.x.x.x."},
            "band": {"bars": 2, "keys": {"chords": "Dmaj7:16 F#m7:16", "style": "sustain", "register": "A3",
                                         "vel": 0.6},
                     "bass": "0:D2:6 6:D2:2 8:A1:8 16:F#1:6 22:F#1:2 24:C#2:8"},
            "tail": {"bars": 1, "keys": {"chords": "Dmaj7:16", "style": "sustain", "register": "A3", "vel": 0.5},
                     "bass": "0:D2:12"},
            "line": {"bars": 2, "vox": {"notes": " ".join(steps), "lyrics": V.LINE}}},
        "arrangement": [{"name": "in", "bars": 1, "play": ["beat", "tail"]},
                        {"name": "hook", "bars": 2, "play": ["beat", "band", "line"]},
                        {"name": "out", "bars": 1, "play": ["beat", "tail"]}],
        "mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -6, "lpf": 7000}},
        "master": {"lufs": -11}}


def render(pj, name):
    import soundfile as sf
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    json.dump(pj, open(os.path.join(d, "project.json"), "w"))
    env = dict(os.environ, BEAT_DIR=d)
    r = subprocess.run([sys.executable, os.path.join(REPO, "engine", "studio.py"), "render"], cwd=d, env=env,
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    pre, _ = sf.read(os.path.join(d, "renders", "v001.premaster.wav"), dtype="float32")
    quick, _ = sf.read(os.path.join(d, "renders", "v001.wav"), dtype="float32")
    return pre.T, quick.T


def lufs(x):
    import pyloudnorm
    return float(pyloudnorm.Meter(SR).integrated_loudness(np.asarray(x.T, dtype=np.float64)))


def mix_check(vid, transpose):
    """Vocal against band (full premaster minus the vocal-muted one, docs/voice/MIXING.md section 6) and Whisper on
    the hook bars of the quick master. The gain after the vocal chain is set so that the vocal sits about 1 LU under the band."""
    bar = int(4 * 60 / 100 * SR)
    a, b = bar - SR // 2, 3 * bar + SR // 2
    gain = 0.0
    for _ in range(4):
        full, quick = render(project(vid, transpose, gain), f"{vid}-full")
        band, _ = render(project(vid, transpose, gain, mute=True), f"{vid}-band")
        n = min(full.shape[1], band.shape[1])
        vocal = full[:, :n] - band[:, :n]
        lu = lufs(vocal[:, bar:3 * bar]) - lufs(band[:, bar:3 * bar])
        if abs(lu + 1.0) < 0.5:
            break
        gain += -1.0 - lu
    text, acc = whisper(quick[:, a:b].mean(0))
    stext, sacc = whisper(vocal[:, a:b].mean(0))
    return dict(vocal_vs_band_lu=round(lu, 1), vocal_gain_db=round(gain, 1), whisper_mix=text,
                whisper_mix_words=round(acc, 2), whisper_stem=stext, whisper_stem_words=round(sacc, 2)), quick


def mix():
    res = {}
    jobs = [(v["id"], int(v.get("audition_transpose", -12))) for v in male_voices()] + [("hanami", 0)]
    for vid, tr in jobs:
        m, quick = mix_check(vid, tr)
        key = f"{vid}-mix" if vid != "hanami" else "ref-hanami-mix"
        res[key] = dict(m, what="the line in a small band (ep, bass, drums) through the standing vocal chain, "
                                "quick master")
        if vid != "hanami":
            mp3(quick, os.path.join(OUT, f"{vid}-mix.mp3"))
        print(key, json.dumps(res[key]))
    save(res)


def timing():
    """Per note: the fastest rise of the 300-3000 Hz level within 150 ms of the written start, in ms (a crude
    P-centre: words that begin with a vowel or a glide have no sharp rise, so read the spread, not single values)."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, [300, 3000], btype="band", fs=SR, output="sos")
    res = {}
    for vid, tr in [(v["id"], int(v.get("audition_transpose", -12))) for v in male_voices()] + [("hanami", 0)]:
        y, ns, _ = dry(vid, tr)
        env = np.convolve(sosfiltfilt(sos, y.astype(np.float64)) ** 2, np.hanning(882) / 441, "same")
        d = np.gradient(np.convolve(10 * np.log10(env + 1e-10), np.ones(441) / 441, "same"))
        w = int(0.15 * SR)
        devs = [round((max(0, nt["t0"] - w) + int(np.argmax(d[max(0, nt["t0"] - w):nt["t0"] + w])) - nt["t0"]) / 44.1)
                for nt in ns]
        key = f"timing-{vid}" if vid != "hanami" else "ref-hanami-timing"
        res[key] = dict(rise_vs_note_start_ms=devs, mean_ms=round(float(np.mean(devs))),
                        sd_ms=round(float(np.std(devs))), what="fastest 300-3000 Hz level rise against each note start")
        print(key, json.dumps(res[key]))
    save(res)


def steps():
    res = {}
    vid = male_voices()[0]["id"]
    for st in (8, 16, 32):
        y, ns, sec = dry(vid, -12, svs_steps=st)
        res[f"steps-{vid}-{st}"] = dict(measure(y, ns), render_s=round(sec), what=f"{st} sampling steps")
        print(st, json.dumps(res[f"steps-{vid}-{st}"]))
    save(res)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    for cmd in sys.argv[1:] or ["audition", "mix"]:
        {"audition": audition, "mix": mix, "steps": steps, "timing": timing}[cmd]()
    shutil.rmtree(TMP, ignore_errors=True)
