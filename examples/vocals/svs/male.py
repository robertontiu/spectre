"""The male voices, `hanami-male` and `hanami-male-es` (docs/voice/VOICES.md "Male voices"): auditions and measurements.
Hanami sings the line an octave above the written notes and the synthesizer moves it down (a voice's `sing_up`).

python3 examples/vocals/svs/male.py audition   # voices/hanami-male.mp3 (the catalogue line an octave down, F#3-B3)
                                               # and voices/hanami-male-es.mp3 ("quiero quedarme aquí contigo",
                                               # E3-B3), dry; the range ends (B2-E3, B3-E4) measured, no audio
python3 examples/vocals/svs/male.py takes      # Whisper and pitch over seeds 1-8 (and Hanami's own line for reference)
python3 examples/vocals/svs/male.py gender     # gender 0 to -0.4: Whisper, tilt, breathiness
python3 examples/vocals/svs/male.py mix        # the lines in a small band through the standing vocal chain
                                               # (docs/voice/MIXING.md section 2): voices/hanami-male-mix.mp3,
                                               # hanami-male-es-mix.mp3, Whisper in the mix and on the vocal alone

Measures: the catalogue's (voices.py: tilt, breathiness, F1/F2 of "are" by LPC, vibrato), the pitch of each note
against the score (median cents over 25-90% of the note), Whisper (small.en; Spanish: small, forced to Spanish, as
spanish.py), the energy above 12 kHz, artefact proxies (level flutter: the 8-40 Hz part of the level inside held
notes, dB; pitch jitter: the median 5 ms frame-to-frame f0 step inside held notes, cents) and the timing against
Hanami's own render of the line an octave up (per-note onset lag and the lag of the whole level envelope, ms).
Results: voices/hanami-male.json. Scratch goes to /tmp/spectre_svs/male (deleted).
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
import spanish as ES  # noqa: E402
import voices as V  # noqa: E402

SR = 44100
OUT = os.path.join(HERE, "voices")
TMP = "/tmp/spectre_svs/male"
WORDS = "here you are round and round".split()
ES_LYRICS, ES_MELODY = ES.LINES[1]  # "quiero quedarme aquí contigo", B4 ... E4; sung an octave down
RANGE = {"low": -19, "high": -7}  # B2-E3 and B3-E4; the audition itself is at -12 (F#3-B3)
_W = {}


# ------------------------------------------------------------------------------------------------ lines
def line(lang, transpose=-12):
    """(notes, total samples, lyrics, bpm) of the audition line: English (the catalogue's) or Spanish."""
    if lang == "es":
        from hand import note_to_midi
        q = 60.0 / ES.BPM / 4
        t, out = 0.3, []
        for tok in ES_MELODY.split():
            n, ln = tok.split(":")
            out.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), vel=0.9, glide=False,
                            f=440 * 2 ** ((note_to_midi(n) + transpose - 69) / 12)))
            t += float(ln) * q
        return out, int((t + 0.8) * SR), ES_LYRICS, ES.BPM
    ns, n = V.notes(transpose)
    return ns, n, V.LINE, 100


def sing(voice, lang, transpose=-12, **extra):
    """(wave, notes, seconds) of a voice's dry line ("hanami" sings it an octave up: the reference)."""
    import singer
    if voice == "hanami":
        transpose += 12
    ns, n, lyrics, _ = line(lang, transpose)
    vid = voice + ("-es" if lang == "es" else "")
    t = time.time()
    y = singer.sing(dict({"source": "svs", "voice": vid, "lyrics": lyrics, "seed": 1}, **extra), ns, n)
    return np.asarray(y, dtype=np.float32), ns, time.time() - t


# ------------------------------------------------------------------------------------------------ measures
def whisper(y, sr=SR):
    """(text, share of the English line's words found in order) by faster-whisper small.en."""
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


