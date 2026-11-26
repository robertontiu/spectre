#!/usr/bin/env python3
"""A/Bs of the techno sounds (2026-11-26; README.md here): A = what the engine could do before (the parts by hand, the
old stand-ins), B = the fitted sound, same notes and patterns. 150 bpm, 8 bars (about 14 s with the tail; the
excerpt 16 bars), through the engine's quick master (both at -10.5 LUFS integrated: loudness-matched), 192 kbps MP3,
mel spectrograms (<case>.png, A left, B right), numbers.json (per case: the changed stem's descriptors from
examples/production/dubstep-v2/describe.py for A and B, and the whole excerpt's band shares and short-term loudness).

    bash tools/remix/waitfree.sh render && python3 examples/production/techno/build.py [case ...]   # ~4 minutes

Writes only into this folder (temporary files in a removed temp folder)."""
import copy
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
sys.path.insert(0, os.path.join(C.HERE, "..", "dubstep-v2"))
import describe as DS  # noqa: E402

SR = C.SR
KEYS = [("groups_db", "sub <60"), ("groups_db", "low 60-150"), ("groups_db", "lowmid 150-500"),
        ("groups_db", "mid 500-2k"), ("groups_db", "pres 2-5k"), ("groups_db", "air 5-16k"), ("centroid_hz", None),
        ("crest_db", None), ("decay20_ms", "low"), ("decay20_ms", "mid"), ("decay20_ms", "high"), ("lufs_m_max", None)]


def T(inst, role, **kw):
    return dict({"inst": inst, "role": role, "humanize_ms": 0, "vel_jitter": 0.02}, **kw)


def proj(tracks, patterns, bars, returns=None, buses=None):
    return {"title": "demo", "bpm": 150, "swing": 0.5, "seed": 11, "seeds": "per-track", "genre": "techno",
            "tracks": tracks, "patterns": patterns, "arrangement": [{"name": "a", "bars": bars, "play": list(patterns)}],
            "buses": buses or {}, "mix": {"reverb": {"size": 0.5, "return_db": -12}, "returns": returns or {}},
            "master": {"lufs": -10.5}}


FOUR = "x...x...x...x..."
HATS_OLD = {"hat": T({"type": "metalhat"}, "hats"), "ohat": T({"type": "metalhat", "open": True}, "hats", choke_by="hat")}
HATS_NEW = {"hat": T({"type": "hat909"}, "hats"), "ohat": T({"type": "openhat909", "decay": 0.16}, "hats", choke_by="hat")}
HATPAT = {"hat": ".xxx.xxx.xxx.xxx", "ohat": "..x...x...x...x."}
OLD_KICK = {"role": "kick", "humanize_ms": 0, "vel_jitter": 0.02,
            "layers": [{"name": "body", "inst": {"type": "kicksub", "note": "A1", "punch": 24, "drop": 0.015, "drive": 0.6,
                                                  "tail": 0.08}, "role": "kick", "eq": {"own_db": 0, "cut_db": 0}},
                       {"name": "punch", "inst": {"type": "kickpunch"}, "role": "kick", "gain_db": -6},
                       {"name": "click", "inst": {"type": "kickclick"}, "role": "kick", "gain_db": -6}],
            "fx": [{"type": "asym", "amount": 0.5, "bias": 0.2}, {"type": "hardclip", "drive_db": 6},
                   {"type": "transient", "attack_db": 4}]}
NEW_KICK = {"preset": "hardkick", "inst": {"note": "A1"}}
OLD_RUMBLE = {"type": "reverb", "size": 1.0, "damping": 0.3, "width": 0, "hpf": 30, "lpf": 0,
              "fx": [{"type": "asym", "amount": 0.7, "bias": 0.2}, {"type": "lpf", "hz": 150}, {"type": "lpf", "hz": 150},
                     {"type": "lpf", "hz": 150}],
              "duck": {"key": "kick", "depth_db": 12, "attack_ms": 5, "release_ms": 250}, "return_db": 0}
