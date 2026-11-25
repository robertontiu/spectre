"""Blend study: why does the SVS lead in the c1 chorus sound "like someone singing along to a speaker", and what fixes it.

python3 examples/vocals/svs/blend.py measure [variant ...]   # render + measure (default: all variants)
python3 examples/vocals/svs/blend.py master [variant ...]    # also master, write blend-<v>.mp3, Whisper word accuracy

Each variant is the c1 chorus (chorus.py: session 009 pre1 + chorus1, the hook sung by the lead)
with the vocal on `singer` `source: "svs"` (engine/svs.py, voice hanami) and a few changes. For the measurements every
variant is rendered four times (deterministic): full mix; vocal muted; reverb and delay returns off; vocal muted and
returns off. Vocal stem = full - muted; its dry part = (returns off) - (muted, returns off); the band likewise.
Results go to /tmp/spectre_svs/blend/<variant>/ and the printed table.
"""
import copy
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP = "/tmp/spectre_svs/blend"
SR = 44100
LYRICS = ("here you are round and round hold on tight round we go "
          "here you are round and round and you stay on the ride")

sys.path.insert(0, HERE)
import chorus  # noqa: E402

GTRS = ["gtrL", "gtrR", "lead", "fig", "figM", "figB", "chug"]


def base_track():
    tr = copy.deepcopy(chorus.SING_TRACK)
    tr["inst"] = {"type": "singer", "source": "svs", "voice": "hanami", "double": 0.35, "seed": 3}
    return tr


def v_tone(pj, tr):
    """Undo the "small speaker" voicing: c1's chain (hpf 150 Hz, +3 dB at 500 Hz for body),
    which on the SVS leaves the vocal 7-8 dB mid-heavy at 500 Hz-1 kHz and 4 dB short of air at 8 kHz against the
    band. Lower hpf, no 500 Hz boost, a small 800 Hz dip, air on top."""
    fx = tr["fx"]
    fx[0]["hz"] = 100
    fx[1] = {"type": "eq", "hz": 800, "gain_db": -2.5, "q": 0.9}
    fx.insert(3, {"type": "highshelf", "hz": 8000, "gain_db": 3})


def v_room(pj, tr):
    """The vocal in the band's room: the kit's early reflections (`room`), a reverb pre-delay so the tail separates
    from the words, a little more reverb send, 1 dB less level."""
    tr["fx"].insert(-1, {"type": "room", "size": 0.35, "mix": 0.3})
    tr["send_reverb"] = 0.28
    tr["reverb_predelay_ms"] = 35
    tr["fx"][-1]["db"] -= 1


def v_edges(pj, tr):
    """Softer phrase edges, a breath before phrases after a rest, a quieter double."""
    tr["inst"].update({"double": 0.2, "inhale": 0.3, "svs_fade_in_ms": 30, "svs_fade_out_ms": 120})


def v_carve(pj, tr):
    """Make room instead of riding on top: guitars dip 2.5 dB around 2.5 kHz, a slower glue compressor on the
    vocal."""
    for g in GTRS:
        if g in pj["tracks"]:
            pj["tracks"][g].setdefault("fx", []).append({"type": "eq", "hz": 2500, "gain_db": -2.5, "q": 0.7})
    tr["fx"].insert(-1, {"type": "comp", "threshold_db": -26, "ratio": 2, "attack_ms": 30, "release_ms": 200})
    tr["fx"][-1]["db"] += 1.5  # the glue compressor takes about 1.5 dB


def v_space(pj, tr):
    """Space without smearing the words: no early reflections on the voice; the shared reverb gets more of it after a
    60 ms pre-delay (the words stay clear, the tail sits in the band's reverb), the double a bit wider."""
    tr["send_reverb"] = 0.32
    tr["reverb_predelay_ms"] = 60
    tr["inst"]["double_pan"] = 0.7


def v_light_room(pj, tr):
    """A light touch of the kit's room (early reflections at a third of variant b's mix)."""
    tr["fx"].insert(-1, {"type": "room", "size": 0.3, "mix": 0.12})


def v_carve_only(pj, tr):
    for g in GTRS:
        if g in pj["tracks"]:
            pj["tracks"][g].setdefault("fx", []).append({"type": "eq", "hz": 2500, "gain_db": -2.5, "q": 0.7})


