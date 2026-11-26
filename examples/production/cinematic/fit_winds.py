#!/usr/bin/env python3
"""Fit the measured wind models of engine/orchestra.py (brass and woodwinds) to recordings: writes
engine/orchestra_winds.json. References (measurement only, never stored in the repo or used in a track): the
University of Iowa MIS (2012 per-pitch sets: Horn, BbTrumpet, TenorTrombone, BassTrombone, Tuba, Flute, Oboe,
BbClarinet, Bassoon; ff) and Versilian VSCO-2-CE (CC0; Brass sustains in 2-4 velocity layers). They are downloaded to
~/.cache/spectre/refs/cinematic (examples/production/cinematic/README.md says how); delete the folder after.

    python3 examples/production/cinematic/fit_winds.py

Per recording: f0 (the candidate within -3 to +1 semitones of the file's note name whose first six harmonics carry
the most energy; f0_est), the harmonic levels in the steady part
(0.35-0.75 s, Hann window, peak within +-3% of each harmonic, up to 9 kHz), normalised to the strongest harmonic,
laid on the engine's 1/6-octave grid (63 Hz x 2^(k/6), k = 0..48; between harmonics by interpolation in log
frequency; below the fundamental -12 dB/octave; above the last harmonic -18 dB/octave). Files whose fundamental lies
more than 40 dB under their strongest harmonic are left out (VSCO's lowest horn notes). Iowa's clarinet files are
named at sounding pitch (measured: Bb3 peaks at 232 Hz). The attack: time for the fundamental's band to reach half its peak after the onset; a power law
in f0 is fitted per instrument. Dynamics: Iowa ff = 1.0; VSCO layers v1..vN = k/N (the trumpet's v1/v3 = 0.33/1.0)."""
import glob
import json
import os
import re

import numpy as np
import soundfile as sf
from scipy import signal

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
R = os.path.expanduser("~/.cache/spectre/refs/cinematic")
GRID = 63.0 * 2 ** (np.arange(49) / 6)
NOTES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
         'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
IOWA = {"Horn": "horn", "BbTrumpet": "trumpet", "TenorTrombone": "trombone", "BassTrombone": "bass_trombone",
        "Tuba": "tuba", "Flute": "flute", "Oboe": "oboe", "BbClarinet": "clarinet", "Bassoon": "bassoon"}
VSCO = {"F Horn": "horn", "Trumpet": "trumpet", "Tenor Trombone": "trombone", "Tuba": "tuba"}


def hz(n, o):
    return 440 * 2 ** ((NOTES[n] + 12 * (o + 1) - 69) / 12)


def load(f):
    x, sr = sf.read(f, always_2d=True)
    x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    # start at the note: Iowa's files open with up to seconds of room noise, and every window below is timed from 0
    i = int(np.argmax(np.abs(x) > np.abs(x).max() * 0.02))
    return x[max(0, i - int(0.01 * SR)):]


def f0_est(x, hint):
    """f0 near the file's note (a transposing instrument may sound up to 3 semitones under its written name): the
    candidate within [-3, +1] semitones of the hint whose first six harmonics carry the most energy."""
    seg = x[int(0.3 * SR):int(0.3 * SR) + 16384]
    if len(seg) < 16384:
        seg = x[:16384]
    seg = seg * np.hanning(len(seg))
    N = 1 << 17
    X = np.abs(np.fft.rfft(seg, N)) ** 2
    df = SR / N
    cands = hint * 2 ** (np.linspace(-3, 1, 161) / 12)
    # each harmonic looked for within +-0.4 % (the candidate grid steps 0.14 %: a fixed +-2-bin window missed the
    # upper harmonics of the true f0 and let a wrong candidate win, as on Iowa's clarinet Bb3 and E3)
    score = [sum(X[int(k * c * 0.996 / df):int(k * c * 1.004 / df) + 2].max() for k in range(1, 7)
                 if k * c < SR / 2) for c in cands]
    c = cands[int(np.argmax(score))]
    f = np.fft.rfftfreq(N, 1 / SR)
    m = (f > c * 0.985) & (f < c * 1.015)
    return float(f[m][np.argmax(X[m])])


def harmonics(x, f0):
    a = int(0.35 * SR)
    seg = x[a:a + int(0.4 * SR)]
    seg = seg * np.hanning(len(seg))
    N = 1 << 17
    X = np.abs(np.fft.rfft(seg, N))
    f = np.fft.rfftfreq(N, 1 / SR)
    lv = []
    k = 1
    while k * f0 <= 9000:
        m = (f > k * f0 * 0.97) & (f < k * f0 * 1.03)
        lv.append(20 * np.log10(X[m].max() + 1e-12))
        k += 1
    return np.array(lv)


