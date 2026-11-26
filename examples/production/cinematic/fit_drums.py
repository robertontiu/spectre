"""Fit the orchestral percussion of engine/orchestra.py to recordings (VSCO-2-CE, CC0): the timpani's mode ratios,
levels and decays, the concert bass drum's, and the suspended cymbal's spectral tilt and decay.

    python3 examples/production/cinematic/fit_drums.py <VSCO-2-CE checkout>            # modes
    python3 examples/production/cinematic/fit_drums.py <VSCO-2-CE checkout> residual   # the band layer above them
    python3 examples/production/cinematic/fit_drums.py <VSCO-2-CE checkout> cymbal     # the cymbal's envelopes

Prints the fitted values (they are written by hand into TIMP, BASSDRUM and SUSCYM in engine/orchestra.py, with this
script named as their source). Method: the strongest spectral peak under 200 Hz in the first 300 ms is the principal
mode; every peak within 30 dB of it up to 3.2 x its frequency is a mode, its level read at 30 ms and its T60 from a
line fitted to its band's energy (+-3 % around the peak) from -5 to -35 dB.
"""
import glob
import os
import sys

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100


def load(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float64)
    if x.ndim == 2:
        x = x.mean(1)
    x /= np.abs(x).max() + 1e-12
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    i = int(np.argmax(np.abs(x) > 0.05))
    return x[max(0, i - 64):]