VARIANTS = {
    "svs": [],  # the approved Hanami chorus, through the engine
    "a": [v_tone],
    "b": [v_tone, v_room],
    "c": [v_tone, v_room, v_edges, v_carve],
    "d": [v_tone, v_space, v_edges, v_carve_only],
    "e": [v_tone, v_space, v_light_room, v_edges, v_carve_only],
}


def project(variant, mute=False, returns=True):
    d = chorus.session_copy(os.path.join(TMP, variant + ("-m" if mute else "") + ("" if returns else "-r")))
    pj = json.load(open(os.path.join(d, "project.json")))
    tr = base_track()
    for f in VARIANTS[variant]:
        f(pj, tr)
    if mute:
        tr["mute"] = True
    chorus.hook_chorus(pj, tr)
    if not returns:
        pj["mix"]["reverb"]["return_db"] = -200
        pj["mix"]["delay"]["return_db"] = -200
    json.dump(pj, open(os.path.join(d, "project.json"), "w"), indent=1)
    return d


def studio(args, d):
    while True:  # one heavy job at a time
        out = subprocess.run(["pgrep", "-af", "studio.py|master"], capture_output=True, text=True).stdout
        if not [ln for ln in out.splitlines() if "pgrep" not in ln and "blend.py" not in ln]:
            break
        time.sleep(10)
    subprocess.run([sys.executable, os.path.join(REPO, "engine", "studio.py")] + args, cwd=d,
                   env=dict(os.environ, BEAT_DIR=d), check=True, capture_output=True)


def render_all(variant):
    out = {}
    for mute in (False, True):
        for ret in (True, False):
            d = project(variant, mute, ret)
            studio(["render"], d)
            y, _ = sf.read(os.path.join(d, "renders", "v001.premaster.wav"), dtype="float32")
            out[(mute, ret)] = y.T
            meta = json.load(open(os.path.join(d, "renders", "v001.meta.json")))
    return out, meta


# ------------------------------------------------------------------------------------------------ measurements
def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x.T.astype(np.float64))


def band(x, lo, hi):
    from scipy import signal as sg
    return sg.sosfiltfilt(sg.butter(4, [lo, hi], "bandpass", fs=SR, output="sos"), x, axis=-1)


def db(e):
    return 10 * np.log10(e + 1e-20)


def env_db(m, win=0.01):
    w = int(win * SR)
    n = len(m) // w
    return db((m[:n * w].reshape(n, w) ** 2).mean(1)), w


def phrase_edges(vdry, sec_a):
    """Phrase starts/ends of the vocal (from its dry stem): rise time 10-90 % of the level at the start and the
    release 90-10 % at the end, on a 10 ms envelope."""
    e, w = env_db(vdry.mean(0))
    act = e > e.max() - 35
    rises, falls = [], []
    i = 0
    n = len(e)
    while i < n:
        if act[i]:
            j = i
            while j < n and (act[j:j + 15].any()):
                j += 1
            seg = e[i:j]
            if len(seg) > 20:
                top = np.percentile(seg, 90)
                lin = 10 ** (seg / 20)
                tl = 10 ** (top / 20)
                a10 = np.argmax(lin >= 0.1 * tl)
                a90 = np.argmax(lin >= 0.9 * tl)
                rises.append((a90 - a10) * 10)
                r = lin[::-1]
                b10 = np.argmax(r >= 0.1 * tl)
                b90 = np.argmax(r >= 0.9 * tl)
                falls.append((b90 - b10) * 10)
            i = j
        else:
            i += 1
    return float(np.median(rises)) if rises else float("nan"), float(np.median(falls)) if falls else float("nan")


def coherence(x, lo=500, hi=4000):
    b = band(x, lo, hi)
    return float(np.corrcoef(b[0], b[1])[0, 1])


def side_mid(x):
    m, s = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
    return float(db((s ** 2).mean()) - db((m ** 2).mean()))


def octave_excess(v, i):
    """Vocal minus band, dB per octave band, both normalised to the same total level."""
    out = {}
    tv, ti = db((v ** 2).mean()), db((i ** 2).mean())
    for c in (250, 500, 1000, 2000, 4000, 8000):
        bv, bi = band(v.mean(0), c / 1.41, min(c * 1.41, 20000)), band(i.mean(0), c / 1.41, min(c * 1.41, 20000))
        out[c] = round(float((db((bv ** 2).mean()) - tv) - (db((bi ** 2).mean()) - ti)), 1)
    return out


