"""SVS feasibility trial: DiffSinger voicebanks singing the "Here You Are" line and chorus (examples/vocals/svs/).

python3 examples/vocals/svs/build.py line [bank ...]     # <bank>-line-dry.mp3 + timing table
python3 examples/vocals/svs/build.py chorus <bank>       # <bank>-chorus.mp3, mixed and mastered exactly like c1-natural
python3 examples/vocals/svs/build.py timing <bank>       # dry chorus timing table (same metrics as joincheck --timing)
python3 examples/vocals/svs/build.py choir                # choir-line-dry.mp3: four takes, melody + a third below
<bank> is hanami, leona or tiger (each with its own vocoder), or hanami-potluck / leona-potluck (Potluck vocoder).
Renders are deterministic (onnxruntime seeded before the sessions are made).

Banks are OpenUtau DiffSinger voicebanks unpacked into ~/.cache/spectre/svs/<bank>/bank (never in git; see README.md
for where each comes from). The line and chorus use the same notes, tempo and lyrics as examples/vocals/tts/build.py
(b3/b1 line: B_MELODY at 100 bpm; c1: session 009's hookD voxD at 136 bpm, pre1 + chorus1). Phoneme timing comes from
each bank's duration model with the vowel groups aligned to the note onsets (OpenUtau's rule); nothing is hand-placed.
"""
import copy
import json
import os
import runpy
import shutil
import sys
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "engine"))
import dsinger  # noqa: E402

SR = 44100
CACHE = os.path.expanduser(os.environ.get("SPECTRE_SVS_DIR", "~/.cache/spectre/svs"))
TMP = "/tmp/spectre_svs"
BANKS = {"hanami": "Root", "leona": "acoustic_Core", "tiger": "tiger_fresh"}
LINE = "here you are round and round"
B_MELODY = "F#4:4 A4:4 B4:8 A4:4 F#4:2 A4:10"  # examples/vocals/tts/build.py, 100 bpm
CHORUS = ("here you are round and round hold on tight round we go "
          "here you are round and round and you stay on the ride")


def midi(name):
    from hand import note_to_midi
    return int(note_to_midi(name))


POTLUCK = os.path.join(CACHE, "potluck", "dsvocoder", "potluck_pc-nsf_lite.onnx")


def bank(name):
    """'<bank>' uses the bank's own vocoder; '<bank>-potluck' the commercial-friendly Potluck vocoder instead."""
    base, _, voc = name.partition("-")
    return dsinger.Bank(os.path.join(CACHE, base, "bank"), speaker=BANKS.get(base),
                        vocoder=POTLUCK if voc == "potluck" else None)


def wait_turn():
    """One heavy job at a time on this machine: wait while a render, master or singer job runs."""
    import subprocess
    while True:
        out = subprocess.run(["pgrep", "-af", "studio.py|master|singer"], capture_output=True, text=True).stdout
        mine = str(os.getpid())
        busy = [ln for ln in out.splitlines() if ln and not ln.startswith(mine + " ") and "pgrep" not in ln
                and "build.py" not in ln]
        if not busy:
            return
        print("waiting for:", busy[0][:100])
        time.sleep(15)


