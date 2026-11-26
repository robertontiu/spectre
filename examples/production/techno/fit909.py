#!/usr/bin/env python3
"""Fit the TR-909 models of engine/techno.py (`kick909`, `hat909`, `openhat909`, `tom909`, `rim909`) to a recorded TR-909
(engine/third_party.json `refs-tr909-detroit`: the "TR-909 Detroit" kit of oramics/sampled, recorded through API and
Neve; measured only), as examples/production/modern/measure909.py did for the snare, clap and ride; then check them,
and the engine's earlier stand-ins, against the other 909 recordings (Freesound previews, `refs-techno-*` roles kick909,
hat909, openhat909, tom909, rim909): those are not fitted to, so they are an independent test.

    python3 examples/production/techno/fit909.py fit [kind ...]   # Nelder-Mead; prints the fitted defaults
    python3 examples/production/techno/fit909.py check            # the table in README.md, 909-numbers.json, 909.png

Features: third-octave spectra (25 Hz-16 kHz) in time windows after the onset (the kick's in four windows, so its pitch
fall counts), each relative to the whole sound's power; and the time each band takes to fall 20 dB (5 ms RMS).
Distance = spectral RMS dB difference (bands within 40 dB of the reference's loudest) + 4 x RMS log2 error of the decay
times. Engine sounds are averaged over 5 random seeds (the noise in them)."""
import json
import os
import sys

import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import techno as T  # noqa: E402
import synth  # noqa: E402

WINS = {"kick": [(0, .01), (.01, .04), (.04, .15), (.15, .45)], "hat": [(0, .03), (.03, .2)],
        "ohat": [(0, .05), (.05, .25), (.25, .6)], "tom": [(0, .03), (.03, .15), (.15, .45)], "rim": [(0, .02), (.02, .1)]}
BANDS = {"kick": [(30, 80), (80, 200), (200, 1000), (1000, 8000)], "hat": [(3000, 6000), (6000, 10000), (10000, 16000)],
         "ohat": [(3000, 6000), (6000, 10000), (10000, 16000)], "tom": [(50, 200), (200, 1000), (1000, 8000)],
         "rim": [(150, 600), (600, 2000), (2000, 8000)]}
DET = {"kick": ["kick.wav"], "hat": ["hihat-closed.wav", "hihat-close.wav"], "ohat": ["hihat-open-1.wav", "hihat-open-2.wav"],
       "tom": ["tom-l.wav", "tom-h.wav"], "rim": ["rim.wav"]}
FS_ROLE = {"kick": "kick909", "hat": "hat909", "ohat": "openhat909", "tom": "tom909", "rim": "rim909"}
MODEL = {"kick": "kick909", "hat": "hat909", "ohat": "openhat909", "tom": "tom909", "rim": "rim909"}
FREE = {"kick": ["tune", "bend", "bend_ms", "bend2", "bend2_ms", "decay", "hold", "shape", "attack", "click_hz",
                 "click_ms", "noise", "noise_ms"],
        "hat": ["low", "decay", "hold", "mid", "high", "top", "noise", "tilt", "hp", "body", "body_hp"],
        "ohat": ["low", "decay", "hold", "mid", "high", "top", "noise", "tilt", "hp", "body", "body_hp"],
        "tom": ["tune_low", "tune_high", "bend", "bend_ms", "decay", "hold", "noise", "noise_ms", "noise_lp", "shape"],
        "rim": ["f1", "f2", "f3", "l2", "l3", "d1", "d2", "d3", "click", "drive", "hp"]}
DEF = {"kick": T.KICK909, "hat": T.HAT909, "ohat": T.OHAT909, "tom": dict(T.TOM909, tune_low=88.0, tune_high=160.0),
       "rim": T.RIM909}
OLD = {"kick": [("clubkick", lambda s: C.hit("clubkick", {}, seed=s)), ("kick", lambda s: C.hit("kick", {}, seed=s)),
                ("kicksub+punch+click", lambda s: _stack(s))],
       "hat": [("metalhat", lambda s: C.hit("metalhat", {}, seed=s)), ("hat", lambda s: C.hit("hat", {}, seed=s)),
               ("kithat", lambda s: C.hit("kithat", {}, seed=s))],
       "ohat": [("metalhat open", lambda s: C.hit("metalhat", {"open": True}, seed=s)),
                ("openhat", lambda s: C.hit("openhat", {}, seed=s))],
       "tom": [("tom", lambda s: C.hit("tom", {}, seed=s)), ("kittom", lambda s: C.hit("kittom", {}, seed=s))],
       "rim": [("rim", lambda s: C.hit("rim", {}, seed=s))]}


def _stack(s):
    a = C.hit("kicksub", {}, seed=s)
    b = C.hit("kickpunch", {}, seed=s) * 10 ** (-7 / 20)
    c = C.hit("kickclick", {}, seed=s) * 10 ** (-5 / 20)
    n = max(len(a), len(b), len(c))
    return sum(np.pad(x, (0, n - len(x))) for x in (a, b, c))