OLD_HOOVER = T({"type": "polysynth", "osc": [{"shape": "pulse", "voices": 3, "detune": 25, "pw": 0.3, "spread": 0.8},
                                            {"shape": "saw", "voices": 2, "detune": 20, "octave": -1, "level": 0.6}],
                "cutoff": 2500, "lfo": [{"dest": "pw", "rate": 1.0, "depth": 0.15}],
                "env2": {"dest": "pitch", "depth": -400, "decay": 0.1}}, "lead", eq="auto", fx=[{"type": "chorus"}])
NEW_HOOVER = {"preset": "hoover"}
ACID = T({"type": "acid", "cutoff": 700, "reso": 0.8, "env_mod": 0.6, "decay": 0.2, "drive": 0.6}, "bass", eq="auto",
         vel_jitter=0, fx=[{"type": "asym", "amount": 0.4, "bias": 0.2}, {"type": "hpf", "hz": 150}],
         sidechain={"source": "kick", "depth": 0.4, "release_ms": 100})
ACIDLINE = "0:A1:1 2:A2:1! 3:A1:1 6:C2:1~ 7:A1:1 8:A1:1! 10:E2:1 12:A1:1 14:G2:1!"
PERC_OLD = {"conga": T({"type": "darbuka", "stroke": "doum", "tune": 2.0}, "perc", swing=0.54, humanize_ms=4),
            "bongo": T({"type": "darbuka", "stroke": "tek"}, "perc", swing=0.54, humanize_ms=4, pan=0.3),
            "slap": T({"type": "darbuka", "stroke": "slap"}, "perc", swing=0.54, humanize_ms=4, pan=-0.2),
            "tom": T({"type": "tom"}, "perc", swing=0.54), "rim": T({"type": "rim"}, "perc", swing=0.54)}
PERC_NEW = {"conga": T({"type": "conga"}, "perc", swing=0.54, humanize_ms=4),
            "bongo": T({"type": "bongo"}, "perc", swing=0.54, humanize_ms=4, pan=0.3),
            "slap": T({"type": "conga", "stroke": "slap"}, "perc", swing=0.54, humanize_ms=4, pan=-0.2),
            "tom": T({"type": "tom909", "pitch": "low"}, "perc", swing=0.54), "rim": T({"type": "rim909"}, "perc", swing=0.54)}
PERCPAT = {"conga": "x..x..x...x..x..", "bongo": "..x...x.x...x..x", "slap": "......x.......x.", "rim": "...x.....x...x.."}


def case_rumble():
    A = proj({"kick": dict(NEW_KICK, sends={"rumble": 1.0}), **copy.deepcopy(HATS_NEW)}, {"k": {"kick": FOUR, **HATPAT}},
             8, returns={"rumble": OLD_RUMBLE})
    B = proj({"kick": dict(NEW_KICK, rumble=True), **copy.deepcopy(HATS_NEW)}, {"k": {"kick": FOUR, **HATPAT}}, 8)
    return A, B, ["(rumble)"], "the kick's rumble: the parts by hand (reverb return size 1, asym, a 150 Hz low-pass, follower duck) against the fitted `rumble`; same hardkick, same hats"


def case_hardkick():
    A = proj({"kick": copy.deepcopy(OLD_KICK), **copy.deepcopy(HATS_NEW)}, {"k": {"kick": FOUR, **HATPAT}}, 8)
    B = proj({"kick": copy.deepcopy(NEW_KICK), **copy.deepcopy(HATS_NEW)}, {"k": {"kick": FOUR, **HATPAT}}, 8)
    return A, B, ["kick"], "the hard kick: kicksub + kickpunch + kickclick through asym, hard clip and transient (TECHNO.md's workaround) against `hardkick`"