def artefacts(y, ns):
    import pyworld as pw
    from scipy.signal import butter, sosfiltfilt
    x = np.asarray(y, dtype=np.float64)
    f0, _ = pw.harvest(x, SR, f0_floor=60, f0_ceil=1100, frame_period=5.0)
    lev = 10 * np.log10(np.convolve(x ** 2, np.ones(441) / 441, "same")[::220] + 1e-12)  # 200 frames a second
    sos = butter(2, [8, 40], btype="band", fs=200, output="sos")
    fl, jit = [], []
    for nt in ns:
        if nt["n"] < 0.3 * SR:
            continue
        a, b = int((nt["t0"] + 0.3 * nt["n"]) / SR * 200), int((nt["t0"] + 0.9 * nt["n"]) / SR * 200)
        if b - a > 30:
            fl.append(float(np.std(sosfiltfilt(sos, lev[a:b]))))
        v = f0[a:b]
        if (v > 0).sum() > 10 and (v > 0).all():
            jit.append(float(np.median(np.abs(np.diff(1200 * np.log2(v))))))
    return dict(flutter_db=round(float(np.mean(fl)), 2) if fl else None,
                jitter_cents=round(float(np.mean(jit)), 2) if jit else None)


def note_lags(y, ns, ref, win_ms=(150, 250), max_ms=80):
    """Per note: the lag (ms, positive = later than the reference) at which this render's level onsets around the
    note start line up best with the reference's (cross-correlation of the rectified rise of the broadband level,
    1 ms steps, searched over +-80 ms)."""
    def onset(x):
        lev = 10 * np.log10(np.convolve(np.asarray(x, dtype=np.float64) ** 2, np.ones(441) / 441, "same")[::44] + 1e-9)
        lev = np.maximum(lev, lev.max() - 50)
        return np.maximum(np.gradient(np.convolve(lev, np.hanning(15) / 7.0, "same")), 0)
    oa, ob = onset(y), onset(ref)
    out = []
    for nt in ns:
        c = int(nt["t0"] / 44)
        a, b = max(0, c - win_ms[0]), min(len(oa), len(ob), c + win_ms[1])
        p, q = oa[a:b], ob[a:b]
        best = (-1.0, 0)
        for k in range(-max_ms, max_ms + 1):
            pp, qq = p[max(0, k):len(p) + min(0, k)], q[max(0, -k):len(q) + min(0, -k)]
            v = float(np.dot(pp, qq) / (np.linalg.norm(pp) * np.linalg.norm(qq) + 1e-12))
            if v > best[0]:
                best = (v, k)
        out.append(best[1] * 44 / 44.1)
    return out


def timing(y, ns, ref):
    """Against Hanami's own render of the line: per-note onset lag (ms, mean and sd; the detector's floor is about
    16 ms sd) and the lag of the whole level envelope (positive = later than her)."""
    lg = np.array(note_lags(y, ns, ref))
    ea, eb = (np.convolve(np.abs(x[:min(len(y), len(ref))]).astype(np.float64), np.ones(441) / 441, "same")[::44]
              for x in (y, ref))
    ea, eb = ea - ea.mean(), eb - eb.mean()
    lags = np.arange(-150, 151)
    cc = [float(np.dot(ea[max(0, k):len(ea) + min(0, k)], eb[max(0, -k):len(eb) + min(0, -k)])) for k in lags]
    return dict(note_lag_ms=[round(float(x)) for x in lg], lag_mean_ms=round(float(lg.mean()), 1),
                lag_sd_ms=round(float(lg.std()), 1), envelope_lag_ms=round(float(lags[int(np.argmax(cc))] * 44 / 44.1), 1))


def words(y, lang):
    if lang == "es":
        text, det, prob = ES.whisper(y)
        return text, float(ES.word_accuracy(ES_LYRICS, text)), f"{det} {prob:.2f}"
    text, acc = whisper(y)
    return text, acc, None


