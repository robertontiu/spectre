#!/usr/bin/env python3
"""hf.py track... : 6-12 kHz energy (dB) of each solo render per section (needs renders/solo_<t>.wav)"""
import sys, json, numpy as np, soundfile as sf
from scipy import signal
m = json.load(open(sorted(__import__('glob').glob('renders/v*.meta.json'))[-1]))
secs = ["verse1a", "pre1", "chorus1", "tag", "verse2a", "bridgeA", "bridgeB"]
S = {s["name"]: s for s in m["sections"]}
print("%-8s" % "", " ".join("%8s" % s[:8] for s in secs))
sos = signal.butter(4, [6000, 12000], "bandpass", fs=44100, output="sos")
for t in sys.argv[1:]:
    x, sr = sf.read(f"renders/solo_{t}.wav"); x = x.mean(1) if x.ndim > 1 else x
    y = signal.sosfilt(sos, x)
    row = []
    for s in secs:
        seg = y[int(S[s]["start"]*sr):int(S[s]["end"]*sr)]
        r = np.sqrt((seg**2).mean()); row.append("%8.1f" % (20*np.log10(r+1e-9)))
    print("%-8s" % t, " ".join(row))