def ref_feats(kind, files):
    return [C.feats(C.load(f), WINS[kind], BANDS[kind]) for f in files]


def det_files(kind):
    by = {os.path.basename(f["path"]): f for f in C.refs(ids=("refs-tr909-detroit",))}
    return [by[n] for n in DET[kind]]


def model_hits(kind, q, seed):
    if kind == "tom":
        out = []
        for pitch in ("low", "high"):
            p = {k: v for k, v in q.items() if not k.startswith("tune_")}
            p["tune"] = q["tune_" + pitch]
            out.append(C.hit("tom909", p, seed=seed))
        return out
    return [C.hit(MODEL[kind], q, seed=seed)]


def score(kind, q, R, seeds=(0,)):
    out = []
    for s in seeds:
        H = model_hits(kind, q, s)
        if kind == "tom":
            d = [C.dist(C.feats(h, WINS[kind], BANDS[kind]), r) for h, r in zip(H, R)]
        else:
            F = C.feats(H[0], WINS[kind], BANDS[kind])
            d = [C.dist(F, r) for r in R]
        out.append(np.mean(d, 0))
    return np.mean(out, 0)


def fit(kind):
    R = ref_feats(kind, det_files(kind))
    q0 = dict(DEF[kind])
    names = FREE[kind]
    x0 = np.array([float(q0[k]) for k in names])

    def f(x):
        q = dict(q0, **{k: float(v) for k, v in zip(names, x)})
        try:
            return score(kind, q, R)[2]
        except Exception:
            return 1e6
    xb, fb = C.minimize_log(f, x0, maxiter=600, restarts=3, verbose=kind)
    q = dict(q0, **{k: float(v) for k, v in zip(names, xb)})
    print(kind, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in q.items()}), flush=True)
    return q


def check():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = {}
    fig, axs = plt.subplots(1, 5, figsize=(22, 4))
    for ax, kind in zip(axs, WINS):
        Rd = ref_feats(kind, det_files(kind))
        fs = C.refs(FS_ROLE[kind], ids=("refs-techno-cc0", "refs-techno-ccby"))
        Rf = ref_feats(kind, fs)
        q = dict(DEF[kind])
        rows = {}
        new = [score(kind, q, Rd, seeds=range(5))]
        cand = [("NEW " + MODEL[kind], None)] + [("old " + n, fn) for n, fn in OLD[kind]]
        for label, fn in cand:
            if fn is None:
                dd = score(kind, q, Rd, seeds=range(5))
                H = [model_hits(kind, q, s) for s in range(5)]
            else:
                H = [[fn(s)] * (2 if kind == "tom" else 1) for s in range(5)]
                dd = np.mean([np.mean([C.dist(C.feats(h, WINS[kind], BANDS[kind]), r) for h, r in
                                       (zip(hh, Rd) if kind == "tom" else [(hh[0], r) for r in Rd])], 0) for hh in H], 0)
            # the independent test: every Freesound 909 recording against the model's first hit
            df = np.mean([[C.dist(C.feats(hh[0] if kind != "tom" else hh[0], WINS[kind], BANDS[kind]), r)
                           for r in Rf] for hh in H], axis=(0, 1)) if Rf else [np.nan] * 3
            rows[label] = dict(fit_spec_db=round(float(dd[0]), 2), fit_env_log2=round(float(dd[1]), 3),
                               test_spec_db=round(float(df[0]), 2), test_env_log2=round(float(df[1]), 3),
                               test_n=len(Rf))
            print(f"{kind:5s} {label:26s} recorded 909 (fit): spectrum {dd[0]:5.2f} dB, decay {dd[1]:.2f}   "
                  f"other 909 recordings (test, n={len(Rf)}): spectrum {df[0]:5.2f} dB, decay {df[1]:.2f}", flush=True)
            S, _ = C.feats((H[0][0]), WINS[kind], BANDS[kind])
            tot = 10 * np.log10(np.sum(10 ** (S / 10), 0) + 1e-12)
            ax.semilogx(C.THIRD, tot, lw=2 if fn is None else 1, ls="-" if fn is None else "--", label=label)
        RS = 10 * np.log10(np.sum(10 ** (Rd[0][0] / 10), 0) + 1e-12)
        ax.semilogx(C.THIRD, RS, "k", lw=2.5, label="TR-909 recorded")
        ax.set_title(kind)
        ax.set_ylim(RS.max() - 50, RS.max() + 5)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
        out[kind] = rows
    fig.tight_layout()
    fig.savefig(os.path.join(C.HERE, "909.png"), dpi=70)
    json.dump(out, open(os.path.join(C.HERE, "909-numbers.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1:2] == ["fit"]:
        for k in (sys.argv[2:] or list(WINS)):
            fit(k)
    else:
        check()
