"""Fit the double bass's body (engine/chamber.py BASS_BODY) the way the cello's and viola's were fitted: each Iowa MIS
double-bass note (arco ff, non-vibrato; E1-D3, 13 recordings) has its harmonic levels divided by those of the bare
bowed waveguide (engine/violin.py through chamber.string_line) at the same pitch; each note is normalised to its
total, all notes pooled on the 1/6-octave grid (63 Hz x 2^(k/6), k = 0..48), smoothed, 0 dB at 1 kHz, held above
8 kHz. Then `passes` closed-loop refinements: render the model with the table, measure the same way, fold the residual
back in. Prints the table and the mean distance per pass.

    python3 examples/production/cinematic/fit_bass.py <folder with Bass.arco.ff.*.aif> [passes]
"""
import glob
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "engine"))
import chamber as C  # noqa: E402

SR = 44100
GRID = 63.0 * 2 ** (np.arange(49) / 6)
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(name):
    m = re.match(r"([A-G])(b|#)?(\d)", name)
    k = NAMES[m.group(1)] + {"b": -1, "#": 1, None: 0}[m.group(2)] + 12 * (int(m.group(3)) + 1)
    return 440.0 * 2 ** ((k - 69) / 12)


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    e = np.convolve(x ** 2, np.ones(441) / 441, "same")
    i = int(np.argmax(e > e.max() * 1e-3))
    return x[i:]


def harmonics(x, f0, t0=0.4, t1=1.4):
    seg = x[int(t0 * SR):int(t1 * SR)]
    seg = seg * np.hanning(len(seg))
    N = 1 << 18
    S = np.abs(np.fft.rfft(seg, N)) ** 2
    fr = np.fft.rfftfreq(N, 1 / SR)
    hs, lv = [], []
    k = 1
    while f0 * k < 8500:
        f = f0 * k
        m = (fr > f * 2 ** (-0.4 / 12)) & (fr < f * 2 ** (0.4 / 12))
        if m.any():
            hs.append(f)
            lv.append(10 * np.log10(S[m].max() + 1e-30))
        k += 1
    lv = np.array(lv)
    lv -= 10 * np.log10((10 ** (lv / 10)).sum())
    return np.array(hs), lv


def model(f0, table):
    old = C.STRING_KIND.get("bass")
    C.STRING_KIND["bass"] = dict(C.STRING_KIND["cello"], table=list(table), lo=40.0, hpf=30.0, lpf=9000.0)
    C._BODIES.pop(("bass", 0), None)
    nt = [dict(t0=0, n=int(1.8 * SR), f=f0, vel=0.9, glide=False, art=[])]
    y = C.string_body("bass", {}, C.string_line("bass", dict(vibrato=0.0, seed=7), nt, int(2.2 * SR)))
    if old is not None:
        C.STRING_KIND["bass"] = old
    return np.asarray(y, dtype=np.float64)


def pool(points):
    """points: list of (freq, dB) -> 1/6-octave grid, median per bin, holes interpolated, 0 dB at 1 kHz."""
    f = np.concatenate([p[0] for p in points])
    v = np.concatenate([p[1] for p in points])
    lg = np.log2(GRID)
    out = np.full(len(GRID), np.nan)
    for i, g in enumerate(lg):
        m = np.abs(np.log2(f) - g) < 1 / 12
        if m.sum() >= 2:
            out[i] = np.median(v[m])
    ok = ~np.isnan(out)
    out = np.interp(lg, lg[ok], out[ok])
    sm = np.convolve(np.pad(out, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")
    k8 = int(np.argmin(abs(GRID - 8000)))
    sm[k8:] = sm[k8]
    return sm - np.interp(np.log2(1000), lg, sm)


def main(folder, passes=2):
    refs = []
    for p in sorted(glob.glob(os.path.join(folder, "Bass.arco.ff.*.aif"))):
        f0 = hz(os.path.basename(p).split(".")[4])
        refs.append((f0, harmonics(load(p), f0)))
    flat = np.zeros(len(GRID))
    pts = []
    for f0, (h, lv) in refs:
        hm, lm = harmonics(model(f0, flat), f0)
        n = min(len(lv), len(lm))
        d = lv[:n] - lm[:n]
        pts.append((h[:n], d - np.mean(d)))
    table = pool(pts)
    for it in range(passes + 1):
        res = []
        for f0, (h, lv) in refs:
            hm, lm = harmonics(model(f0, table), f0)
            n = min(len(lv), len(lm))
            d = lv[:n] - lm[:n]
            res.append((h[:n], d - np.mean(d)))
        dist = np.mean([np.mean(np.abs(r[1][(r[0] > 100) & (r[0] < 8000)])) for r in res])
        sm = pool(res)
        band = (GRID > 100) & (GRID < 8000)
        print(f"pass {it}: mean distance {dist:.2f} dB per harmonic, {np.mean(np.abs(sm[band] - sm[band].mean())):.2f} dB "
              "1/6-octave smoothed, 100 Hz-8 kHz")
        if it < passes:
            table = table + 0.7 * pool(res)
            table -= np.interp(np.log2(1000), np.log2(GRID), table)
    print("BASS_BODY =", [round(float(v), 1) for v in table])


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2)
