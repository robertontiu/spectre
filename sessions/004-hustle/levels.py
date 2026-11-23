import json, sys, numpy as np, glob
f = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("renders/v*.meta.json"))[-1]
m = json.load(open(f)); print(f)
for k, v in m["stems_rms"].items():
    a = np.array(v); a = a[a > 1e-5]
    if len(a): print(f"{k:8s} mean {20*np.log10(np.sqrt((a**2).mean())):6.1f} dB   peak-env {20*np.log10(a.max()):6.1f}")