def measure(variant):
    r, meta = render_all(variant)
    full, muted, full_nr, muted_nr = r[(False, True)], r[(True, True)], r[(False, False)], r[(True, False)]
    sec = next(s for s in meta["sections"] if s["name"] == "chorus1")
    a, b = int(sec["start"] * SR), int(sec["end"] * SR)
    V, I = (full - muted)[:, a:b], muted[:, a:b]
    Vd, Id = (full_nr - muted_nr)[:, a:b], muted_nr[:, a:b]
    Vw, Iw = V - Vd, I - Id
    res = dict(variant=variant)
    res["vocal_vs_band_LU"] = round(lufs(V) - lufs(I), 1)
    res["vocal_wet_dB"] = round(float(db((Vw ** 2).mean()) - db((Vd ** 2).mean())), 1)  # wet (send returns) vs dry
    res["band_wet_dB"] = round(float(db((Iw ** 2).mean()) - db((Id ** 2).mean())), 1)
    res["coh_vocal"] = round(coherence(V), 2)
    res["coh_vocal_dry"] = round(coherence(Vd), 2)
    res["coh_band"] = round(coherence(I), 2)
    res["side_mid_vocal_dB"] = round(side_mid(V), 1)
    res["side_mid_band_dB"] = round(side_mid(I), 1)
    pv = band(V.mean(0), 1000, 4000)
    pi_ = band(I.mean(0), 1000, 4000)
    res["presence_1_4k_vs_band_dB"] = round(float(db((pv ** 2).mean()) - db((pi_ ** 2).mean())), 1)
    res["excess_per_octave"] = octave_excess(V, I)
    res["rise_ms"], res["release_ms"] = phrase_edges(Vd, a)
    # how much the vocal is "on top": share of 50 ms frames where the vocal is >6 dB above the band at 1-4 kHz
    ev, w = env_db(pv, 0.05)
    ei, _ = env_db(pi_, 0.05)
    act = ev > ev.max() - 30
    res["frames_vocal_over_band_6dB_%"] = round(100 * float(np.mean((ev - ei)[act] > 6)), 0)
    os.makedirs(TMP, exist_ok=True)
    json.dump(res, open(os.path.join(TMP, f"{variant}.json"), "w"), indent=1)
    print(json.dumps(res))
    return res


def word_accuracy(hyp, ref=LYRICS):
    h = re.sub(r"[^a-z ]", " ", hyp.lower()).split()
    r = ref.split()
    d = np.zeros((len(r) + 1, len(h) + 1), dtype=int)
    d[:, 0] = range(len(r) + 1)
    d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return 1 - d[len(r), len(h)] / len(r)


def whisper(path):
    os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(raw, dtype=np.float32), language="en", beam_size=5,
                           condition_on_previous_text=False)
    return " ".join(s.text.strip() for s in segs)


def master(variant):
    d = os.path.join(TMP, variant)
    if not os.path.exists(os.path.join(d, "renders", "v001.premaster.wav")):
        d = project(variant)
        studio(["render"], d)
    studio(["master", "v001", "--genre", "rock"], d)
    y, _ = sf.read(os.path.join(d, "renders", "v001.master.wav"))
    name = "blend-ref-svs" if variant == "svs" else f"blend-{variant}"
    chorus.mp3(y.T, name, HERE, TMP, kbps=88, normalize=False)
    text = whisper(os.path.join(HERE, name + ".mp3"))
    acc = word_accuracy(text)
    print(f"{variant}: Whisper on the mastered mix: {acc:.0%} words | {text}")
    res = json.load(open(os.path.join(TMP, f"{variant}.json"))) if os.path.exists(
        os.path.join(TMP, f"{variant}.json")) else {}
    res.update(whisper_words=round(acc, 3), whisper_text=text)
    json.dump(res, open(os.path.join(TMP, f"{variant}.json"), "w"), indent=1)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    cmd = sys.argv[1]
    for v in sys.argv[2:] or list(VARIANTS):
        {"measure": measure, "master": master}[cmd](v)
