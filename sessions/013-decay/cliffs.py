#!/usr/bin/env python3
"""cliffs.py master.mp3: level and spectrum around each drop (K-weighted short-term loudness, bands)"""
import sys, subprocess, numpy as np, pyloudnorm as pyln
from scipy import signal
SR = 44100; BAR = 240 / 140
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", sys.argv[1], "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
M = pyln.Meter(SR, block_size=0.4)
def lufs(t0, t1):
    seg = x[int(t0 * SR):int(t1 * SR)]
    try: return M.integrated_loudness(seg.astype(np.float64))
    except Exception: return float("nan")
def bands(t0, t1):
    seg = x[int(t0 * SR):int(t1 * SR)].mean(1)
    f, p = signal.welch(seg, SR, nperseg=8192)
    out = []
    for lo, hi in [(20, 120), (120, 2000), (2000, 8000), (8000, 16000)]:
        out.append(10 * np.log10(p[(f >= lo) & (f < hi)].sum() + 1e-15))
    return out
for name, build0, drop in [("drop 1", 25, 33), ("main drop", 65, 73)]:
    td = (drop - 1) * BAR
    print(name, "at %.1f s" % td)
    for lab, a, b in [("build first 2 bars", (build0 - 1) * BAR, (build0 + 1) * BAR), ("build bars 5-6", (build0 + 3) * BAR, (build0 + 5) * BAR),
                      ("last 2 bars before", td - 2 * BAR, td), ("last bar before", td - BAR, td), ("last beat before", td - BAR / 4, td),
                      ("first bar after", td, td + BAR), ("first 2 bars after", td, td + 2 * BAR)]:
        bl = bands(a, b)
        print("  %-20s %6.1f LUFS   low %5.1f  mid %5.1f  high %5.1f  air %5.1f" % (lab, lufs(a, b), *bl))
    print("  cliff (first bar after - last bar before): %.1f LU; low band %.1f dB" % (lufs(td, td + BAR) - lufs(td - BAR, td), bands(td, td + BAR)[0] - bands(td - BAR, td)[0]))
