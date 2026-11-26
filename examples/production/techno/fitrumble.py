#!/usr/bin/env python3
"""Fit the rumble (engine/techno.py `rumble`, a return `"type": "rumble"`) to recorded kick-and-rumble loops
(engine/third_party.json `refs-techno-*` role rumble: 8 Freesound loops at 130-158 bpm; measured only).

    bash tools/remix/waitfree.sh render && python3 examples/production/techno/fitrumble.py fit     # ~5 min
    python3 examples/production/techno/fitrumble.py check      # rumble-numbers.json, the table in README.md

What is measured on each loop (and on the engine's `hardkick` preset with its rumble, 8 bars at 150 bpm, bars 3-8):
  pump      the 30-150 Hz level through the beat, folded over every beat from kick to kick (20 phase bins, dB under the
            loudest), the median over beats: the dip after each kick and the swell before the next;
  spectrum  third-octave shares of 25-800 Hz (dB re that range): where the rumble's energy sits (the low-pass);
  between   the 30-150 Hz level in the second half of the beat against the kick's first 10%.
The score is the median over the loops of the RMS dB differences of pump and spectrum. The engine's kick is not the
references' kicks: the fit sets the rumble (decay, drive, low-pass, duck depth, release, swell curve, level), not the
kick."""
import json
import os
import re
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import techno as T  # noqa: E402

SR = C.SR
BINS = 20
LOW = [c for c in C.THIRD if c <= 800]
FREE = ["decay", "drive_db", "lpf", "duck_db", "release", "curve", "neg_level_db"]


def lowenv(m, lo=30, hi=150, hop=220):
    y = signal.sosfilt(signal.butter(4, [lo, hi], btype="band", fs=SR, output="sos"), m)
    return np.sqrt(np.convolve(y ** 2, np.ones(hop) / hop, mode="same")[::hop]), SR / hop


def bpm_of(f, e, fps):
    mm = re.search(r"(\d{3})\s*bpm", f.get("title", "").lower())
    if mm:
        return float(mm.group(1))
    d = np.maximum(np.diff(e), 0)
    ac = np.correlate(d, d, "full")[len(d) - 1:]
    lags = np.arange(len(ac))
    bp = 60 * fps / np.maximum(lags, 1)
    sel = (bp >= 118) & (bp <= 175)
    return float(bp[sel][np.argmax(ac[sel])])