def measure(y, ns, lang, ref=None):
    m = V.measure(y, ns)
    if lang == "es":  # the LPC pair is taken on note 3, which is the long "are" only in the English line
        m.pop("F1", None)
        m.pop("F2", None)
    pc = pitch_cents(y, ns)
    text, acc, det = words(y, lang)
    m.update(pitch_cents=pc, pitch_mean_abs_cents=round(float(np.mean([abs(p) for p in pc if p is not None])), 1),
             whisper=text, whisper_words=round(acc, 2), **({"whisper_detected": det} if det else {}),
             above_12k_db=above_12k_db(y), **artefacts(y, ns))
    if ref is not None:
        m["timing"] = timing(y, ns, ref)
    return m


def mp3(y, path):
    import soundfile as sf
    os.makedirs(TMP, exist_ok=True)
    wav = os.path.join(TMP, os.path.basename(path)[:-4] + ".wav")
    y = np.asarray(y)
    sf.write(wav, (y / max(np.abs(y).max(), 1e-9) * 0.89).T if y.ndim == 2 else y / max(np.abs(y).max(), 1e-9) * 0.89,
             SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", path], check=True)


def save(res):
    path = os.path.join(OUT, "hanami-male.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, "w"), indent=1, ensure_ascii=False)


# ------------------------------------------------------------------------------------------------ commands
def audition():
    res = {}
    for lang in ("en", "es"):
        sfx = "-es" if lang == "es" else ""
        ref, ref_ns, _ = sing("hanami", lang)
        res["ref-hanami" + sfx] = dict(measure(ref, ref_ns, lang), what="Hanami's own render of the line, an octave up")
        y, ns, sec = sing("hanami-male", lang)
        res["hanami-male" + sfx] = dict(measure(y, ns, lang, ref), render_s=round(sec), what=(
            "the Spanish line, E3-B3, dry" if lang == "es" else "the catalogue line, F#3-B3, dry"))
        mp3(y, os.path.join(OUT, f"hanami-male{sfx}.mp3"))
        print("hanami-male" + sfx, json.dumps(res["hanami-male" + sfx], ensure_ascii=False))
    for name, tr in RANGE.items():
        y, ns, _ = sing("hanami-male", "en", tr)
        res[f"range-{name}"] = dict(measure(y, ns, "en"), what=f"the line at {tr:+d} semitones: the {name} end")
        print(name, json.dumps(res[f"range-{name}"]))
    save(res)


def takes():
    """How often a take reads: the English line with seeds 1-8 (another seed is another performance)."""
    import singer
    res = {}
    for vid in ("hanami-male", "hanami"):
        ns, n, lyrics, _ = line("en", 0 if vid == "hanami" else -12)
        rows = []
        for seed in range(1, 9):
            y = np.asarray(singer.sing({"source": "svs", "voice": vid, "lyrics": lyrics, "seed": seed}, ns, n),
                           dtype=np.float32)
            text, acc = whisper(y)
            pc = pitch_cents(y, ns)
            rows.append(dict(seed=seed, whisper=text, words=round(acc, 2),
                             pitch_mean_abs_cents=round(float(np.mean([abs(p) for p in pc if p is not None])), 1)))
            print(vid, json.dumps(rows[-1]))
        res[f"takes-{vid}"] = dict(takes=rows, all_words=sum(x["words"] == 1.0 for x in rows), of=len(rows),
                                   what=f"{vid}: the catalogue line over seeds 1-8, dry")
    save(res)


def gender():
    res = {}
    for g in (0.0, -0.2, -0.3, -0.4):
        y, ns, _ = sing("hanami-male", "en", gender=g)
        text, acc = whisper(y)
        m = V.measure(y, ns)
        res[f"gender{g}"] = dict(whisper=text, whisper_words=round(acc, 2), tilt_db=m["tilt_db"],
                                 breathiness=m["breathiness"], **artefacts(y, ns))
        print(g, json.dumps(res[f"gender{g}"]))
    save(res)


def project(voice, lang, gain_db, mute=False, transpose=-12):
    """Four bars: a bar of band, the two-bar line over electric piano, bass and drums, a bar of tail. The vocal chain
    is the standing one of docs/voice/MIXING.md section 2 (hpf 100, a dip near 800 Hz, +3 dB shelf at 8 kHz, 3:1
    compression, reverb behind a 60 ms pre-delay, a quiet wide double, soft phrase edges)."""
    import librosa
    from hand import note_to_midi
    vid = voice + ("-es" if lang == "es" else "")
    mel, lyrics = (ES_MELODY, ES_LYRICS) if lang == "es" else (V.MELODY, V.LINE)
    steps, t = [], 0
    for tok in mel.split():
        n, ln = tok.split(":")
        steps.append(f"{t}:{librosa.midi_to_note(note_to_midi(n) + transpose, unicode=False)}:{ln}")
        t += int(ln)
    pj = {
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
            "line": {"bars": 2, "vox": {"notes": " ".join(steps), "lyrics": lyrics}}},
        "arrangement": [{"name": "in", "bars": 1, "play": ["beat", "tail"]},
                        {"name": "hook", "bars": 2, "play": ["beat", "band", "line"]},
                        {"name": "out", "bars": 1, "play": ["beat", "tail"]}],
        "mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -6, "lpf": 7000}},
        "master": {"lufs": -11}}
    if lang == "es":  # the Spanish line gets its own tempo and chords
        pj["bpm"] = ES.BPM
        pj["patterns"]["band"] = {"bars": 2, "keys": {"chords": "Em7:16 Cmaj7:8 D:8", "style": "sustain",
                                                      "register": "A3", "vel": 0.6},
                                  "bass": "0:E2:6 6:E2:2 8:B1:8 16:C2:6 22:C2:2 24:D2:8"}
        pj["patterns"]["tail"] = {"bars": 1, "keys": {"chords": "Em7:16", "style": "sustain", "register": "A3",
                                                      "vel": 0.5}, "bass": "0:E2:12"}
    return pj


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


def mix_check(voice, lang, transpose=-12):
    """The vocal set about 1 LU under the band (full premaster minus the vocal-muted one, docs/voice/MIXING.md
    section 6), then Whisper on the hook bars of the quick master and on the vocal alone."""
    bar = int(4 * 60 / (ES.BPM if lang == "es" else 100) * SR)
    a, b = bar - SR // 2, 3 * bar + SR // 2
    gain = 0.0
    for _ in range(4):
        full, quick = render(project(voice, lang, gain, transpose=transpose), f"{voice}-{lang}-full")
        band, _ = render(project(voice, lang, gain, mute=True, transpose=transpose), f"{voice}-{lang}-band")
        n = min(full.shape[1], band.shape[1])
        vocal = full[:, :n] - band[:, :n]
        lu = lufs(vocal[:, bar:3 * bar]) - lufs(band[:, bar:3 * bar])
        if abs(lu + 1.0) < 0.5:
            break
        gain += -1.0 - lu
    text, acc, _ = words(quick[:, a:b].mean(0), lang)
    stext, sacc, _ = words(vocal[:, a:b].mean(0), lang)
    return dict(vocal_vs_band_lu=round(lu, 1), vocal_gain_db=round(gain, 1), whisper_mix=text,
                whisper_mix_words=round(acc, 2), whisper_stem=stext, whisper_stem_words=round(sacc, 2)), quick


def mix():
    res = {}
    for lang in ("en", "es"):
        sfx = "-es" if lang == "es" else ""
        m, quick = mix_check("hanami-male", lang)
        res[f"hanami-male{sfx}-mix"] = dict(m, what="the line in a small band (ep, bass, drums) through the standing "
                                                    "vocal chain, quick master")
        mp3(quick, os.path.join(OUT, f"hanami-male{sfx}-mix.mp3"))
        print(f"hanami-male{sfx}-mix", json.dumps(m, ensure_ascii=False))
        m, _ = mix_check("hanami", lang, transpose=0)
        res[f"ref-hanami{sfx}-mix"] = dict(m, what="Hanami an octave above in the same band and chain")
        print(f"ref-hanami{sfx}-mix", json.dumps(m, ensure_ascii=False))
    save(res)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    for cmd in sys.argv[1:] or ["audition"]:
        {"audition": audition, "takes": takes, "gender": gender, "mix": mix}[cmd]()
    shutil.rmtree(TMP, ignore_errors=True)
