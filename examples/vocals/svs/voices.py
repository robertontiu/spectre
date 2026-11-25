"""Voice catalogue auditions and measurements for singer source "svs" (docs/voice/VOICES.md, engine/voices.json).

python3 examples/vocals/svs/voices.py            # every voice and control demo: voices/<id>.mp3 + measurements
Each audition is the same two bars at 100 bpm ("here you are, round and round", F#4-B4 for the voices; the control
demos move one setting), dry, through the engine (singer.sing with source "svs"), so it is exactly what a track gets.
Measurements (on the dry render; pyworld analysis): spectral tilt (energy 2-5 kHz vs 0.2-1 kHz on voiced frames),
breathiness (mean aperiodicity 1-4 kHz, 0 = pure harmonics, 1 = noise), F1/F2 of the long "are" vowel (LPC),
vibrato (f0 standard deviation around the note on the long notes, cents), attack (10-90 % rise of each phrase), level.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
SR = 44100
OUT = os.path.join(HERE, "voices")
LINE = "here you are, round and round"
MELODY = "F#4:4 A4:4 B4:8 A4:4 F#4:2 A4:10"

DEMOS = {  # control demos: id -> (voice, extra params, transpose, what it shows)
    "ctl-hanami-gender-dark": ("hanami", {"gender": -0.5}, 0, "gender -0.5: formants down (longer tract: darker, older)"),
    "ctl-hanami-gender-bright": ("hanami", {"gender": 0.5}, 0, "gender +0.5: formants up (shorter tract: brighter, younger)"),
    "ctl-hanami-male-fake": ("hanami", {"gender": -1.0}, -12, "gender -1 an octave down: how far it is from a male"),
    "ctl-hanami-velocity-slow": ("hanami", {"velocity": 0.6}, 0, "velocity 0.6: slower, softer consonants"),
    "ctl-hanami-velocity-fast": ("hanami", {"velocity": 1.6}, 0, "velocity 1.6: faster, crisper consonants"),
    "ctl-hanami-low": ("hanami", {}, -7, "the line a fifth lower (B3-E4): the bottom of the range"),
    "ctl-hanami-high": ("hanami", {}, 7, "the line a fifth higher (C#5-F#5): the top of the range"),
    "ctl-leona-soft-dark": ("leona-soft", {"gender": -0.5}, 0, "LEONA soft with gender -0.5 (formants down)"),
}


def notes(transpose=0, bpm=100, start=0.3):
    from hand import note_to_midi
    q = 60.0 / bpm / 4
    t, out = start, []
    for tok in MELODY.split():
        n, ln = tok.split(":")
        m = note_to_midi(n) + transpose
        out.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), f=440 * 2 ** ((m - 69) / 12), vel=0.9,
                        glide=False))
        t += float(ln) * q
    return out, int((t + 0.8) * SR)


def measure(y, ns):
    import pyworld as pw
    x = y.astype(np.float64)
    f0, t = pw.harvest(x, SR, f0_floor=70, f0_ceil=1200, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, SR)
    ap = pw.d4c(x, f0, t, SR)
    fr = np.fft.rfftfreq((sp.shape[1] - 1) * 2, 1 / SR)
    v = f0 > 0
    lo = sp[v][:, (fr >= 200) & (fr < 1000)].sum(1)
    hi = sp[v][:, (fr >= 2000) & (fr < 5000)].sum(1)
    tilt = float(np.median(10 * np.log10(hi / lo)))
    breath = float(np.median(ap[v][:, (fr >= 1000) & (fr < 4000)].mean(1)))
    # vowel of "are" (third note): F1/F2 by LPC on its middle 300 ms
    n3 = ns[2]
    mid = n3["t0"] + n3["n"] // 2
    seg = x[mid - int(0.15 * SR): mid + int(0.15 * SR)]
    import librosa
    s11 = librosa.resample(seg, orig_sr=SR, target_sr=11025) * np.hamming(int(0.3 * 11025) + 1)[:len(
        librosa.resample(seg, orig_sr=SR, target_sr=11025))]
    a = librosa.lpc(s11, order=12)
    roots = [r for r in np.roots(a) if np.imag(r) > 0]
    fmts = sorted(np.angle(roots) * 11025 / (2 * np.pi))
    fmts = [f for f in fmts if f > 250][:2]
    # vibrato: cents deviation on the long notes (2nd half), around their mean
    vib = []
    for nt in ns:
        if nt["n"] > 0.5 * SR:
            a0, a1 = int((nt["t0"] + nt["n"] * 0.5) / SR * 200), int((nt["t0"] + nt["n"]) / SR * 200)
            c = 1200 * np.log2(f0[a0:a1][f0[a0:a1] > 0] / nt["f"])
            if len(c) > 10:
                vib.append(np.std(c - np.convolve(c, np.ones(25) / 25, mode="same")[:len(c)]))
    e = 10 * np.log10(np.convolve(x ** 2, np.ones(441) / 441, mode="same")[::441] + 1e-12)
    on = np.where(e > e.max() - 30)[0]
    rise = float("nan")
    if len(on):
        seg = 10 ** (e[on[0]:on[0] + 50] / 20)
        tl = np.percentile(seg, 95)
        rise = float((np.argmax(seg >= 0.9 * tl) - np.argmax(seg >= 0.1 * tl)) * 10)
    return dict(tilt_db=round(tilt, 1), breathiness=round(breath, 2),
                F1=int(fmts[0]) if fmts else None, F2=int(fmts[1]) if len(fmts) > 1 else None,
                vibrato_cents=round(float(np.mean(vib)), 0) if vib else None, attack_ms=rise)


def main():
    import singer
    os.makedirs(OUT, exist_ok=True)
    from svs import voices
    # a voice may give "audition_transpose" (the male voices sing the line an octave down: male.py measures them)
    # the voices converted from Hanami (`convert`: hanami-male, male-svc) are auditioned and measured by svc.py
    jobs = [(v["id"], v["id"], {}, int(v.get("audition_transpose", 0)), "") for v in voices()["voices"]
            if not v.get("convert")]
    jobs += [(k, v, p, tr, what) for k, (v, p, tr, what) in DEMOS.items()]
    res = {}
    import subprocess
    import soundfile as sf
    for name, vid, extra, tr, what in jobs:
        ns, n = notes(tr)
        p = dict({"source": "svs", "voice": vid, "lyrics": LINE, "seed": 1}, **extra)
        y = singer.sing(p, ns, n)
        m = measure(y, ns)
        m["what"] = what
        res[name] = m
        print(name, json.dumps(m))
        wav = f"/tmp/spectre_svs/{name}.wav"
        os.makedirs("/tmp/spectre_svs", exist_ok=True)
        sf.write(wav, y / max(np.abs(y).max(), 1e-9) * 0.89, SR)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", os.path.join(OUT, name + ".mp3")],
                       check=True)
    json.dump(res, open(os.path.join(OUT, "measurements.json"), "w"), indent=1)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    main()