def to_grid(f0, lv):
    fh = f0 * np.arange(1, len(lv) + 1)
    lv = lv - lv.max()
    lf = np.log2(GRID)
    v = np.interp(lf, np.log2(fh), lv)
    lo = GRID < fh[0]
    v[lo] = lv[0] - 12 * (np.log2(fh[0]) - lf[lo])
    hi = GRID > fh[-1]
    v[hi] = lv[-1] - 18 * (lf[hi] - np.log2(fh[-1]))
    return v


def attack_ms(x, f0):
    sos = signal.butter(4, [f0 * 0.93, f0 * 1.07], btype='band', fs=SR, output='sos')
    e = np.abs(signal.hilbert(signal.sosfilt(sos, x[:int(0.8 * SR)])))
    e = np.convolve(e, np.ones(64) / 64, 'same')
    th = int(np.argmax(np.abs(x) > np.abs(x).max() * 0.02))  # (10 ms after the trimmed file's start)
    i = int(np.argmax(e > e.max() * 0.5))
    return (i - th) / SR * 1000


def main():
    files = []
    for f in sorted(glob.glob(R + "/*/*.aif")):
        d = os.path.basename(os.path.dirname(f))
        if d not in IOWA:
            continue
        m = re.search(r'\.(pp|mf|ff)\.([A-G]b?)(\d)\.', os.path.basename(f))
        if not m:
            continue
        files.append((f, IOWA[d], {'pp': 0.2, 'mf': 0.6, 'ff': 1.0}[m.group(1)], hz(m.group(2), int(m.group(3))),
                      'vib' in f))
    for f in sorted(glob.glob(R + "/vsco/Brass/*/sus/*.wav")):
        inst = VSCO[f.split('/')[-3]]
        m = re.search(r'_sus_([A-G]#?)(-?\d)_v(\d)', os.path.basename(f))
        n, o, v = m.group(1), int(m.group(2)) + 1, int(m.group(3))
        layers = sorted({int(re.search(r'_v(\d)', g).group(1)) for g in glob.glob(
            os.path.dirname(f) + f"/*_sus_{m.group(1)}{m.group(2)}_v*")})
        dyn = (layers.index(v) + 1) / len(layers) if inst != "trumpet" else (0.33 if v == 1 else 1.0)
        files.append((f, inst, round(dyn, 2), hz(n, o), False))
    out = {}
    for f, inst, dyn, exp, vib in files:
        x = load(f)
        if len(x) < 0.8 * SR:
            continue
        f0 = f0_est(x, exp)
        lv = harmonics(x, f0)
        if len(lv) < 3 or lv.max() - lv[0] > 40:
            continue
        o = out.setdefault(inst, dict(anchors=[], attack=[]))
        o["anchors"].append(dict(f0=round(f0, 2), dyn=dyn, src=os.path.relpath(f, R), vib=vib,
                                 curve=[round(float(v), 1) for v in to_grid(f0, lv)]))
        a = attack_ms(x, f0)
        if 5 < a < 400:
            o["attack"].append((f0, a))
    res = {"_about": "Measured wind models for engine/orchestra.py, written by examples/production/cinematic/fit_winds.py "
                     "(2026-11-26): per instrument, anchors = recorded notes (f0, dynamic 0-1, harmonic levels on a "
                     "1/6-octave grid 63 Hz x 2^(k/6), dB re the strongest harmonic) and an attack law t = a (f0/220)^b "
                     "ms. Sources: University of Iowa MIS (ff) and VSCO-2-CE (CC0) brass layers; measurement only.",
           "grid_hz": [round(float(g), 2) for g in GRID]}
    for inst, o in out.items():
        fa = np.array(o["attack"])
        A = np.vstack([np.ones(len(fa)), np.log2(fa[:, 0] / 220)]).T
        c, *_ = np.linalg.lstsq(A, np.log2(fa[:, 1]), rcond=None)
        res[inst] = dict(anchors=sorted(o["anchors"], key=lambda a: (a["dyn"], a["f0"])),
                         attack_ms_220=round(float(2 ** c[0]), 1), attack_exp=round(float(c[1]), 3),
                         n=len(o["anchors"]))
        print(inst, "anchors", len(o["anchors"]), "dyn levels", sorted({a["dyn"] for a in o["anchors"]}),
              "attack", res[inst]["attack_ms_220"], res[inst]["attack_exp"])
    p = os.path.join(REPO, "engine", "orchestra_winds.json")
    with open(p + ".tmp", "w") as fh:
        json.dump(res, fh, separators=(",", ":"))
    os.replace(p + ".tmp", p)
    print("wrote", p)


if __name__ == "__main__":
    main()
