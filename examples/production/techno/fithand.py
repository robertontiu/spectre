#!/usr/bin/env python3
"""Fit the hand drums of engine/techno.py (`conga`, `bongo`, open stroke) to recorded congas and bongos (Freesound
previews, engine/third_party.json `refs-techno-*` roles conga and bongo; measured only), and compare them with the
engine's earlier stand-ins (`darbuka`, `tom`, `kittom`).

    python3 examples/production/techno/fithand.py fit [conga|bongo]   # prints the fitted defaults
    python3 examples/production/techno/fithand.py check               # the table in README.md, hand-numbers.json

Features as fit909.py (third-octave spectra in three windows, band decay times); the score is the median over the
recordings of each one's distance (the recordings mix strokes and drums: the median keeps the typical one)."""
import json
import os
import sys

import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import techno as T  # noqa: E402

WINS = [(0, .02), (.02, .1), (.1, .4)]
BANDS = [(100, 400), (400, 1500), (1500, 8000)]
FREE = ["tune", "decay", "modes", "bright", "bend", "bend_ms", "slap", "slap_hz", "drive"]
DEF = {"conga": T.CONGA, "bongo": T.BONGO}
OLD = {"conga": [("darbuka doum", "darbuka", {"stroke": "doum", "tune": 2.0}), ("tom", "tom", {}),
                 ("kittom", "kittom", {})],
       "bongo": [("darbuka tek", "darbuka", {"stroke": "tek"}), ("darbuka slap", "darbuka", {"stroke": "slap"}),
                 ("tom", "tom", {})]}


def R(kind):
    return [C.feats(C.load(f), WINS, BANDS) for f in C.refs(kind)]


def score(kind, q, RR, seeds=(0,)):
    out = []
    for s in seeds:
        F = C.feats(C.hit(kind, q, seed=s), WINS, BANDS)
        out.append(np.median([C.dist(F, r) for r in RR], 0))
    return np.mean(out, 0)


def fit(kind):
    RR = R(kind)
    q0 = {k: v for k, v in DEF[kind].items() if k != "stroke"}
    x0 = np.array([float(q0[k]) for k in FREE])

    def f(x):
        return score(kind, dict(q0, **{k: float(v) for k, v in zip(FREE, x)}), RR)[2]
    xb, fb = C.minimize_log(f, x0, maxiter=600, restarts=3, verbose=kind)
    q = dict(q0, **{k: round(float(v), 4) for k, v in zip(FREE, xb)})
    print(kind, round(fb, 3), json.dumps(q), flush=True)


def check():
    out = {}
    for kind in DEF:
        RR = R(kind)
        rows = {}
        for label, typ, p in [("NEW " + kind, kind, {})] + OLD[kind]:
            d = np.mean([np.median([C.dist(C.feats(C.hit(typ, p, seed=s), WINS, BANDS), r) for r in RR], 0)
                         for s in range(5)], 0)
            rows[label] = dict(spec_db=round(float(d[0]), 2), env_log2=round(float(d[1]), 3), n=len(RR))
            print(f"{kind:6s} {label:16s} n={len(RR)}: spectrum {d[0]:5.2f} dB, decay {d[1]:.2f}", flush=True)
        out[kind] = rows
    json.dump(out, open(os.path.join(C.HERE, "hand-numbers.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1:2] == ["fit"]:
        for k in (sys.argv[2:] or list(DEF)):
            fit(k)
    else:
        check()
