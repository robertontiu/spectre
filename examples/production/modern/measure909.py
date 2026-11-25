#!/usr/bin/env python3
"""The 909 models against a recorded TR-909 (docs/MANUAL.md "909 drums"): 1/3-octave spectrum and band envelopes of
`snare909`, `clap909`, `ride909` and of the engine's earlier snare, claps and rides, against the TR-909 "Detroit" kit
of oramics/sampled (a free kit recorded through API and Neve; the collection says "public domain or similar", the
kit itself names no licence, so it is used for measurement only: downloaded to ~/.cache/spectre/refs/tr909, never
stored in the repo or used in a track; delete the folder after).

    python3 examples/production/modern/measure909.py        # prints the table, writes 909-vs-reference.png

Method: each sound and reference is aligned at its onset (first sample over 5% of the peak); spectrum = power in
1/3-octave bands (125 Hz-16 kHz) over the first 300 ms (600 ms for the ride), in dB relative to the total over those
bands; the match is the RMS difference in dB over the bands. Envelope = the time each band (4th-order band-pass, 10
ms RMS) takes to fall 20 dB under its peak; the match is the RMS of log2(model / reference) (0.1 = about 7% off).
Engine sounds are averaged over 5 random seeds (round robin). The defaults of the 909 models were fitted to these
same recordings (Nelder-Mead on the two measures; the snare's pitch fall was left free and lands on the measured
pitch track: 254 Hz averaged over the first 23 ms, 184 Hz after 20 ms), so the numbers show how close the model can
get, not an independent test: n = 1 snare, 2 claps, 1 ride, one machine.
"""
import os
import sys
import urllib.request

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import instruments as I  # noqa: E402
import synth  # noqa: E402
import tr909 as T  # noqa: E402

SR = 44100
CACHE = os.path.expanduser("~/.cache/spectre/refs/tr909")
BASE = "https://raw.githubusercontent.com/oramics/sampled/master/DM/TR-909/Detroit/samples/"
REFS = {"snare": ["snare.wav"], "clap": ["clap-1.wav", "clap-2.wav"], "ride": ["ride.wav"]}
BANDS = {"snare": [(150, 450), (450, 2000), (2000, 6000), (6000, 16000)],
         "clap": [(300, 1500), (1500, 6000), (6000, 16000)],
         "ride": [(300, 1800), (1800, 5000), (5000, 9000), (9000, 16000)]}
DUR = {"snare": 0.3, "clap": 0.3, "ride": 0.6}
MODELS = {"snare": [("snare909", T.snare909, {}), ("snare", I.snare, {}), ("kitsnare", I.DRUMS["kitsnare"], {})],
          "clap": [("clap909", T.clap909, {}), ("handclap", I.DRUMS["handclap"], {}), ("clap (old)", I.clap, {})],
          "ride": [("ride909", T.ride909, {}), ("kitride", I.DRUMS["kitride"], {}),
                   ("metalhat open", synth.metalhat, {"open": True})]}


def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        urllib.request.urlretrieve(BASE + name, path)
    return path


def onset(x):
    x = x.mean(1) if x.ndim == 2 else x
    i = int(np.argmax(np.abs(x) > np.abs(x).max() * 0.05))
    return x[max(0, i - 20):]


def third(x, dur):
    x = np.pad(x, (0, max(0, int(dur * SR) - len(x))))[:int(dur * SR)]
    X = np.abs(np.fft.rfft(x, 2 ** 17)) ** 2
    f = np.fft.rfftfreq(2 ** 17, 1 / SR)
    cs = 1000 * 2 ** (np.arange(-9, 13) / 3)
    s = np.array([X[(f >= c * 2 ** (-1 / 6)) & (f < c * 2 ** (1 / 6))].sum() for c in cs])
    return cs, 10 * np.log10(s / s.sum() + 1e-20)


def t20(x, lo, hi, ms=10):
    y = signal.sosfilt(signal.butter(4, [lo, min(hi, 21000)], btype="band", fs=SR, output="sos"), np.pad(x, (0, SR)))
    k = int(ms / 1000 * SR)
    m = len(y) // k
    e = np.sqrt((y[:m * k].reshape(m, k) ** 2).mean(1))
    e = 20 * np.log10(e / e.max() + 1e-9)
    return float(np.argmax(e < -20) * ms)


def feats(x, kind):
    cs, s = third(x, DUR[kind])
    return cs, s, np.array([t20(x, lo, hi) for lo, hi in BANDS[kind]])


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    for ax, kind in zip(axs, BANDS):
        R = [feats(onset(sf.read(fetch(f))[0]), kind) for f in REFS[kind]]
        cs, rs, rt = R[0][0], np.mean([r[1] for r in R], 0), np.mean([r[2] for r in R], 0)
        print(f"{kind}: reference t-20 per band (ms) {rt.astype(int).tolist()}  bands {BANDS[kind]}")
        ax.semilogx(cs, rs, "k", lw=2.5, label="TR-909 (recorded)")
        for name, fn, p in MODELS[kind]:
            S, E, TS = [], [], []
            for seed in range(5):
                I.RNG = np.random.default_rng(seed)
                T._RIDE_CACHE.clear()
                _, s, ts = feats(np.asarray(fn(p, 0.9, 0), dtype=np.float64), kind)
                S.append(s)
                TS.append(ts)
                E.append(np.sqrt(np.mean(np.log2(np.maximum(ts, 5) / np.maximum(rt, 5)) ** 2)))
            s = np.mean(S, 0)
            spec = np.mean([np.sqrt(np.mean((x - rs) ** 2)) for x in S])
            print(f"  {name:14s} spectrum RMS {spec:5.2f} dB   envelope log2 error {np.mean(E):.2f}   "
                  f"t-20 {np.mean(TS, 0).astype(int).tolist()}")
            ax.semilogx(cs, s, lw=1.5 if name.endswith("909") else 1, ls="-" if name.endswith("909") else "--",
                        label=f"{name} ({spec:.1f} dB)")
        ax.set_title(kind)
        ax.set_xlabel("Hz")
        ax.set_ylabel("dB (1/3 octave, of the total)")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "909-vs-reference.png"), dpi=70)


if __name__ == "__main__":
    main()
