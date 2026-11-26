#!/usr/bin/env python3
"""Fit the techno presets (engine/techno_presets.json: `hardkick`, `hoover`) to the references (engine/third_party.json
`refs-techno-*` roles hardkick and hoover), as examples/production/dubstep-v2/fit.py did for the bass presets: the
patch and its dynamics (distortion, clip, transient) set by hand against the references' descriptors (crest, loudness
density, band decay times: dubstep-v2/describe.py), then a `curve` (third-octave gains) fitted in four renders, each
moving it 0.8 of the way to the references' median spectrum (smoothed over five bands, re-anchored where the sound's
energy is, limited to +/-9 dB). Writes engine/techno_presets.json.

    bash tools/remix/waitfree.sh render && python3 examples/production/techno/fitpresets.py [hardkick|hoover] [--show]
"""
import copy
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
sys.path.insert(0, os.path.join(C.HERE, "..", "dubstep-v2"))
import describe as DS  # noqa: E402

THIRD = DS.THIRD
BASE = {
    "hardkick": dict(note="X...............", bars=1, sustained=False, lim=9, fitted_to="15 hard-techno kicks (dynamics by a Nelder-Mead search on crest, loudness density, band decays and six band shares, tune held at 55 Hz)", test="one hit at A1 (55 Hz), 150 bpm", track={
        "role": "kick", "humanize_ms": 0, "vel_jitter": 0.02,
        "layers": [{"name": "body", "inst": {"type": "kicksub", "tune": 55, "punch": 24, "drop": 0.0165, "hold": 0.0246,
                                              "tail": 0.0452, "length": 0.32, "drive": 0.5}, "role": "kick",
                    "eq": {"own_db": 0, "cut_db": 0}},
                   {"name": "punch", "inst": {"type": "kickpunch", "tune": 100, "decay": 0.05, "thump": 0.4,
                                               "drive": 0.4}, "role": "kick", "eq": {"hp": 70, "own_db": 0},
                    "gain_db": -4.4},
                   {"name": "click", "inst": {"type": "kickclick", "tone": 3500, "noise": 0.6, "decay": 0.006},
                    "role": "kick", "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}, "gain_db": -3.94}],
        "fx": [{"type": "asym", "amount": 0.56, "bias": 0.2}, {"type": "hardclip", "drive_db": 3.1, "ceiling_db": -1},
               {"type": "transient", "attack_db": 3.89, "sustain_db": 0}, "CURVE",
               {"type": "clip", "drive_db": 6.23, "ceiling_db": -1}]}),
    "hoover": dict(note="0:F2:32", bars=2, sustained=True, lim=12, fitted_to="6 hoover sounds", test="a held F2, two bars, 150 bpm", track={
        "role": "lead", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "polysynth",
                 "osc": [{"shape": "pulse", "voices": 3, "detune": 28, "spread": 0.9, "pw": 0.3},
                         {"shape": "saw", "voices": 3, "detune": 22, "spread": 0.9, "octave": -1, "level": 0.7}],
                 "cutoff": 3200, "reso": 0.15, "attack": 0.01, "decay": 0.4, "sustain_level": 0.9, "release": 0.25,
                 "lfo": [{"dest": "pw", "rate": 0.9, "depth": 0.18, "shape": "sine"}],
                 "env2": {"dest": "pitch", "depth": -500, "attack": 0.0, "decay": 0.09, "sustain": 0.0}},
        "fx": ["CURVE", {"type": "chorus"}, {"type": "ott", "depth": 0.6},
               {"type": "clip", "drive_db": 9, "ceiling_db": -1}]}),
}
NIT = 6


def build(spec, pts):
    tr = copy.deepcopy(spec["track"])
    tr["fx"] = [({"type": "curve", "points": pts} if f == "CURVE" else f) for f in tr["fx"]]
    return tr


def render(tr, note, bars):
    P = C.project({"x": tr}, {"p": {"bars": bars, "x": note}}, bars)
    return C.stems(P)["x"]


def ref_d(role, sustained):
    return [DS.describe(C.load(f), 150, sustained) for f in C.refs(role)]


def show(role, x, D, sustained):
    d = DS.describe(x, 150, sustained)
    med = lambda k, s=None: float(np.median([(r[k][s] if s else r[k]) for r in D]))  # noqa: E731
    print(f"{role}: crest {d['crest_db']} (refs {med('crest_db'):.1f}), density {d['lufs_m_max']} LUFS ({med('lufs_m_max'):.1f}), "
          f"decay low/mid/high {d['decay20_ms']} (refs {med('decay20_ms', 'low'):.0f}/{med('decay20_ms', 'mid'):.0f}/"
          f"{med('decay20_ms', 'high'):.0f}), centroid {d['centroid_hz']} ({med('centroid_hz'):.0f})")
    print("   groups", d["groups_db"], "\n   refs  ", {g: round(med("groups_db", g), 1) for g in d["groups_db"]})
    return d


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = os.path.join(C.REPO, "engine", "techno_presets.json")
    out = json.load(open(path))
    for role, spec in BASE.items():
        if args and role not in args:
            continue
        D = ref_d(role, spec["sustained"])
        refT = np.median(np.array([d["third_db"] for d in D]), 0)
        pts = np.zeros(len(THIRD))
        hist = []
        for it in range(NIT):
            tr = build(spec, {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})
            x = render(tr, spec["note"], spec["bars"])
            et = np.array(DS.describe(x, 150, spec["sustained"])["third_db"])
            dev = refT - et
            ok = refT > refT.max() - 45
            sm = np.convolve(np.pad(dev, 2, mode="edge"), np.array([1, 2, 3, 2, 1]) / 9, mode="valid")
            hist.append(round(float(np.sqrt(np.mean(dev[ok] ** 2))), 2))
            if it < NIT - 1:
                pts = pts + 0.8 * np.where(ok, sm, 0.0)
                w = 10 ** (et / 10) * ok
                pts = pts - np.sum(w * pts) / np.sum(w)
                pts = np.clip(pts, -spec["lim"], spec["lim"])
        final = build(spec, {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})
        d = show(role, render(final, spec["note"], spec["bars"]), D, spec["sustained"])
        out["presets"][role] = {"fitted_to": f"{spec['fitted_to']} (median third-octave spectrum)", "test": spec["test"],
                                "third_octave_rms_dev_db": hist, "track": final}
        print(role, "third-octave RMS deviation from the references' median, per iteration (dB):", hist, flush=True)
    if "--show" not in sys.argv:
        json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