def mp3(y, name, kbps=128, normalize=True):
    import subprocess
    os.makedirs(TMP, exist_ok=True)
    y = np.asarray(y, dtype=np.float64)
    if normalize:
        y = y / max(np.abs(y).max(), 1e-9) * 0.89  # -1 dBFS peak, as tts/build.py
    wav = os.path.join(TMP, name + ".wav")
    sf.write(wav, y.T if y.ndim == 2 else y, SR)
    dst = os.path.join(HERE, name + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", f"{kbps}k", dst + ".tmp.mp3"], check=True)
    os.replace(dst + ".tmp.mp3", dst)
    print(dst, os.path.getsize(dst) // 1024, "KB")


# ------------------------------------------------------------------------------------------------ timing metrics
def timing(y, phones, score_ms, words, bpm, label=""):
    """Per syllable, against the score: the same quantities as tools/joincheck.py --timing. `phones` are the
    SVS's own phoneme boundaries (start, end ms) with the note each belongs to; 'on' = before the vowel group."""
    from scipy import signal as sg
    fp = 5.0
    hop = SR * fp / 1000
    band = sg.sosfiltfilt(sg.butter(3, [300, 3000], "bandpass", fs=SR, output="sos"), y)
    h = int(hop)
    nF = int(len(y) / hop)
    e = np.array([10 * np.log10(np.mean(band[max(0, int(k * hop) - h):int(k * hop) + h] ** 2) + 1e-12)
                  for k in range(nF)])
    de = np.convolve(np.r_[0, np.diff(np.convolve(e, np.ones(3) / 3, mode="same"))], np.ones(2) / 2, mode="same")
    vowels = set(dsinger_vowels)
    rows = []
    for k, sc in enumerate(score_ms):
        mine = [p for p in phones if p[3] == k]
        if not mine:
            continue
        a0 = mine[0][1]
        vow = [p for p in mine if p[0] in vowels]
        v0 = vow[0][1] if vow else a0
        vlen = sum(p[2] - p[1] for p in vow)
        sung = mine[-1][2] - a0
        lo, hi = max(int(a0 / fp) - 2, 0), min(int(v0 / fp) + 12, nF - 1)
        pc = (lo + int(np.argmax(de[lo:hi + 1]))) * fp
        rows.append(dict(word=words[k], score=sc / 1000, lead=v0 - a0, c_dev=a0 - sc, v_dev=v0 - sc, p_dev=pc - sc,
                         p=pc, sung=sung, cons=sung - vlen, vowel=vlen))
    beat = 60.0 / bpm
    for i, r in enumerate(rows):
        if i + 1 < len(rows):
            r["ioi_score"] = (rows[i + 1]["score"] - r["score"]) * 1000
            r["ioi_sung"] = rows[i + 1]["p"] - r["p"]
        else:
            r["ioi_score"] = r["ioi_sung"] = float("nan")
        ioi = r["ioi_score"] if np.isfinite(r["ioi_score"]) else 500.0
        r["jnd"] = max(6.0, 0.025 * ioi)
        r["flag"] = "!!" if abs(r["p_dev"]) > 3 * r["jnd"] else "!" if abs(r["p_dev"]) > r["jnd"] else ""
    print(f"\n== timing: {label}")
    print(f"{'syllable':9s} {'score s':>7s} {'lead':>5s} {'cons':>6s} {'vowel':>6s} {'P-ctr':>6s} {'/beat':>6s} "
          f"{'IOI sc':>6s} {'IOI sg':>6s} {'sung':>5s} {'cons':>5s} {'vowel':>5s}  flag")
    for r in rows:
        print(f"{r['word']:9s} {r['score']:7.3f} {r['lead']:5.0f} {r['c_dev']:+6.0f} {r['v_dev']:+6.0f} "
              f"{r['p_dev']:+6.0f} {r['p_dev'] / 1000 / beat:+6.2f} {r['ioi_score']:6.0f} {r['ioi_sung']:6.0f} "
              f"{r['sung']:5.0f} {r['cons']:5.0f} {r['vowel']:5.0f}  {r['flag']}")
    pd = np.array([r["p_dev"] for r in rows])
    di = np.array([r["ioi_sung"] - r["ioi_score"] for r in rows[:-1]])
    cons = [r for r in rows if r["lead"] > 0]
    summ = dict(p_mean=pd.mean(), p_sd=pd.std(), p_max=np.abs(pd).max(), ioi_sd=di.std(),
                jnd=sum(1 for r in rows if r["flag"]), jnd3=sum(1 for r in rows if r["flag"] == "!!"), n=len(rows),
                cons_start=np.median([r["c_dev"] for r in cons]) if cons else float("nan"),
                vowel=np.median([r["v_dev"] for r in cons]) if cons else float("nan"),
                lead=np.median([r["lead"] for r in cons]) if cons else float("nan"))
    print(f"P-centre vs score: mean {summ['p_mean']:+.0f} ms, sd {summ['p_sd']:.0f} ms, max |dev| {summ['p_max']:.0f} ms; "
          f"IOI error sd {summ['ioi_sd']:.0f} ms; beyond JND: {summ['jnd']}/{summ['n']}, beyond 3x JND: {summ['jnd3']}")
    print(f"syllables with a consonant onset: median consonant start vs beat {summ['cons_start']:+.0f} ms, "
          f"vowel vs beat {summ['vowel']:+.0f} ms, lead {summ['lead']:.0f} ms "
          f"(GTSinger singers: +1, +106, 91; docs/voice/GENERAL.md)")
    return rows, summ


dsinger_vowels = set()


def _vowels(b):
    dsinger_vowels.clear()
    dsinger_vowels.update(p for p, t in b.types.items() if t == "vowel")


# ------------------------------------------------------------------------------------------------ the line
def line_notes(start_ms=500.0, bpm=100):
    q = 60000.0 / bpm / 4
    t, out = start_ms, []
    for tok, w in zip(B_MELODY.split(), LINE.split()):
        n, ln = tok.split(":")
        out.append((t, float(ln) * q, midi(n), w))
        t += float(ln) * q
    s, d, m, w = out[-1]
    out[-1] = (s, d * 0.95, m, w)  # the engine's 0.95 legato on the last note (the others touch, as in OpenUtau)
    return out


def line(name):
    wait_turn()
    b = bank(name)
    _vowels(b)
    notes = line_notes()
    t = time.time()
    y, ph = dsinger.sing(b, notes, notes[-1][0] / 1000 + notes[-1][1] / 1000 + 1.0)
    dt = time.time() - t
    print(f"{name}: rendered {len(y) / SR:.1f} s in {dt:.1f} s on CPU (first call loads the models); "
          f"stages {', '.join(f'{k} {v:.1f} s' for k, v in b.timings.items())}")
    b.timings.clear()
    t = time.time()
    y2, _ = dsinger.sing(b, notes, len(y) / SR)
    print(f"{name}: second render (models loaded) {time.time() - t:.1f} s; "
          f"stages {', '.join(f'{k} {v:.1f} s' for k, v in b.timings.items())}")
    for p in ph:
        print(f"   {p[0]:4s} {p[1]:7.0f} {p[2]:7.0f}  note {p[3]} {p[4]}")
    timing(y, ph, [n[0] for n in notes], LINE.split(), 100, f"{name}, dry line")
    mp3(y, f"{name}-line-dry")
    return y, ph


# ------------------------------------------------------------------------------------------------ a small choir
CHOIR = [  # (bank, speaker, semitones under the melody (diatonic third in D major), pan)
    ("hanami", "Root", 0, -0.6), ("leona", "acoustic_Core", 0, 0.6),
    ("hanami", "Nectar", "third", -0.25), ("leona", "acoustic_CatNap", "third", 0.25)]
THIRD = {66: 62, 69: 66, 71: 67}  # F#4 -> D4, A4 -> F#4, B4 -> G4


def choir(_name=None):
    """Four separate DiffSinger takes of the line (two voicebanks, two vocal modes each), melody plus a third below,
    each with its own sampled pitch curve and a few ms of timing spread, panned: a dry few-voice texture (Potluck
    vocoder for all)."""
    wait_turn()
    notes = line_notes()
    n = int((notes[-1][0] + notes[-1][1]) / 1000 * SR) + SR
    out = np.zeros((2, n), dtype=np.float64)
    t = time.time()
    for i, (bk, spk, harm, pan) in enumerate(CHOIR):
        b = dsinger.Bank(os.path.join(CACHE, bk, "bank"), speaker=spk, vocoder=POTLUCK)
        ns = [(s, d, THIRD[m] if harm == "third" else m, w) for s, d, m, w in notes]
        y, _ = dsinger.sing(b, ns, n / SR, jitter_ms=15, seed=10 + i)
        y = y[:n] / max(np.sqrt(np.mean(y[np.abs(y) > 1e-3] ** 2)), 1e-9) * (0.8 if harm == "third" else 1.0)
        a = (pan + 1) * np.pi / 4
        out[0] += y * np.cos(a)
        out[1] += y * np.sin(a)
    print(f"choir: 4 takes in {time.time() - t:.0f} s")
    mp3(out, "choir-line-dry")


# ------------------------------------------------------------------------------------------------ the chorus
def chorus_score():
    """The chorus as joincheck measures it (session 009 hookD voxD, 136 bpm, starting at 0.3 s)."""
    pj = json.load(open(os.path.join(REPO, "sessions", "009-carousel", "project.json")))
    spec, bpm = pj["patterns"]["hookD"]["voxD"], pj["bpm"]
    q = 60000.0 / bpm / 4
    out = []
    for tok, w in zip(spec.split(), CHORUS.split()):
        st, nm, ln = tok.split(":")[:3]
        out.append((300.0 + float(st) * q, float(ln.rstrip("~!.")) * q * 0.95, midi(nm), w))
    return out, bpm


LEGATO_MS = 80.0  # gaps up to this are the engine's 0.95 note length, not rests: the notes touch (OpenUtau)


def chorus_timing(name):
    wait_turn()
    b = bank(name)
    _vowels(b)
    notes, bpm = chorus_score()
    os.makedirs(TMP, exist_ok=True)
    t = time.time()
    y, ph = dsinger.sing(b, notes, notes[-1][0] / 1000 + 2.0, legato_ms=LEGATO_MS)
    print(f"{name}: chorus {len(y) / SR:.1f} s rendered in {time.time() - t:.1f} s")
    sf.write(os.path.join(TMP, f"{name}-chorus-dry.wav"), y, SR)
    return timing(y, ph, [n[0] for n in notes], CHORUS.split(), bpm, f"{name}, dry chorus")


def svs_singer(name, legato_ms=LEGATO_MS):
    """A drop-in for singer.sing (same signature) that sings the notes with the DiffSinger bank instead, so the
    chorus goes through exactly the same track fx, sends, mix and master as c1-natural. The double is a second
    DiffSinger take (the pitch model samples a new curve each run), moved by a few ms and 7 cents, panned opposite,
    with singer.py's own double law and level normalisation."""
    import singer as _singer
    b = bank(name)
    words = CHORUS.split()

    def sing(p, notes, total_n):
        ns = [(nt["t0"] / SR * 1000, nt["n"] / SR * 1000, 69 + 12 * np.log2(nt["f"] / 440.0), words[i])
              for i, nt in enumerate(notes)]
        ns = [(a, d, int(round(m)), w) for a, d, m, w in ns]
        main, _ = dsinger.sing(b, ns, total_n / SR, legato_ms=legato_ms)
        main = main[:total_n]
        norm = _singer._norm(main)
        dbl = float(p.get("double", 0.0))
        if dbl <= 0:
            return (main * norm).astype(np.float32)
        take2, _ = dsinger.sing(b, ns, total_n / SR, legato_ms=legato_ms, jitter_ms=p.get("double_ms", 12),
                                seed=1, detune_cents=p.get("double_cents", 7))
        take2 = take2[:total_n]
        sp_ = float(p.get("double_pan", 0.5))
        a = (sp_ + 1) * np.pi / 4
        c = (-sp_ + 1) * np.pi / 4
        L = main * np.cos(c) + dbl * take2 * np.cos(a)
        R = main * np.sin(c) + dbl * take2 * np.sin(a)
        return (np.stack([L, R]) / (1 + dbl) * norm).astype(np.float32)
    return sing


def chorus(name):
    """c1-natural with the DiffSinger voice in place of the `tts` singer: same project, backing, vocal chain, level,
    sends and release master (rock)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ttsbuild", os.path.join(REPO, "examples", "vocals", "tts", "build.py"))
    ttsbuild = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ttsbuild)
    wait_turn()
    ttsbuild.TMP = TMP
    d = ttsbuild._session_copy()
    pj = json.load(open(os.path.join(d, "project.json")))
    tr = copy.deepcopy(ttsbuild.SING_TRACK)
    tr["inst"].update(ttsbuild.VARIANTS["c1-natural"])
    pj["tracks"]["sing"] = tr
    pj["patterns"]["hookSing"] = {"bars": 8, "sing": {"notes": pj["patterns"]["hookD"]["voxD"],
                                                      "lyrics": ttsbuild.HOOK_LYRICS}}
    sec = copy.deepcopy(next(s for s in pj["arrangement"] if s["name"] == "chorus1"))
    pre = next(s for s in pj["arrangement"] if s["name"] == "pre1")
    sec["play"] = [x for x in sec["play"] if x != "hook"] + ["hookSing"]
    pj["arrangement"] = [copy.deepcopy(pre), sec, {"name": "tail", "bars": 2, "play": []}]
    json.dump(pj, open(os.path.join(d, "project.json"), "w"), indent=1)
    import singer as _singer
    _singer.sing = svs_singer(name)  # studio's mono_voice calls singer.sing at render time
    os.environ["BEAT_DIR"] = d
    cwd = os.getcwd()
    os.chdir(d)
    t = time.time()
    for args in (["render"], ["master", "v001", "--genre", "rock"]):
        sys.argv = ["studio.py"] + args
        try:
            runpy.run_path(os.path.join(REPO, "engine", "studio.py"), run_name="__main__")
        except SystemExit as e:
            if e.code not in (None, 0):
                raise
    os.chdir(cwd)
    print(f"{name}: chorus render + master {time.time() - t:.0f} s")
    y, _ = sf.read(os.path.join(d, "renders", "v001.master.wav"))
    keep = os.path.join(TMP, f"{name}-chorus")
    shutil.rmtree(keep, ignore_errors=True)
    shutil.copytree(d, keep)
    mp3(y.T, f"{name}-chorus", kbps=88, normalize=False)  # as c1-natural.mp3


if __name__ == "__main__":
    try:
        with open("/proc/self/oom_score_adj", "w") as f:
            f.write("1000")
    except OSError:
        pass
    cmd, names = sys.argv[1], sys.argv[2:] or (["-"] if sys.argv[1] == "choir" else list(BANKS))
    for n in names:
        {"line": line, "chorus": chorus, "timing": chorus_timing, "choir": choir}[cmd](n)
