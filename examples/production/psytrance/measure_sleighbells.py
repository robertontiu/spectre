"""Sleigh bells: the engine's `sleighbells` (engine/psy.py) against VSCO-2 CE's sleigh bells (CC0; measured only).

The 13 reference samples (two straps, single hits and shakes) are fetched by URL into
~/.cache/spectre/refs/psytrance/sleighbells/ (never into the repo; VSCO-2-CE commit 4403009). Per file, from its
peak: 1/3-octave power over 300 ms relative to the total (500 Hz-16 kHz), the time to fall 20 dB (5 ms RMS), the
number of strikes (peaks of the >4 kHz envelope within 30 dB of the maximum) and the spectral centroid. Then the same
for the engine at its defaults (8 seeds). Prints both and their difference; writes sleighbells.json beside this file.

    python3 examples/production/psytrance/measure_sleighbells.py
"""
import json
import os
import sys
import urllib.request

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "engine"))
import instruments as I  # noqa: E402
import psy  # noqa: E402

SR = 44100
REFS = os.path.expanduser("~/.cache/spectre/refs/psytrance/sleighbells")
BASE = "https://raw.githubusercontent.com/sgossner/VSCO-2-CE/440300901dfe9275fd84e0b7763af1f8443ae62e/"
FILES = ["Percussion/Sleighbells_Hit_v1_rr1_Mid.wav", "Percussion/Sleighbells_Hit_v1_rr2_Mid.wav"] + [
    f"Miscellania Raw/Misc 2/{n}.wav" for n in (
        "sleighbell1_hit_1", "sleighbell1_hit_2", "sleighbell1_hit_3", "sleighbell1_hit_loud_1", "sleighbell1_hit_loud_2",
        "sleighbell1_hit_quiet", "sleighbell1_shake1", "sleighbell2_hit_1", "sleighbell2_hit_2", "sleighbell2_hit_loud",
        "sleighbell2_shake1")]
BANDS = [1000, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]


def fetch():
    os.makedirs(REFS, exist_ok=True)
    out = []
    for f in FILES:
        dst = os.path.join(REFS, os.path.basename(f))
        if not os.path.exists(dst):
            urllib.request.urlretrieve(BASE + f.replace(" ", "%20"), dst)
        out.append(dst)
    return out


def measure(x, sr=SR):
    x = x.mean(1) if x.ndim > 1 else x
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    pk = int(np.argmax(np.abs(x)))
    seg = x[max(0, pk - int(0.01 * SR)):pk + int(0.3 * SR)]
    f, P = signal.welch(seg, SR, nperseg=4096)
    tot = P.sum()
    bands = [10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() / tot + 1e-20) for c in BANDS]
    w = int(0.005 * SR)
    e = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "same")) + 1e-12)
    p = int(np.argmax(e))
    below = np.where(e[p:] < e[p] - 20)[0]
    t20 = below[0] / SR if len(below) else float("nan")
    hp = signal.sosfilt(signal.butter(4, 4000, "high", fs=SR, output="sos"), x)
    e2 = np.convolve(np.abs(signal.hilbert(hp)), np.ones(44) / 44, "same")
    pks, _ = signal.find_peaks(20 * np.log10(e2 + 1e-9), prominence=6, distance=int(0.004 * SR))
    pks = pks[(pks > p - int(0.02 * SR)) & (e2[pks] > e2.max() * 10 ** (-30 / 20))]
    f2, P2 = signal.welch(x[p:p + int(0.3 * SR)], SR, nperseg=4096)
    return dict(bands=bands, t20=t20, strikes=int(len(pks)), centroid=float((f2 * P2).sum() / P2.sum()))


def summary(ms):
    return dict(bands=[round(float(np.median([m["bands"][i] for m in ms])), 1) for i in range(len(BANDS))],
                t20=round(float(np.nanmedian([m["t20"] for m in ms])), 3),
                strikes=float(np.median([m["strikes"] for m in ms])),
                centroid=round(float(np.median([m["centroid"] for m in ms])), 0))


def main():
    ref = summary([measure(*sf.read(f)) for f in fetch() if "shake" not in f])  # single hits (the shakes are long)
    eng = []
    for s in range(8):
        I.RNG = np.random.default_rng(100 + s)
        eng.append(measure(psy.sleighbells({}, 0.9).astype(float)))
    eng = summary(eng)
    print("band Hz   ", " ".join(f"{b:>6}" for b in BANDS))
    print("reference ", " ".join(f"{v:6.1f}" for v in ref["bands"]), ref["t20"], ref["strikes"], ref["centroid"])
    print("engine    ", " ".join(f"{v:6.1f}" for v in eng["bands"]), eng["t20"], eng["strikes"], eng["centroid"])
    d = [e - r for e, r in zip(eng["bands"], ref["bands"])]
    print("difference", " ".join(f"{v:6.1f}" for v in d), " mean |d| 2-12.5 kHz:",
          round(float(np.mean(np.abs(d[1:10]))), 2))
    with open(os.path.join(HERE, "sleighbells.json"), "w") as fh:
        json.dump(dict(bands_hz=BANDS, reference_hits_median=ref, engine_defaults_median=eng,
                       difference_db=[round(v, 1) for v in d],
                       note="1/3-octave power over 300 ms from the peak, dB re the total; t20 s; strikes = >4 kHz "
                            "envelope peaks within 30 dB; references: VSCO-2 CE sleigh bells, 11 single hits (CC0)"),
                  fh, indent=1)


if __name__ == "__main__":
    main()
