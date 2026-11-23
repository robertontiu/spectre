#!/usr/bin/env python3
"""levels.py T0 T1 track...: render each solo (unless --nr) and print RMS and band levels over [T0,T1] seconds"""
import sys, subprocess, os, numpy as np, soundfile as sf
from scipy.signal import welch
a = sys.argv[1:]
nr = "--nr" in a; a = [x for x in a if x != "--nr"]
t0, t1, names = float(a[0]), float(a[1]), a[2:]
for s in names:
    if not nr:
        subprocess.run(["python3", "/home/claude/spectre/engine/studio.py", "render", "--solo", s], capture_output=True)
    x, sr = sf.read(f"renders/solo_{s}.wav"); x = x.mean(1) if x.ndim > 1 else x
    x = x[int(t0 * sr):int(t1 * sr)]
    f, p = welch(x, sr, nperseg=4096)
    bands = [round(10 * np.log10(p[(f >= lo) & (f < hi)].sum() + 1e-12), 1) for lo, hi in [(20, 60), (60, 250), (250, 2000), (2000, 8000), (8000, 20000)]]
    print("%-8s rms %6.1f" % (s, 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)), bands)
