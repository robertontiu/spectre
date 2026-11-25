#!/usr/bin/env python3
"""hiss.py <wav>: 6-12 kHz level in 0.4 s windows; prints the loudest ones (sibilants, breaths) and the median"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
y, sr = sf.read(sys.argv[1]); y = y.mean(axis=1) if y.ndim > 1 else y
hi = sosfilt(butter(4, [6000, 12000], btype='band', fs=sr, output='sos'), y)
w = int(0.4 * sr); L = [10 * np.log10(np.mean(hi[i:i + w] ** 2) + 1e-12) for i in range(0, len(hi) - w, w)]
L = np.array(L); print("median %.1f dB" % np.median(L[L > -80]))
for i in np.argsort(L)[::-1][:8]:
    print("  %6.1f s  %.1f dB" % (i * 0.4, L[i]))
