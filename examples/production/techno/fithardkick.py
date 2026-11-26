#!/usr/bin/env python3
"""The `hardkick` preset's joint fit (README.md here): its distortion chain makes a curve fitted before it non-linear,
so the curve sits after the distortion and before the final clip, and the dynamics (kicksub tail and hold, clip drive,
transient attack, click level) are refitted around it: three rounds of three curve iterations (0.6 of the way to the
15 references' median third-octave spectrum, limited to +/-9 dB) and a 50-step Nelder-Mead on crest, loudness density
and band decay times. Prints the parameters and the curve, which go into fitpresets.py BASE and
engine/techno_presets.json. The patch's starting point came from the same search without a curve (tune held at 55 Hz).

    bash tools/remix/waitfree.sh render && python3 examples/production/techno/fithardkick.py      # ~15 minutes
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitpresets as FP  # noqa: E402
import common as C  # noqa: E402
import describe as DS  # noqa: E402
spec = FP.BASE["hardkick"]; THIRD = DS.THIRD
D = FP.ref_d("hardkick", False)
med = lambda f: float(np.median([f(r) for r in D]))
tg = dict(crest=med(lambda r: r["crest_db"]), dens=med(lambda r: r["lufs_m_max"]), dl=med(lambda r: r["decay20_ms"]["low"]), dm=med(lambda r: r["decay20_ms"]["mid"]), dh=med(lambda r: r["decay20_ms"]["high"]))
refT = np.median(np.array([d["third_db"] for d in D]), 0)
def run(x, pts):
    tail, hold, clipd, att, cg = x
    tr = FP.build(spec, {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})
    L = tr["layers"]; L[0]["inst"].update(tail=tail, hold=hold); L[2]["gain_db"] = -cg
    tr["fx"][2]["attack_db"] = att; tr["fx"][4]["drive_db"] = clipd
    xx = FP.render(tr, spec["note"], 1); return tr, DS.describe(xx, 150, False)
x = np.array([0.033, 0.035, 6.0, 4.0, 3.9])  # tail, hold, clip drive_db, transient attack_db, click -gain_db; pts = np.zeros(len(THIRD))
for outer in range(3):
    # curve iterations at fixed x
    for it in range(3):
        tr, d = run(x, pts); et = np.array(d["third_db"]); dev = refT - et; ok = refT > refT.max() - 45
        sm = np.convolve(np.pad(dev, 2, mode="edge"), np.array([1, 2, 3, 2, 1]) / 9, mode="valid")
        print("spec", round(float(np.sqrt(np.mean(dev[ok] ** 2))), 2), flush=True)
        pts = pts + 0.6 * np.where(ok, sm, 0); w = 10 ** (et / 10) * ok; pts = np.clip(pts - np.sum(w * pts) / np.sum(w), -9, 9)
    def cost(z):
        _, d = run(z, pts)
        return abs(d["crest_db"] - tg["crest"]) + abs(d["lufs_m_max"] - tg["dens"]) + 4 * sum(abs(np.log2(max(d["decay20_ms"][b], 3) / tg[k])) for b, k in (("low", "dl"), ("mid", "dm"), ("high", "dh")))
    x, f = C.minimize_log(cost, x, maxiter=50, restarts=1, step=0.3, verbose="dyn")
    print("x", np.round(x, 4).tolist(), f, flush=True)
tr, d = run(x, pts)
dev = refT - np.array(d["third_db"]); ok = refT > refT.max() - 45
print("FINAL", np.round(x, 4).tolist(), "spec", round(float(np.sqrt(np.mean(dev[ok] ** 2))), 2), d["crest_db"], d["lufs_m_max"], d["decay20_ms"], d["groups_db"])
print("PTS", {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})