def band_t60(x, f, rel=0.03):
    lo, hi = f * (1 - rel), f * (1 + rel)
    y = signal.sosfiltfilt(signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
    e = signal.convolve(y ** 2, np.ones(441) / 441, "same")
    edb = 10 * np.log10(e + 1e-20)
    pk = int(np.argmax(edb[:SR // 2]))
    d = edb[pk:] - edb[pk]
    i1 = np.argmax(d < -5)
    i2 = np.argmax(d < -35)
    if i2 <= i1 + 10:
        i2 = len(d) - 1
    t = np.arange(i1, i2) / SR
    slope = np.polyfit(t, d[i1:i2], 1)[0]
    return float(-60 / slope) if slope < 0 else float("nan"), float(edb[pk])


def modes(x, fmax_ratio=3.2):
    seg = x[int(0.03 * SR):int(0.33 * SR)] * np.hanning(int(0.3 * SR))
    N = 1 << 17
    S = np.abs(np.fft.rfft(seg, N))
    fr = np.fft.rfftfreq(N, 1 / SR)
    sdb = 20 * np.log10(S / S.max() + 1e-12)
    low = (fr > 30) & (fr < 200)
    f1 = fr[low][np.argmax(sdb[low])]
    pk, _ = signal.find_peaks(sdb, prominence=6, distance=int(8 / (fr[1] - fr[0])))
    out = []
    for i in pk:
        if f1 * 0.95 <= fr[i] <= f1 * fmax_ratio and sdb[i] > sdb[np.argmin(abs(fr - f1))] - 30:
            out.append((fr[i] / f1, sdb[i]))
    l1 = sdb[np.argmin(abs(fr - f1))]
    return f1, [(r, lv - l1) for r, lv in out]


def main(root):
    print("== timpani hits")
    rows = []
    for p in sorted(glob.glob(os.path.join(root, "Percussion/Timpani/Timpani*_Hit_*.wav"))):
        x = load(p)
        f1, ms = modes(x)
        t1 = band_t60(x, f1)[0]
        row = [(round(r, 3), round(lv, 1), round(band_t60(x, f1 * r)[0], 2)) for r, lv in ms]
        print(os.path.basename(p), f"f1 {f1:.1f} Hz T60 {t1:.2f}s", row)
        rows.append((f1, t1, row))
    # pool: for each target ratio of the air-loaded membrane, the nearest measured mode (within 4 %)
    target = [1.0, 1.504, 1.742, 2.0, 2.245, 2.494, 2.8]
    print("pooled (ratio, level dB, T60 s) per target ratio:")
    for tr in target:
        hits = [(r, lv, t) for _, _, row in rows for r, lv, t in row if abs(r / tr - 1) < 0.04]
        if hits:
            a = np.array(hits)
            print(f"  {tr}: n={len(a)} ratio {np.median(a[:, 0]):.3f} level {np.median(a[:, 1]):.1f} "
                  f"T60 {np.nanmedian(a[:, 2]):.2f}")
        else:
            print(f"  {tr}: not found")
    print("== concert bass drum")
    for p in sorted(glob.glob(os.path.join(root, "Percussion/BDrumNewhit_*.wav"))):
        x = load(p)
        f1, ms = modes(x, 3.4)
        print(os.path.basename(p), f"f1 {f1:.1f} Hz T60 {band_t60(x, f1, 0.06)[0]:.2f}s",
              [(round(r, 2), round(lv, 1), round(band_t60(x, f1 * r, 0.05)[0], 2)) for r, lv in ms[:10]])
    print("== suspended cymbal")
    for p in sorted(glob.glob(os.path.join(root, "VSCO 1 Percussion/varMetal/Cymbals/susp/susp_hit_*.wav"))):
        x = load(p)
        f, P = signal.welch(x[:int(1.5 * SR)], SR, nperseg=8192)
        oc = 250 * 2 ** np.arange(0, 6.5, 0.5)
        lv = [10 * np.log10(P[(f > c / 2 ** 0.25) & (f < c * 2 ** 0.25)].mean() + 1e-20) for c in oc]
        lv = np.array(lv) - max(lv)
        sl = np.polyfit(np.log2(oc[oc >= 1000] / 1000), lv[oc >= 1000], 1)[0]
        bt = [band_t60(x, c, 0.2)[0] for c in (1000, 4000, 8000)]
        e = signal.convolve(x ** 2, np.ones(4410) / 4410, "same")
        print(os.path.basename(p), "half-octave levels from 250 Hz", np.round(lv, 1).tolist(),
              f"slope above 1k {sl:.1f} dB/oct", "T60 1k/4k/8k", np.round(bt, 2).tolist(),
              f"peak at {np.argmax(e) / SR:.2f}s of {len(x) / SR:.1f}s")


def band_levels(x, centers, t1=1.0):
    """Energy in third-octave bands at `centers` over the first t1 s, dB re their sum."""
    seg = np.asarray(x, dtype=np.float64)[:int(t1 * SR)]
    f, P = signal.welch(seg, SR, nperseg=8192)
    lv = np.array([P[(f >= c * 2 ** (-1 / 6)) & (f < c * 2 ** (1 / 6))].sum() for c in centers])
    lv = 10 * np.log10(lv + 1e-30)
    return lv - 10 * np.log10((10 ** (lv / 10)).sum())


def schroeder_t60(x, c):
    y = signal.sosfilt(signal.butter(2, [c * 2 ** (-1 / 6), min(c * 2 ** (1 / 6), SR * 0.45)], btype="band", fs=SR,
                                     output="sos"), x)
    E = np.cumsum((y ** 2)[::-1])[::-1]
    L = 10 * np.log10(E / E[0] + 1e-30)
    i1, i2 = int(np.argmax(L < -5)), int(np.argmax(L < -25))
    if i2 <= i1 + 10:
        return float("nan")
    return float(-60 / np.polyfit(np.arange(i1, i2) / SR, L[i1:i2], 1)[0])


def residual(root, passes=5):
    """Closed-loop fit of orchestra.TIMP_RES and BD_RES: third-octave bands from 0.5x to 64x the principal (timpani)
    or 40 Hz-16 kHz (bass drum); T60 per band from the recordings (Schroeder, T20 x 3), levels moved by the
    difference between the recordings' median band levels and the model's, `passes` times."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
    import orchestra as O
    hits = []
    for p in sorted(glob.glob(os.path.join(root, "Percussion/Timpani/Timpani*_Hit_v3_rr1_Sum.wav"))):
        x = load(p)
        hits.append((modes(x)[0], x))
    ratios = [2 ** (k / 3) for k in range(-3, 19)]
    tgt = np.median([band_levels(x, [f1 * r for r in ratios]) for f1, x in hits], axis=0)
    t60 = [float(np.nanmedian([schroeder_t60(x, f1 * r) for f1, x in hits if f1 * r * 1.12 < SR * 0.45]))
           for r in ratios]
    O.TIMP_RES.update(ratios=ratios, levels=[-40.0] * len(ratios), t60=[min(max(v, 0.05), 6.0) for v in t60])
    for it in range(passes + 1):
        mod = np.median([band_levels(O.timpani({}, f1, 0.9, 0.5), [f1 * r for r in ratios]) for f1, _ in hits], axis=0)
        err = tgt - mod
        m = tgt > tgt.max() - 40
        print(f"timpani pass {it}: mean |error| {np.mean(np.abs(err[m])):.2f} dB over the bands within 40 dB")
        if it < passes:
            O.TIMP_RES["levels"] = list(np.clip(np.array(O.TIMP_RES["levels"]) + err, -120, 20))
    print("TIMP_RES = dict(ratios=", [round(r, 3) for r in ratios], ", levels=",
          [round(float(v), 1) for v in O.TIMP_RES["levels"]], ", t60=", [round(v, 2) for v in O.TIMP_RES["t60"]], ")")
    bds = [load(p) for p in sorted(glob.glob(os.path.join(root, "Percussion/BDrumNewhit_v[357]_rr1_Sum.wav")))]
    hz = [40 * 2 ** (k / 3) for k in range(0, 27)]
    tgt = np.median([band_levels(x, hz) for x in bds], axis=0)
    t60 = [float(np.nanmedian([schroeder_t60(x, c) for x in bds])) for c in hz]
    O.BD_RES.update(hz=hz, levels=[-40.0] * len(hz), t60=[min(max(v, 0.05), 6.0) for v in t60])
    for it in range(passes + 1):
        mod = band_levels(O.bassdrum({}, 0.9), hz)
        err = tgt - mod
        m = tgt > tgt.max() - 40
        print(f"bass drum pass {it}: mean |error| {np.mean(np.abs(err[m])):.2f} dB over the bands within 40 dB")
        if it < passes:
            O.BD_RES["levels"] = list(np.clip(np.array(O.BD_RES["levels"]) + err, -120, 20))
    print("BD_RES = dict(hz=", [round(c, 1) for c in hz], ", levels=", [round(float(v), 1) for v in O.BD_RES["levels"]],
          ", t60=", [round(v, 2) for v in O.BD_RES["t60"]], ")")


def cymbal(root, passes=8):
    """Closed-loop fit of orchestra.SUSCYM_ENV: third-octave levels (250 Hz-16 kHz) of the hard-mallet hit over its
    first 1.5 s and of the soft-mallet crescendo roll up to its peak, model against recording."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "engine"))
    import orchestra as O
    d = os.path.join(root, "VSCO 1 Percussion/varMetal/Cymbals/susp")
    hit = load(os.path.join(d, "susp_hit_hardmall_f.wav"))
    roll = load(os.path.join(d, "susp_hit_softmall_roll2_cresc.wav"))
    pk = int(np.argmax(np.convolve(roll ** 2, np.ones(4410), "same"))) / SR
    B = O.SUSCYM_BANDS
    for mode, ref, t1, render in (("hit", hit, 1.5, lambda: O.suscymbal({"mode": "hit"}, 0, 0.9, 0.1)),
                                  ("swell", roll, pk, lambda: O.suscymbal({}, 0, 0.9, pk))):
        tgt = band_levels(ref, B, t1)
        O.SUSCYM_ENV[mode] = [0.0] * len(B)
        for it in range(passes + 1):
            O._CYM.clear()
            mod = np.mean([band_levels(np.asarray(render(), dtype=np.float64), B, t1) for _ in range(4)], axis=0)
            err = tgt - mod
            print(f"cymbal {mode} pass {it}: mean |error| {np.mean(np.abs(err)):.2f} dB (4 strokes averaged)")
            if it < passes:  # damped: each stroke's noise differs
                O.SUSCYM_ENV[mode] = list(np.array(O.SUSCYM_ENV[mode]) + 0.6 * err)
        print(f'"{mode}":', [round(float(v), 1) for v in O.SUSCYM_ENV[mode]])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "residual":
        residual(sys.argv[1])
    elif len(sys.argv) > 2 and sys.argv[2] == "cymbal":
        cymbal(sys.argv[1])
    else:
        main(sys.argv[1])
