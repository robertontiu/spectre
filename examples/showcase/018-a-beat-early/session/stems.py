"""per-section stem levels (dB RMS, energy mean) from a render's meta: python3 stems.py vNNN [SEC,SEC...]"""
import json, sys, numpy as np
v = sys.argv[1]
m = json.load(open(f"renders/{v}.meta.json"))
hop = m["rms_hop"]; secs = m["sections"]
want = sys.argv[2].split(",") if len(sys.argv) > 2 else None
names = sorted(m["stems_rms"])
for s in secs:
    if want and s["name"] not in want:
        continue
    a, b = int(s["start"] / hop), int(s["end"] / hop)
    row = []
    for n in names:
        x = np.asarray(m["stems_rms"][n][a:b], float)
        if len(x) and x.max() > 0:
            db = 10 * np.log10(np.mean(x ** 2) + 1e-12)
            if db > -45:
                row.append((db, n))
    row.sort(reverse=True)
    print(f"{s['name']:6s}", " ".join(f"{n}:{d:.0f}" for d, n in row))
