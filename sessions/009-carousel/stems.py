#!/usr/bin/env python3
"""stems.py vNNN section [section...]: pre-master RMS (dB) of every stem in each section, from the render meta"""
import sys, json, numpy as np
v = sys.argv[1]; secs = sys.argv[2:]
m = json.load(open(f"renders/{v}.meta.json")); hop = m["rms_hop"]
S = {s["name"]: s for s in m["sections"]}
print("%-9s" % "", " ".join("%8s" % s[:8] for s in secs))
for k, env in m["stems_rms"].items():
    env = np.array(env); row = []
    for s in secs:
        a, b = int(S[s]["start"] / hop), int(S[s]["end"] / hop)
        seg = env[a:b]
        r = np.sqrt((seg ** 2).mean()) if len(seg) else 0
        row.append("%8.1f" % (20 * np.log10(r + 1e-9)) if r > 1e-5 else "       .")
    print("%-9s" % k, " ".join(row))
