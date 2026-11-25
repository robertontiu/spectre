#!/usr/bin/env python3
"""spec.py <wav> [start end]: octave-third band levels (dB, relative to the 1 kHz band) of a render or premaster"""
import sys, numpy as np, soundfile as sf
y, sr = sf.read(sys.argv[1]); y = y.mean(axis=1) if y.ndim > 1 else y
if len(sys.argv) > 3: y = y[int(float(sys.argv[2]) * sr):int(float(sys.argv[3]) * sr)]
n = 1 << 15; hop = n // 2; w = np.hanning(n); P = np.zeros(n // 2 + 1)
for i in range(0, len(y) - n, hop): P += np.abs(np.fft.rfft(y[i:i + n] * w)) ** 2
f = np.fft.rfftfreq(n, 1 / sr); cs = [31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]
L = {c: 10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-12) for c in cs}
print(" ".join(f"{c:g}:{L[c] - L[1000]:+.0f}" for c in cs))
