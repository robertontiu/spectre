#!/usr/bin/env python3
"""Why session 017 "Captive" doesn't peak: measurements of its drops against docs/DUBSTEP.md and the references
(README.md, "Why Captive doesn't peak"). Reads a render of sessions/017-captive/project.json made OUTSIDE the
session folder, mastered as published (bit-identical to the published master: -8.7 LUFS, -1.03 dBTP, PLR 7.6):

    mkdir -p /tmp/me/s017 && cp sessions/017-captive/project.json /tmp/me/s017/
    cd /tmp/me/s017 && bash <repo>/tools/remix/waitfree.sh render && BEAT_DIR=$PWD python3 <repo>/engine/studio.py render
    bash <repo>/tools/remix/waitfree.sh master && BEAT_DIR=$PWD python3 <repo>/engine/studio.py master v001 --genre dubstep --lufs -8.5
    bash <repo>/tools/remix/waitfree.sh render && python3 <repo>/examples/production/dubstep-v2/diagnose.py /tmp/me/s017

Writes diagnosis.json here (numbers only).
"""
import copy
import json
import os
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sounds as SO  # noqa: E402

SR = SO.SR


def third(x, cs):
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.array([10 * np.log10(X[(f >= c * 2 ** -(1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in cs])


def main(d):
    import pyloudnorm as pyln
    import soundfile as sf
    meta = json.load(open(os.path.join(d, "renders", "v001.meta.json")))
    y, _ = sf.read(os.path.join(d, "renders", "v001.master.wav"), always_2d=True)
    y = y.T
    rep = json.load(open(os.path.join(d, "renders", "v001.master.report.json")))
    sec = {s["name"]: s for s in meta["sections"]}
    meter = pyln.Meter(SR)
    out = {"master": {k: rep["out"][k] for k in ("lufs", "true_peak", "plr", "short_term_max", "loudness_range")}}

    def st_curve(a, b, win=3.0):
        w = int(win * SR)
        return [meter.integrated_loudness(y[:, i:i + w].T) for i in range(a, max(a + 1, b - w), SR // 10)]
    # 1. loudness per section
    L = {}
    for nm in ("intro_sing", "build1", "build1b", "drop1a", "drop1b", "drop1c", "panic", "panic2", "drop2a", "drop2b",
               "drop2c"):
        a, b = int(sec[nm]["start"] * SR), int(sec[nm]["end"] * SR)
        c = st_curve(a, b)
        seg = y[:, a:b]
        L[nm] = {"short_term_median": round(float(np.median(c)), 1), "short_term_max": round(float(np.max(c)), 1),
                 "peak_to_short_term_db": round(float(20 * np.log10(np.abs(seg).max()) - np.median(c)), 1)}
    out["loudness by section (master)"] = L
    # 2. tone of drop 1 against dubstep_2015
    T = json.load(open(os.path.join(SO.REPO, "engine", "targets.json")))["dubstep_2015"]
    cs = np.array([float(h) for h in T["curve"]])
    tgt = np.array(list(T["curve"].values()), dtype=float)
    a, b = int(sec["drop1a"]["start"] * SR), int(sec["drop1c"]["end"] * SR)
    mine = third(y[:, a:b].mean(0), cs)
    mine -= mine[np.argmin(np.abs(cs - 1000))]
    dev = mine - tgt
    sel = (cs >= 31) & (cs <= 16000)
    groups = {"31.5-40": (31, 41), "50-63": (49, 64), "80-125": (79, 126), "160-400": (159, 401),
              "500-1250": (499, 1251), "1.6-4k": (1599, 4001), "5-10k": (4999, 10001), "12.5-16k": (12499, 16001)}
    out["drop 1 (mastered) against dubstep_2015 re 1 kHz"] = {
        "rms_db": round(float(np.sqrt(np.mean(dev[sel] ** 2))), 1),
        "by band (mean dB)": {g: round(float(dev[(cs >= lo) & (cs <= hi)].mean()), 1) for g, (lo, hi) in groups.items()}}
    # 3. the drop's first beat
    a = int(sec["drop1a"]["start"] * SR)
    beat = 60 / 140
    mom = lambda i: meter.integrated_loudness(y[:, i:i + int(0.4 * SR)].T)
    pre = [mom(i) for i in range(int(a - 4 * beat * SR), a - int(0.4 * SR), SR // 20)]
    post = [mom(i) for i in range(a, int(a + 4 * beat * SR), SR // 20)]
    lo_pre = third(y[:, int(a - 2 * beat * SR):a].mean(0), np.array([50.0, 63, 80]))
    lo_post = third(y[:, a:int(a + 2 * beat * SR)].mean(0), np.array([50.0, 63, 80]))
    q = y[:, int(a - beat * SR):a]
    out["the drop's first beat"] = {
        "momentary LU, the drop's first bar minus the build's last bar (medians)": round(float(np.median(post) - np.median(pre)), 1),
        "the build's quietest 400 ms in its last beat (LUFS)": round(float(min(mom(i) for i in range(int(a - beat * SR), a - int(0.4 * SR) + 1, SR // 100))), 1),
        "the build's last beat, peak dBFS": round(float(20 * np.log10(np.abs(q).max() + 1e-12)), 1),
        "50-80 Hz energy, the drop's first two beats minus the build's last two (dB)": round(float(
            10 * np.log10(np.sum(10 ** (lo_post / 10)) / np.sum(10 ** (lo_pre / 10)))), 1)}
    # 4. drums and bass in drop 1A (a window render of the stems)
    P = copy.deepcopy(SO.P17)
    st = {}
    t0, t1 = sec["drop1a"]["start"], sec["drop1a"]["end"]
    SO.ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.copy()), window=(t0, t1), quiet=True)
    off = int(2 * 4 * 60 / 140 * SR)
    S = {k: v[:, off:off + int((t1 - t0) * SR)].mean(0) for k, v in st.items()}
    bass = S["captor"] + S.get("soul", 0) + S.get("chop", 0)

    def rms_db(x):
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
    out["drop 1A stems (window render, before the buses)"] = {
        nm: {"crest_db": round(float(20 * np.log10(np.abs(S[nm]).max()) - rms_db(S[nm])), 1),
             "peak_vs_bass_peak_db": round(float(20 * np.log10(np.abs(S[nm]).max() / np.abs(bass).max())), 1),
             "rms_vs_bass_rms_db": round(float(rms_db(S[nm]) - rms_db(bass)), 1)} for nm in ("kick", "snare", "sub")}
    cap = S["captor"]
    X = np.abs(np.fft.rfft(cap)) ** 2
    f = np.fft.rfftfreq(len(cap), 1 / SR)
    t150 = X[(f >= 150) & (f < 16000)].sum()
    out["captor in drop 1A (stem)"] = {g: round(float(10 * np.log10(X[(f >= lo) & (f < hi)].sum() / t150)), 1)
                                       for g, lo, hi in (("150-500 re >150", 150, 500), ("500-2k re >150", 500, 2000),
                                                         ("2-5k re >150", 2000, 5000), ("5-16k re >150", 5000, 16000))}
    json.dump(out, open(os.path.join(HERE, "diagnosis.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
