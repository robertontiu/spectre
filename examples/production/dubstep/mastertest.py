#!/usr/bin/env python3
"""The dubstep master test (docs/DUBSTEP.md "Engine mapping" gap 8): does a clip-first master land a dubstep drop at
-6.5 to -6 LUFS short-term with a sane true peak, and does `--lufs -8.5` behave on a track with a long quiet outro?

    bash tools/remix/waitfree.sh master && python3 examples/production/dubstep/mastertest.py

The track: the B drop of build.py (fmgrowl, sampler chops, 909 snare and clap, clipped drum and bass buses) as a
16-bar drop between an 8-bar intro (pad and hats) and an outro (pad, 16 bars falling 14 dB; and a version without
it). Each premaster goes through engine/master.py with `--genre dubstep` and the flags below; numbers go to
numbers.json ("master"). Temporary files in a temporary folder that is removed."""
import copy
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "engine"))
import build as BD  # noqa: E402
import master as M  # noqa: E402
import pyloudnorm as pyln  # noqa: E402
import studio as ST  # noqa: E402

SR = 44100


def track(outro=True):
    P = BD.drop(True)
    P["tracks"]["pad"] = BD.T({"type": "polysynth", "osc": [{"shape": "saw", "voices": 4, "detune": 15}],
                               "cutoff": 1800, "attack": 0.4, "release": 1.2}, role="pad", eq="auto", send_reverb=0.3,
                              gain_db=-4)
    P["patterns"]["p"] = {"bars": 2, "pad": {"chords": "Fm9:16 Dbmaj7:16", "style": "sustain", "register": "F3",
                                             "voicing": "keys", "vel": 0.6}}
    P["patterns"]["h"] = {"bars": 1, "hats": "x.x.x.x.x.x.x.x."}
    arr = [{"name": "intro", "bars": 8, "play": ["p", "h"]},
           {"name": "dropA", "bars": 8, "play": ["d", "b"], "enter": {"impact": 0.8}},
           {"name": "dropB", "bars": 8, "play": ["d", "b", "c"]}]
    if outro:
        arr.append({"name": "outro", "bars": 16, "play": ["p"], "auto": {"pad": {"gain_db": [0, -14]}}})
    P["arrangement"] = arr
    return P


def drop_st(path, secs):
    x, _ = sf.read(path)
    x = x.T.astype(np.float64)
    m = pyln.Meter(SR)
    st = M.short_term_lufs(x, m)            # 3 s windows, 1 s hop: window k covers [k, k + 3) s
    a = [S for S in secs if S["name"].startswith("drop")]
    t0, t1 = a[0]["start"], a[-1]["end"]
    v = st[int(np.ceil(t0)):int(t1 - 3) + 1]
    return dict(drop_short_term_max=round(float(v.max()), 1), drop_short_term_median=round(float(np.median(v)), 1))


def main():
    out = {}
    with tempfile.TemporaryDirectory() as td:
        for name, outro in (("with outro", True), ("without outro", False)):
            mix, meta = ST.render(track(outro))
            pre = os.path.join(td, f"{outro}.premaster.wav")
            sf.write(pre, meta["_premaster"].T, SR, subtype="FLOAT")
            for flags in (["--lufs", "-8"], ["--lufs", "-8.5"], ["--lufs", "-7"], ["--lufs", "-6.5"]):
                o = os.path.join(td, "m.wav")
                subprocess.run([sys.executable, os.path.join(REPO, "engine", "master.py"), pre, "--genre", "dubstep",
                                *flags, "--out", o], check=True, capture_output=True)
                rep = json.load(open(o.replace(".wav", ".report.json")))
                r = dict(drop_st(o, meta["sections"]), integrated=rep["out"]["lufs"], true_peak=rep["out"]["true_peak"],
                         plr=rep["out"]["plr"], limiter_max_gr_db=rep.get("limiter_max_gr_db"), drive_db=rep.get("drive_db"))
                out[f"{name}, --genre dubstep {' '.join(flags)}"] = r
                print(name, flags, r, flush=True)
    npath = os.path.join(HERE, "numbers.json")
    numbers = json.load(open(npath)) if os.path.exists(npath) else {}
    numbers["master"] = out
    json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
