#!/usr/bin/env python3
"""Fit the bass-music presets (engine/bass_presets.json) to the references: each preset's patch and dynamics were set
by hand against the references' descriptors (tables.md); its `curve` (third-octave gains) is fitted here, iterating
four renders: the deviation of the patch's third-octave spectrum from the median of the role's references (re total
energy for drums, re the energy above 150 Hz for bass voices, whose lows belong to the sub) is smoothed over five
bands, 0.8 of it added to the curve, the curve re-anchored where the sound's energy is (a tone change, not a level
change) and limited to +/-6-12 dB. Writes engine/bass_presets.json (the presets as they are now were made with it).

    python3 examples/production/dubstep-v2/refs.py          # refs-numbers.json first (the references' spectra)
    bash tools/remix/waitfree.sh render && python3 examples/production/dubstep-v2/fit.py [role ...]   # ~30 s
"""
import collections
import copy
import json
import os
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import describe as DS  # noqa: E402
import sounds as SO  # noqa: E402

THIRD = DS.THIRD
NAME = {"hat": "hats"}
TEST = {"growl": "a held F#1, one bar, r=1/8", "riddim": "a held F#1, one bar, r=1/8", "wobble": "a held F#1, two bars",
        "reese": "a held F#1, two bars", "screech": "a held F#3, one bar", "snare": "one hit", "clap": "one hit",
        "kick": "one hit", "hat": "one hit"}


def ref_third(R, role, above=None):
    A = np.array([r["d"]["third_db"] for r in R if r["role"] == role])
    if above:
        sel = THIRD >= above
        A = A - 10 * np.log10(np.sum(10 ** (A[:, sel] / 10), 1, keepdims=True))
    return np.median(A, 0)


def eng_third(x, above=None):
    t = np.array(DS.describe(x, 140, True)["third_db"])
    if above:
        sel = THIRD >= above
        t = t - 10 * np.log10(np.sum(10 ** (t[sel] / 10)))
    return t