def features(m, bpm=None, f=None, t0=0.0):
    m = m[int(t0 * SR):]
    e, fps = lowenv(m)
    bpm = bpm or bpm_of(f or {}, e, fps)
    per = 60 / bpm * fps
    pk, _ = signal.find_peaks(e, distance=int(per * 0.7), height=e.max() * 0.3)
    segs = []
    for p in pk:
        a = p - 1
        if a < 0 or a + per + 1 > len(e):
            continue
        xs = a + np.arange(BINS) * per / BINS
        segs.append(np.interp(xs, np.arange(len(e)), e))
    F = np.median(np.array(segs), 0)
    pump = 20 * np.log10(F / F.max() + 1e-9)
    X = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
    fr = np.fft.rfftfreq(len(m), 1 / SR)
    s = np.array([X[(fr >= c * 2 ** (-1 / 6)) & (fr < c * 2 ** (1 / 6))].sum() for c in LOW])
    spec = 10 * np.log10(s / s.sum() + 1e-12)
    between = float(np.median(pump[BINS // 2:]) - np.median(pump[:2]))
    return dict(bpm=bpm, n_beats=len(segs), pump=pump, spec=spec, between=between)


def ref_feats():
    out = []
    for f in C.refs("rumble"):
        out.append(dict(features(C.load(f).mean(0), f=f), id=f["path"]))
    return out


def engine(cfg, kick=None, bars=8, bpm=150, note="A1"):
    tr = {"preset": "hardkick", "inst": {"note": note}} if kick is None else dict(kick)
    if cfg is not None:
        tr["rumble"] = dict(cfg)
    P = C.project({"kick": tr}, {"p": {"bars": 1, "kick": "x...x...x...x..."}}, bars, bpm=bpm)
    st = C.stems(P)
    m = st["kick"].mean(0) + (st["(rumble)"].mean(0) if "(rumble)" in st else 0)
    return m, st


def score(F, R):
    d = [np.sqrt(np.mean((F["pump"] - r["pump"]) ** 2)) + np.sqrt(np.mean((F["spec"] - r["spec"]) ** 2)) for r in R]
    return float(np.median(d))


def cfg_of(x):
    q = dict(zip(FREE, x))
    q["level_db"] = -q.pop("neg_level_db")
    return q


def fit():
    R = ref_feats()
    x0 = np.array([T.RUMBLE["decay"], T.RUMBLE["drive_db"], T.RUMBLE["lpf"], T.RUMBLE["duck_db"], T.RUMBLE["release"],
                   T.RUMBLE["curve"], -T.RUMBLE["level_db"]])

    def f(x):
        m, _ = engine(cfg_of(x))
        return score(features(m, 150, t0=2 * 4 * 60 / 150), R)
    xb, fb = C.minimize_log(f, x0, maxiter=150, restarts=2, step=0.3, verbose="rumble")
    print(round(fb, 2), json.dumps({k: round(float(v), 3) for k, v in cfg_of(xb).items()}), flush=True)


def check():
    R = ref_feats()
    out = {"refs": [dict(id=r["id"], bpm=round(r["bpm"], 1), beats=r["n_beats"], between_db=round(r["between"], 1),
                         pump=np.round(r["pump"], 1).tolist()) for r in R]}
    med_pump = np.median([r["pump"] for r in R], 0)
    med_spec = np.median([r["spec"] for r in R], 0)
    out["refs_median"] = dict(pump=np.round(med_pump, 1).tolist(), spec=dict(zip(map(str, LOW), np.round(med_spec, 1).tolist())),
                              between_db=round(float(np.median([r["between"] for r in R])), 1))
    cases = {"NEW: hardkick + rumble (defaults)": {}, "hardkick alone (no rumble)": None,
             "old: the parts by hand (reverb return size 1, asym, lpf 150, follower duck)": "old"}
    for label, cfg in cases.items():
        if cfg == "old":
            m, _ = old_parts()
        else:
            m, _ = engine(cfg)
        F = features(m, 150, t0=2 * 4 * 60 / 150)
        out[label] = dict(score_db=round(score(F, R), 2), between_db=round(F["between"], 1),
                          pump_rms_db=round(float(np.sqrt(np.mean((F["pump"] - med_pump) ** 2))), 2),
                          spec_rms_db=round(float(np.sqrt(np.mean((F["spec"] - med_spec) ** 2))), 2),
                          pump=np.round(F["pump"], 1).tolist(), spec=dict(zip(map(str, LOW), np.round(F["spec"], 1).tolist())))
        print(f"{label:70s} score {out[label]['score_db']:5.2f}  pump RMS {out[label]['pump_rms_db']:5.2f}  spectrum RMS "
              f"{out[label]['spec_rms_db']:5.2f}  between {out[label]['between_db']:6.1f} (refs {out['refs_median']['between_db']})")
    json.dump(out, open(os.path.join(C.HERE, "rumble-numbers.json"), "w"), indent=1)


def old_parts():
    """What a producer could build before this pass (docs/TECHNO.md 'Engine mapping', the rumble row): the kick sent to
    a named reverb return (size 1, 100% wet, mono), asym distortion and a 48 dB/oct low-pass at 150 Hz in its fx, ducked
    by a level follower on the kick."""
    tr = {"preset": "hardkick", "inst": {"note": "A1"}, "sends": {"rum": 1.0}}
    ret = {"rum": {"type": "reverb", "size": 1.0, "damping": 0.3, "width": 0, "hpf": 30, "lpf": 0,
                   "fx": [{"type": "asym", "amount": 0.7, "bias": 0.2}, {"type": "lpf", "hz": 150},
                          {"type": "lpf", "hz": 150}, {"type": "lpf", "hz": 150}],
                   "duck": {"key": "kick", "depth_db": 12, "attack_ms": 5, "release_ms": 250}, "return_db": 0}}
    P = C.project({"kick": tr}, {"p": {"bars": 1, "kick": "x...x...x...x..."}}, 8, bpm=150, returns=ret)
    st = C.stems(P)
    return st["kick"].mean(0) + st["(rum)"].mean(0), st


if __name__ == "__main__":
    fit() if sys.argv[1:2] == ["fit"] else check()
