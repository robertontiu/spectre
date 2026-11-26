#!/usr/bin/env python3
"""The loud-techno master test (docs/TECHNO.md "Engine mapping" gap 4): does `--genre techno --strand hard` land the
loudest 2 minutes of a hard-techno track at about -7.5 to -7 LUFS short-term with a sane true peak, and how does the
default `--genre techno` (-9.5 LUFS integrated) behave on a track with long DJ intros and outros?

    bash tools/remix/waitfree.sh master && python3 examples/production/techno/mastertest.py     # ~8 minutes

The track: the A/B excerpt's fitted sounds (build.py `excerpt(True)`: hardkick with its rumble, 909 hats and clap,
congas, bongos, a free-running 909 tom, acid, hoover) at 150 bpm in TECHNO.md's DJ form, 176 bars (4:42): intro 32
bars of kick and rumble (hats from bar 17), main 48 adding percussion and acid, a 16-bar breakdown without the kick, the
peak 48 with the hoover, an outro 32 back to kick, rumble and hats. A second version has 8-bar ends instead (the
loud section is most of the track). Each premaster goes through engine/master.py with the flags below; the numbers go
to numbers.json ("master"). Temporary files in a removed temporary folder."""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as BD  # noqa: E402
import common as C  # noqa: E402
import master as M  # noqa: E402
import pyloudnorm as pyln  # noqa: E402
import studio as ST  # noqa: E402

SR = C.SR


def track(long_ends=True):
    P = BD.excerpt(True)
    P["patterns"]["kk"] = {"kick": BD.FOUR}
    P["patterns"]["hh"] = dict(BD.HATPAT)
    P["patterns"]["cl"] = {"clap": "....x.......x..."}
    e = 32 if long_ends else 8
    P["arrangement"] = [
        {"name": "intro", "bars": e // 2, "play": ["kk"], "auto": {"return:rumble": {"lpf": [90, 160]}}},
        {"name": "intro2", "bars": e // 2, "play": ["kk", "hh"]},
        {"name": "main", "bars": 48, "play": ["k", "p", "t3", "a"], "auto": {"acid": {"inst": {"cutoff": [500, 1500]}}}},
        {"name": "break", "bars": 16, "play": ["hh", "a", "t3"], "auto": {"acid": {"inst": {"cutoff": [1500, 900]}}}},
        {"name": "peak", "bars": 48, "play": ["k", "p", "t3", "a", "h"],
         "auto": {"acid": {"inst": {"cutoff": [1500, 2500], "reso": [0.8, 0.9]}}}},
        {"name": "outro", "bars": e // 2, "play": ["kk", "hh", "cl"]},
        {"name": "outro2", "bars": e // 2, "play": ["kk"]}]
    return P


def loudest(x, secs, win=120.0):
    """Short-term loudness (3 s, 1 s hop) over the loudest `win` seconds (the window with the highest integrated
    loudness), and the intro's and the peak's medians."""
    m = pyln.Meter(SR)
    st = M.short_term_lufs(x, m)
    n = int(win)
    best, k0 = -99, 0
    for k in range(0, max(1, len(st) - n)):
        seg = x[:, int(k * SR):int((k + win) * SR)]
        v = m.integrated_loudness(seg.T)
        if v > best:
            best, k0 = v, k
    w = st[k0:k0 + n - 2]
    by = {}
    for S in secs:
        v = st[int(np.ceil(S["start"])):max(int(np.ceil(S["start"])) + 1, int(S["end"] - 3) + 1)]
        by[S["name"]] = round(float(np.median(v)), 1) if len(v) else None
    return dict(loudest_2min_integrated=round(float(best), 1), loudest_2min_start_s=k0,
                loudest_2min_short_term_median=round(float(np.median(w)), 1),
                loudest_2min_short_term_max=round(float(np.max(w)), 1), section_short_term_median=by)


def main():
    out = {}
    with tempfile.TemporaryDirectory() as td:
        for name, long_ends in (("DJ ends (32-bar intro and outro)", True), ("short ends (8 bars)", False)):
            subprocess.run(["bash", os.path.join(C.REPO, "tools", "remix", "waitfree.sh"), "render"], check=True,
                           capture_output=True)
            mix, meta = ST.render(track(long_ends), quiet=True)
            pre = os.path.join(td, f"{long_ends}.premaster.wav")
            sf.write(pre, meta["_premaster"].T, SR, subtype="FLOAT")
            for flags in (["--strand", "hard"], ["--strand", "hard", "--lufs", "-8"], []):
                subprocess.run(["bash", os.path.join(C.REPO, "tools", "remix", "waitfree.sh"), "master"], check=True,
                               capture_output=True)
                o = os.path.join(td, "m.wav")
                subprocess.run([sys.executable, os.path.join(C.REPO, "engine", "master.py"), pre, "--genre", "techno",
                                *flags, "--out", o], check=True, capture_output=True)
                rep = json.load(open(o.replace(".wav", ".report.json")))
                x, _ = sf.read(o)
                r = dict(loudest(x.T.astype(np.float64), meta["sections"]), integrated=rep["out"]["lufs"],
                         true_peak=rep["out"]["true_peak"], plr=rep["out"]["plr"],
                         limiter_max_gr_db=rep.get("limiter_max_gr_db"), drive_db=rep.get("drive_db"),
                         duration_s=round(x.shape[0] / SR, 1))
                label = f"{name}, --genre techno {' '.join(flags)}".strip()
                out[label] = r
                print(label, json.dumps(r), flush=True)
    npath = os.path.join(C.HERE, "numbers.json")
    numbers = json.load(open(npath)) if os.path.exists(npath) else {}
    numbers["master"] = out
    json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
