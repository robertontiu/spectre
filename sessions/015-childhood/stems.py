#!/usr/bin/env python3
"""stems.py vNNN : pre-master RMS (dB) of every stem per section"""
import sys, json, numpy as np
v = sys.argv[1]
m = json.load(open(f"renders/{v}.meta.json")); hop = m["rms_hop"]
R = [(s["name"], s["start"], s["end"]) for s in m["sections"]]
print("%-7s" % "", " ".join("%6s" % n[:6] for n, _, _ in R))
for k, env in m["stems_rms"].items():
    env = np.array(env); row = []
    for n, a, b in R:
        seg = env[int(a / hop):int(b / hop)]
        r = np.sqrt((seg ** 2).mean()) if len(seg) else 0
        row.append("%6.1f" % (20 * np.log10(r + 1e-9)) if r > 1e-5 else "     .")
    print("%-7s" % k, " ".join(row))