def case_kick909():
    A = proj({"kick": T({"type": "clubkick"}, "kick")}, {"k": {"kick": FOUR}}, 8)
    B = proj({"kick": T({"type": "kick909"}, "kick")}, {"k": {"kick": FOUR}}, 8)
    return A, B, ["kick"], "the 909 kick: `clubkick` (909 lineage) against `kick909`"


def case_hats909():
    k = {"kick": T({"type": "kick909"}, "kick")}
    A = proj(dict(k, **copy.deepcopy(HATS_OLD)), {"k": {"kick": FOUR, **HATPAT}}, 8)
    B = proj(dict(k, **copy.deepcopy(HATS_NEW)), {"k": {"kick": FOUR, **HATPAT}}, 8)
    return A, B, ["hat", "ohat"], "909 hats: `metalhat` closed and open (808 tones) against `hat909` and `openhat909`, over `kick909`"


def case_groove():
    base = {"kick": T({"type": "kick909"}, "kick"), **copy.deepcopy(HATS_NEW)}
    pats = lambda: {"k": {"kick": FOUR, **HATPAT}, "p": dict(PERCPAT), "t3": {"bars": 0.1875, "free": True, "tom": "x.."}}  # noqa: E731
    A = proj(dict(base, **copy.deepcopy(PERC_OLD)), pats(), 8)
    B = proj(dict(base, **copy.deepcopy(PERC_NEW)), pats(), 8)
    for P in (A, B):
        P["patterns"]["k"]["bars"] = 1
        P["patterns"]["p"]["bars"] = 1
    return A, B, ["conga", "bongo", "slap", "tom", "rim"], "hard-groove percussion: darbuka, tom, rim stand-ins against `conga`, `bongo` (open and slap), `tom909`, `rim909`; the tom on a free-running 3-step loop over the 4/4"


def case_hoover():
    line = "0:A3:6 8:A3:2 16:G3:6 24:C4:4"
    k = {"kick": T({"type": "kick909"}, "kick")}
    A = proj(dict(k, lead=copy.deepcopy(OLD_HOOVER)), {"k": {"kick": FOUR}, "h": {"bars": 2, "lead": line}}, 8)
    B = proj(dict(k, lead=copy.deepcopy(NEW_HOOVER)), {"k": {"kick": FOUR}, "h": {"bars": 2, "lead": line}}, 8)
    return A, B, ["lead"], "the hoover: a polysynth patch by hand (PWM pulses, a pitch envelope, chorus) against the `hoover` preset"


def excerpt(new):
    tr = {"kick": copy.deepcopy(NEW_KICK if new else OLD_KICK), **copy.deepcopy(HATS_NEW if new else HATS_OLD),
          "clap": T({"type": "clap909"}, "clap", gain_db=-2), **copy.deepcopy(PERC_NEW if new else PERC_OLD),
          "acid": copy.deepcopy(ACID), "lead": copy.deepcopy(NEW_HOOVER if new else OLD_HOOVER)}
    rets = {}
    if new:
        tr["kick"]["rumble"] = True
    else:
        tr["kick"]["sends"] = {"rumble": 1.0}
        rets["rumble"] = copy.deepcopy(OLD_RUMBLE)
    for k in ("hat", "ohat", "clap", "conga", "bongo", "slap", "tom", "rim"):
        tr[k]["bus"] = "drums" if k in ("hat", "ohat", "clap") else "perc"
    tr["kick"]["bus"] = "drums"
    buses = {"drums": {"fx": [{"type": "clip", "drive_db": 2, "ceiling_db": -1}]},
             "perc": {"fx": [{"type": "sat", "amount": 0.3}, {"type": "hpf", "hz": 80}], "gain_db": -3}}
    pats = {"k": {"kick": FOUR, **HATPAT, "clap": "....x.......x..."}, "p": dict(PERCPAT, bars=1),
            "t3": {"bars": 0.1875, "free": True, "tom": "x.."}, "a": {"acid": ACIDLINE},
            "h": {"bars": 2, "lead": "0:A3:6 8:A3:2 16:G3:6 24:C4:4"}}
    P = proj(tr, pats, 16, returns=rets, buses=buses)
    P["tracks"]["lead"]["gain_db"] = -4
    P["arrangement"] = [{"name": "drive", "bars": 8, "play": ["k", "p", "t3", "a"],
                         "auto": {"acid": {"inst": {"cutoff": [500, 1500]}}}},
                        {"name": "fury", "bars": 8, "play": ["k", "p", "t3", "a", "h"],
                         "auto": {"acid": {"inst": {"cutoff": [1500, 2500], "reso": [0.8, 0.9]}}}}]
    return P