BASE = {
    "growl": dict(note="0:F#1:16/r=1/8", bars=1, above=150, lim=6, track={
        "role": "upper-bass", "eq": "auto", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "fmgrowl", "ops": [{"ratio": 1}, {"ratio": 2, "index": 1.5}, {"ratio": 1, "index": 1.0}],
                 "feedback": 0.2, "voices": 2, "detune": 14, "spread": 0.3, "fold": 0.15, "drive": 0.5, "cutoff": 2400,
                 "release": 0.05, "mod": [{"dest": "index", "rate": "1/8", "shape": "saw", "depth": 5},
                                          {"dest": "cutoff", "rate": "1/8", "shape": "saw", "depth": 2.5}]},
        "fx": ["CURVE", {"type": "multiband", "split": [150, 2000],
                         "bands": [[{"type": "comp", "threshold_db": -18, "ratio": 3}], [{"type": "ott", "depth": 0.5}],
                                   [{"type": "ott", "depth": 0.5}, {"type": "hardclip", "drive_db": 2}]],
                         "gains_db": [-2, -5, 1], "widths": [0, 0.5, 0.6]},
               {"type": "clip", "drive_db": 10, "ceiling_db": -1}]}),
    "riddim": dict(note="0:F#1:16/r=1/8", bars=1, above=150, lim=9, track={
        "role": "upper-bass", "eq": "auto", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "wavetable", "table": "harsh", "pos": 0.35, "voices": 4, "detune": 18, "spread": 0.9,
                 "fold": 0.2, "drive": 0.6, "cutoff": 2500, "release": 0.04,
                 "mod": [{"dest": "pos", "rate": "1/8", "shape": "square", "depth": 0.5},
                         {"dest": "cutoff", "rate": "1/4", "shape": "saw", "depth": 2.5}]},
        "fx": ["CURVE", {"type": "flanger", "rate": "1/2", "feedback": 0.5, "mix": 0.3},
               {"type": "multiband", "split": [150, 2000],
                "bands": [[{"type": "comp", "threshold_db": -18, "ratio": 3}], [{"type": "ott", "depth": 0.6}],
                          [{"type": "ott", "depth": 0.7}, {"type": "hardclip", "drive_db": 6}]],
                "widths": [0, 1.4, 1.6]},
               {"type": "mseq", "side_hpf": 150}, {"type": "clip", "drive_db": 7, "ceiling_db": -1}]}),
    "wobble": dict(note="0:F#1:32", bars=2, above=150, lim=9, track={
        "role": "upper-bass", "eq": "auto", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 14}], "cutoff": 500,
                 "reso": 0.5, "sustain_level": 1.0, "release": 0.05,
                 "lfo": [{"dest": "cutoff", "rate": "1/8", "depth": 3.0, "shape": "triangle"}]},
        "fx": ["CURVE", {"type": "asym", "amount": 0.5, "bias": 0.2}, {"type": "ott", "depth": 0.4},
               {"type": "mseq", "side_hpf": 150}, {"type": "clip", "drive_db": 9, "ceiling_db": -1}]}),
    "reese": dict(note="0:F#1:32", bars=2, above=150, lim=9, track={
        "role": "upper-bass", "eq": "auto", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 2, "detune": 15},
                                              {"shape": "saw", "voices": 2, "detune": 6}],
                 "cutoff": 5000, "sustain_level": 1, "release": 0.1,
                 "lfo": [{"dest": "detune", "rate": "1/16d", "depth": 0.3}]},
        "fx": ["CURVE", {"type": "asym", "amount": 0.4, "bias": 0.25}, {"type": "ott", "depth": 0.8},
               {"type": "mseq", "side_hpf": 250}, {"type": "clip", "drive_db": 10, "ceiling_db": -1}]}),
    "screech": dict(note="0:F#3:16", bars=1, above=150, lim=9, track={
        "role": "upper-bass", "eq": "auto", "humanize_ms": 0, "vel_jitter": 0,
        "inst": {"type": "fmgrowl", "ops": [{"ratio": 1}, {"ratio": 3, "index": 2.0}], "feedback": 0.5, "voices": 3,
                 "detune": 25, "spread": 0.9, "fold": 0.2, "drive": 0.6, "cutoff": 9000, "release": 0.05,
                 "mod": [{"dest": "index", "rate": "1/16", "shape": "saw", "depth": 4},
                         {"dest": "pitch", "rate": "1/4", "shape": "sine", "depth": 0.5, "bipolar": True}]},
        "fx": ["CURVE", {"type": "flanger", "rate": "1/4", "feedback": 0.7, "mix": 0.5},
               {"type": "ott", "depth": 0.5}, {"type": "clip", "drive_db": 6, "ceiling_db": -1}]}),
    "snare": dict(note="X...............", bars=1, above=None, lim=9, drum=True, track={
        "role": "snare", "humanize_ms": 0, "vel_jitter": 0.02,
        "layers": [{"name": "body", "inst": {"type": "snare909", "tune": 200, "snappy": 0.7, "noise_decay": 0.07,
                                              "tone_decay": 0.05, "bend": 1.5, "bend_ms": 12, "body": 0.7,
                                              "drive": 0.4}, "role": "snare"},
                   {"name": "shell", "inst": {"type": "kitsnare", "tune": 190}, "role": "snare", "gain_db": -6},
                   {"name": "crack", "inst": {"type": "clap909"}, "role": "clap", "gain_db": -6}],
        "fx": ["CURVE", {"type": "transient", "attack_db": 0, "sustain_db": -3}, {"type": "clip", "drive_db": 2,
                                                                                  "ceiling_db": -1},
               {"type": "widen", "from_hz": 2000, "amount": 0.3}]}),
    "clap": dict(note="X...............", bars=1, above=None, lim=12, drum=True, track={
        "role": "clap", "humanize_ms": 0, "vel_jitter": 0.02, "inst": {"type": "clap909"},
        "fx": ["CURVE", {"type": "clip", "drive_db": 4, "ceiling_db": -1}]}),
    "kick": dict(note="X...............", bars=1, above=None, lim=9, drum=True, track={
        "role": "kick", "humanize_ms": 0, "vel_jitter": 0.02,
        "layers": [{"name": "sub", "inst": {"type": "kicksub", "tune": 50, "punch": 30, "drop": 0.04, "hold": 0.03,
                                             "tail": 0.04, "drive": 0.3}, "role": "kick",
                    "eq": {"own_db": 0, "cut_db": 0}},
                   {"name": "punch", "inst": {"type": "kickpunch", "tune": 110, "decay": 0.04}, "role": "kick",
                    "eq": {"hp": 70, "own_db": 0}, "gain_db": -6},
                   {"name": "click", "inst": {"type": "kickclick", "tone": 4500, "noise": 0.7, "decay": 0.02},
                    "role": "kick", "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}, "gain_db": 0}],
        "fx": ["CURVE", {"type": "clip", "drive_db": 5, "ceiling_db": -1}]}),
    "hat": dict(note="x...............", bars=1, above=None, lim=12, drum=True, track={
        "role": "hats", "humanize_ms": 0, "vel_jitter": 0.02,
        "inst": {"type": "metalhat", "decay": 0.018, "noise": 0.6, "partials": 0.3},
        "fx": ["CURVE", {"type": "widen", "from_hz": 4000, "amount": 0.12}]}),
}


NIT = 4


def build(spec, pts):
    tr = copy.deepcopy(spec["track"])
    tr["fx"] = [({"type": "curve", "points": pts} if f == "CURVE" else f) for f in tr["fx"]]
    return tr


def main():
    R = json.load(open(os.path.join(HERE, "refs-numbers.json")))["refs"]
    n = collections.Counter(r["role"] for r in R)
    path = os.path.join(SO.REPO, "engine", "bass_presets.json")
    out = json.load(open(path))
    only = sys.argv[1:]
    for role, spec in BASE.items():
        if only and role not in only:
            continue
        refT = ref_third(R, role, spec["above"])
        pts = np.zeros(len(THIRD))
        hist = []
        for it in range(NIT):
            tr = build(spec, {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})
            x = SO.one(tr, spec["note"], spec["bars"], "x")
            et = eng_third(x, spec["above"])
            dev = refT - et
            ok = refT > refT.max() - 45
            if spec["above"]:
                ok &= THIRD >= spec["above"]
            sm = np.convolve(np.pad(dev, 2, mode="edge"), np.array([1, 2, 3, 2, 1]) / 9, mode="valid")
            hist.append(round(float(np.sqrt(np.mean(dev[ok] ** 2))), 2))
            if it < NIT - 1:
                pts = pts + 0.8 * np.where(ok, sm, 0.0)
                w = 10 ** (et / 10) * ok
                pts = pts - np.sum(w * pts) / np.sum(w)
                pts = np.clip(pts, -spec["lim"], spec["lim"])
        out["presets"][NAME.get(role, role)] = {
            "fitted_to": f"{n[role]} reference {role} sounds (median third-octave spectrum)", "test": TEST[role],
            "third_octave_rms_dev_db": hist,
            "track": build(spec, {str(c): round(float(v), 1) for c, v in zip(THIRD, pts)})}
        print(role, "third-octave RMS deviation from the references' median, per iteration (dB):", hist, flush=True)
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