def case_excerpt():
    return excerpt(False), excerpt(True), ["kick", "(rumble)", "lead"], "a 16-bar hard-techno excerpt at 150 bpm with everything together: the old stand-ins (A) against the fitted sounds (B); same acid, clap and patterns"


CASES = {"rumble": case_rumble, "hardkick": case_hardkick, "kick909": case_kick909, "hats909": case_hats909,
         "groove": case_groove, "hoover": case_hoover, "excerpt": case_excerpt}


def mp3(x, path):
    import soundfile as sf
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "x.wav")
        sf.write(w, x.T, SR, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "192k", path], check=True)


def picture(name, a, b, path, title):
    import librosa
    import librosa.display
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.6), sharey=True)
    for ax, x, lab in ((axs[0], a, "A (before)"), (axs[1], b, "B (fitted)")):
        M = librosa.feature.melspectrogram(y=x.mean(0), sr=SR, n_fft=2048, hop_length=512, n_mels=128, fmax=18000)
        librosa.display.specshow(librosa.power_to_db(M + 1e-10, ref=np.max), sr=SR, hop_length=512, y_axis="mel",
                                 x_axis="time", fmax=18000, ax=ax, cmap="magma", vmin=-80)
        ax.set_title(f"{name} {lab}", fontsize=10)
    fig.suptitle(title, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)


def whole(x):
    import pyloudnorm as pyln
    import master as M
    d = DS.describe(x, 150, True)
    st = M.short_term_lufs(x.astype(np.float64), pyln.Meter(SR))
    return dict(groups_db=d["groups_db"], centroid_hz=d["centroid_hz"],
                short_term_max=round(float(np.max(st)), 1), short_term_median=round(float(np.median(st)), 1),
                integrated=round(float(pyln.Meter(SR).integrated_loudness(x.T)), 1))


def main():
    import studio as ST
    names = sys.argv[1:] or list(CASES)
    npath = os.path.join(C.HERE, "numbers.json")
    numbers = json.load(open(npath)) if os.path.exists(npath) else {}
    for name in names:
        A, B, stem_names, desc = CASES[name]()
        outs, stems = [], []
        for P in (A, B):
            st = {}
            mix, meta = ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.copy()), quiet=True)
            outs.append(mix)
            stems.append(st)
        mp3(outs[0], os.path.join(C.HERE, f"{name}-A.mp3"))
        mp3(outs[1], os.path.join(C.HERE, f"{name}-B.mp3"))
        picture(name, outs[0], outs[1], os.path.join(C.HERE, f"{name}.png"), desc)
        rec = {"what": desc, "A_mix": whole(outs[0]), "B_mix": whole(outs[1])}
        for s in stem_names:
            for lab, stt in (("A", stems[0]), ("B", stems[1])):
                key = s if s in stt else ("(rumble)" if s == "(rumble)" and "(rumble)" in stt else None)
                if key is None:
                    continue
                d = DS.describe(stt[key], 150, s in ("lead", "(rumble)"))
                rec[f"{lab} {s}"] = {(k if not sub else f"{k}[{sub}]"): (d[k][sub] if sub else d[k]) for k, sub in KEYS}
        numbers[name] = rec
        print(name, json.dumps({k: v for k, v in rec.items() if k.endswith("_mix")}), flush=True)
        json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
