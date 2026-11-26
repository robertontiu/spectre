#!/usr/bin/env python3
"""A/Bs of the fitted bass-music sounds (2026-11-26, second pass; README.md here): A = the engine's sound before this
pass (the first dubstep A/B, session 017 "Captive"), B = the fitted preset or the "fx_model": 2 transition, same
notes. 140 bpm, through the engine's quick master (both at -10.5 LUFS, no tonal EQ), 192 kbps MP3, mel spectrograms
(<case>.png, A left, B right), numbers.json (the changed stem's descriptors for A and B beside the references' median,
from refs-numbers.json; reference audio is never published).

    bash tools/remix/waitfree.sh render && python3 examples/production/dubstep-v2/build.py [case ...]   # ~3 minutes

The "drop" case also masters both versions with `--genre dubstep --lufs -8.5` (as 017 was) for the drop's short-term
loudness: run tools/remix/waitfree.sh master before it. Writes only into this folder (temporary files in a removed
temp folder).
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import describe as DS  # noqa: E402
import sounds as SO  # noqa: E402

ST, DB, P17 = SO.ST, SO.DB, SO.P17
SR, BAR = SO.SR, SO.BAR
KEYS = [("groups150_db", "pres 2-5k"), ("groups150_db", "air 5-16k"), ("groups150_db", "lowmid 150-500"),
        ("centroid_hz", None), ("centroid_move_oct", None), ("flatness", None), ("crest_db", None),
        ("decay20_ms", "low"), ("decay20_ms", "high"), ("side_mid_db", "150-1k"), ("side_mid_db", ">5k"),
        ("lufs_m_max", None)]


def proj(tracks, patterns, arrangement, returns=None, buses=None, fx_model=None):
    P = {"title": "demo", "bpm": 140, "swing": 0.5, "seed": 5, "seeds": "per-track", "genre": "dubstep",
         "tracks": tracks, "patterns": patterns, "arrangement": arrangement, "buses": buses or {},
         "mix": {"reverb": {"size": 0.6, "return_db": -10}, "returns": returns or {}}, "master": {"lufs": -10.5}}
    if fx_model:
        P["fx_model"] = fx_model
    return P


def t17(name, keep=("bus",)):
    tr = copy.deepcopy(P17["tracks"][name])
    for k in ("sends", "sidechain", "bus"):
        if k not in keep:
            tr.pop(k, None)
    return tr


def drums17():
    return {"kick": t17("kick", ()), "snare": t17("snare", ()), "hats": t17("hats", ())}


def drums_new():
    return {"kick": {"preset": "kick"}, "snare": {"preset": "snare"}, "hats": {"preset": "hats"}}


def sub17():
    s = t17("sub", ())
    s["sidechain"] = {"source": "kick", "depth": 0.75, "release_ms": 110}
    return s


def bass_case(old, new, pats_bass, drum_pat, bars, sub_line=None):
    def P(bass):
        tr = dict(drums17(), sub=sub17(), bass=bass)
        pats = {"d": dict(drum_pat), "b": dict(pats_bass)}
        if sub_line:
            pats["b"]["sub"] = sub_line
        return proj(tr, pats, [{"name": "a", "bars": bars, "play": ["d", "b"]}])
    return P(old), P(new), "bass"


def case_growl():
    line = P17["patterns"]["d1A"]["captor"]
    A, B, s = bass_case(t17("captor", ()), {"preset": "growl"}, {"bars": 4, "bass": line}, P17["patterns"]["dA"], 8,
                        P17["patterns"]["d1A"]["sub"])
    return A, B, s, "growl", ("A: session 017's captor (four fmgrowl layers, multiband fold/OTT/clip); B: the `growl` "
                              "preset on the same notes (drop 1A, F#1/G1, per-note rates); 017's kick, snare, hats, sub")


def case_riddim():
    A, B, s = bass_case(t17("husk", ()), {"preset": "riddim"}, {"bars": 2, "bass": P17["patterns"]["d2"]["husk"]},
                        P17["patterns"]["dR"], 8, P17["patterns"]["d2"]["sub"])
    return A, B, s, "riddim", "A: session 017's husk (drop 2); B: the `riddim` preset, same notes and drums"


def case_wobble():
    wob = copy.deepcopy(DB.OLD_WOBBLE)
    A, B, s = bass_case(DB.T(wob, role="upper-bass", eq="auto", fx=DB.OLD_FX), {"preset": "wobble"},
                        {"bars": 2, "bass": DB.LINE}, P17["patterns"]["dA"], 8, DB.LINE)
    return A, B, s, "wobble", ("A: the old wobble (polysynth saws, resonant low-pass LFO at 1/8 triplet, drive, "
                               "bitcrush, OTT); B: the `wobble` preset (1/8, asym, OTT, clip, fitted tone)")


def case_reese():
    reese = {"type": "polysynth", "osc": [{"shape": "saw", "voices": 2, "detune": 25},
                                          {"shape": "saw", "voices": 2, "detune": 9}],
             "cutoff": 2500, "sustain_level": 1, "release": 0.1, "lfo": [{"dest": "detune", "rate": "1/16d", "depth": 0.3}]}
    line = "0:F1:14 16:F1:6 24:Ab1:8 32:Eb1:14 48:F1:16"
    A, B, s = bass_case(DB.T(reese, role="upper-bass", eq="auto"), {"preset": "reese"}, {"bars": 4, "bass": line},
                        P17["patterns"]["dA"], 8, line)
    return A, B, s, "reese", ("A: the reese as docs/DUBSTEP.md's mapping builds it (detuned saws, a detune LFO); B: "
                              "the `reese` preset (asym, OTT, mono below 250 Hz, clip, fitted tone)")


def case_screech():
    cb = copy.deepcopy(DB.GROWL)
    cb.update(vowel=None)
    old = DB.T(cb, role="upper-bass", eq="auto", fx=[
        {"type": "comb", "note": "F4", "feedback": 0.85, "depth": 0.3, "rate": "1/8", "mix": 0.6},
        {"type": "flanger", "rate": "1/2", "feedback": 0.6, "mix": 0.4}])
    line = "0:F3:6 8:F3:4 14:Ab3:2 16:F3:6 24:Eb3:8"
    A, B, s = bass_case(old, {"preset": "screech"}, {"bars": 2, "bass": line}, P17["patterns"]["dA"], 8)
    return A, B, s, "screech", ("A: the first A/B's comb screech (growl, comb at F4, flanger); B: the `screech` "
                                "preset (FM 1:3 with feedback, flanger, OTT, clip, fitted tone)")


def case_drums():
    pat = dict(P17["patterns"]["dC"])
    A = proj(drums17(), {"d": pat}, [{"name": "a", "bars": 8, "play": ["d"]}])
    B = proj(drums_new(), {"d": pat}, [{"name": "a", "bars": 8, "play": ["d"]}])
    return A, B, ["kick", "snare", "hats"], "kick,snare,hat", (
        "A: session 017's kick stack (sub on C#2, punch, click), snare stack (909 at 200 Hz + 909 clap) and metalhat; "
        "B: the `kick`, `snare` and `hats` presets; 017's drop 1C pattern, no reverb")


def case_transitions():
    tr = dict(drums17(), sub=sub17())
    pats = {"d": dict(P17["patterns"]["dA"]), "s": {"bars": 1, "sub": "0:F#1:16"}}
    arr = [{"name": "build", "bars": 4, "play": ["s"], "exit": {"riser": 8}},
           {"name": "drop", "bars": 4, "play": ["d", "s"], "enter": {"impact": 0.8}, "exit": {"reverse": 2}},
           {"name": "down", "bars": 2, "play": ["s"], "enter": {"downlifter": 4}}]
    A = proj(copy.deepcopy(tr), pats, arr)
    B = proj(copy.deepcopy(tr), pats, arr, fx_model=2)
    return A, B, "(fx)", "impact,riser,downlifter", (
        "A: the old transitions (mono: noise riser, a 40 Hz sine impact, a reverse cymbal, a noise downlifter); B: "
        "\"fx_model\": 2 (stereo, fitted: a riser with a body, a pitched impact with a room, a downlifter with a "
        "falling tone); a sub and 017's drums for scale")


def drop_project(new):
    """Session 017's build 1b (4 bars) into drop 1A (8 bars), every drop track and both buses as in the session; B
    swaps the captor for the `growl` preset (same notes), kick, snare and hats for the presets, and sets fx_model 2."""
    P = copy.deepcopy(P17)
    keep = {"build1b", "drop1a"}
    P["arrangement"] = [s for s in P["arrangement"] if s["name"] in keep]
    P["master"] = {"lufs": -10.5}
    if new:
        for k in ("kick", "snare", "hats"):
            tr = {"preset": {"hats": "hats"}.get(k, k), "bus": "drums"}
            if k == "snare":
                tr["sends"] = P["tracks"]["snare"].get("sends", {})
            P["tracks"][k] = tr
        cap = P["tracks"]["captor"]
        P["tracks"]["captor"] = {"preset": "growl", "bus": cap["bus"], "sends": cap.get("sends", {})}
        P["fx_model"] = 2
    return P


def case_drop():
    return drop_project(False), drop_project(True), None, None, (
        "session 017: build 1b (4 bars) into drop 1A (8 bars) as published (A) and with the captor, kick, snare and "
        "hats swapped for the fitted presets and fx_model 2 (B); everything else, buses and returns as in 017")


CASES = {"growl": case_growl, "riddim": case_riddim, "wobble": case_wobble, "reese": case_reese,
         "screech": case_screech, "drums": case_drums, "transitions": case_transitions, "drop": case_drop}


def ref_medians(roles):
    D = json.load(open(os.path.join(HERE, "refs-numbers.json")))
    out = {}
    for role in roles:
        R = [r["d"] for r in D["refs"] if r["role"] == role]
        row = {}
        for k, s in KEYS:
            v = [x for x in ((d.get(k) or {}).get(s) if s else d.get(k) for d in R) if isinstance(x, (int, float))]
            if v:
                row[k + (f"[{s}]" if s else "")] = round(float(np.median(v)), 2)
        out[role] = row
    return out


def pick(d):
    return {k + (f"[{s}]" if s else ""): ((d.get(k) or {}).get(s) if s else d.get(k)) for k, s in KEYS}


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
    for ax, x, lab in ((axs[0], a, "A"), (axs[1], b, "B")):
        M = librosa.feature.melspectrogram(y=x.mean(0), sr=SR, n_fft=2048, hop_length=512, n_mels=128, fmax=18000)
        librosa.display.specshow(librosa.power_to_db(M + 1e-10, ref=np.max), sr=SR, hop_length=512, y_axis="mel",
                                 x_axis="time", fmax=18000, ax=ax, cmap="magma", vmin=-80)
        ax.set_title(f"{name} {lab}", fontsize=10)
    fig.suptitle(title, fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)


def drop_numbers(P, mix, stems, meta):
    """The drop through the genre master as 017 was mastered (--genre dubstep --lufs -8.5): its short-term loudness,
    the momentary step into it, its tone against dubstep_2015; the drums' crest and peak against the bass (stems)."""
    import soundfile as sf
    import pyloudnorm as pyln
    sec = {s["name"]: s for s in meta["sections"]}
    a, b = int(sec["drop1a"]["start"] * SR), int(sec["drop1a"]["end"] * SR)
    pre_mix = meta["_premaster"]
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "renders"))
        sf.write(os.path.join(td, "renders", "v001.premaster.wav"), pre_mix.T, SR, subtype="FLOAT")
        json.dump({k: v for k, v in meta.items() if not k.startswith("_")},
                  open(os.path.join(td, "renders", "v001.meta.json"), "w"), default=str)
        json.dump(P, open(os.path.join(td, "renders", "v001.project.json"), "w"))
        json.dump(P, open(os.path.join(td, "project.json"), "w"))
        env = dict(os.environ, BEAT_DIR=td)
        subprocess.run(["bash", os.path.join(SO.REPO, "tools", "remix", "waitfree.sh"), "master"], check=True,
                       capture_output=True)   # a master slot (AGENTS.md rule 7)
        subprocess.run([sys.executable, os.path.join(SO.REPO, "engine", "studio.py"), "master", "v001", "--genre",
                        "dubstep", "--lufs", "-8.5"], cwd=td, env=env, check=True, capture_output=True)
        y, _ = sf.read(os.path.join(td, "renders", "v001.master.wav"), always_2d=True)
    y = y.T
    meter = pyln.Meter(SR)
    st = [meter.integrated_loudness(y[:, i:i + 3 * SR].T) for i in range(a, b - 3 * SR, SR // 10)]
    out = {"genre master (--lufs -8.5, these 12 bars): drop 1A short-term LUFS median / max": [
        round(float(np.median(st)), 1), round(float(np.max(st)), 1)]}
    mom = lambda i: meter.integrated_loudness(y[:, i:i + int(0.4 * SR)].T)
    pre = [mom(i) for i in range(a - 2 * SR, a - int(0.4 * SR), SR // 20)]
    post = [mom(i) for i in range(a, a + 2 * SR, SR // 20)]
    out["momentary loudness: the drop's first 2 s against the build's last 2 s (LU, median)"] = round(
        float(np.median(post) - np.median(pre)), 1)
    T = json.load(open(os.path.join(SO.REPO, "engine", "targets.json")))["dubstep_2015"]
    cs = np.array([float(h) for h in T["curve"]])
    tgt = np.array(list(T["curve"].values()), dtype=float)
    x = y[:, a:b].mean(0)
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mine = np.array([10 * np.log10(X[(f >= c * 2 ** -(1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in cs])
    mine -= mine[np.argmin(np.abs(cs - 1000))]
    dev = mine - tgt
    sel = (cs >= 31) & (cs <= 16000)
    out["drop 1A (mastered) against dubstep_2015, re 1 kHz: RMS dB"] = round(float(np.sqrt(np.mean(dev[sel] ** 2))), 1)
    out["per band (Hz: dB)"] = {str(int(c) if c >= 100 else c): round(float(v), 1) for c, v in zip(cs, dev)}
    bass = sum(stems[k][:, a:b] for k in ("captor", "soul", "chop") if k in stems).mean(0)
    for nm in ("kick", "snare"):
        s = stems[nm][:, a:b].mean(0)
        out[f"{nm} stem in the drop: crest dB"] = round(float(20 * np.log10(np.abs(s).max() / (np.sqrt(np.mean(s ** 2)) + 1e-12))), 1)
        out[f"{nm} stem peak against the bass stems' peak, dB"] = round(float(20 * np.log10(np.abs(s).max() / np.abs(bass).max())), 1)
    return out


def main():
    names = sys.argv[1:] or list(CASES)
    npath = os.path.join(HERE, "numbers.json")
    numbers = json.load(open(npath)) if os.path.exists(npath) else {}
    for name in names:
        A, B, stem_names, roles, desc = CASES[name]()
        outs, stems, metas = [], [], []
        for P in (A, B):
            st = {}
            mix, meta = ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.copy()), quiet=True)
            n = int(min(meta["duration"] + 0.4, mix.shape[1] / SR) * SR)
            x = mix[:, :n].copy()
            fo = int(0.3 * SR)
            x[:, -fo:] *= np.linspace(1, 0, fo)
            outs.append(x)
            stems.append(st)
            metas.append(meta)
        if name == "drop":
            num = {"what": desc}
            for k, P, mix, st, meta in (("A", A, outs[0], stems[0], metas[0]), ("B", B, outs[1], stems[1], metas[1])):
                num[k] = drop_numbers(P, mix, st, meta)
        else:
            rl = roles.split(",")
            num = {"what": desc}
            if name != "transitions":   # the transitions stem holds three effects: compare them one by one in tables.md
                num["reference median"] = ref_medians(rl)
            if isinstance(stem_names, list):
                for k, st in (("A", stems[0]), ("B", stems[1])):
                    num[k] = {nm: pick(DS.describe(st[nm], 140, False)) for nm in stem_names}
            else:
                for k, st in (("A", stems[0]), ("B", stems[1])):
                    num[k] = pick(DS.describe(st[stem_names], 140, name != "transitions"))
        a, b = outs
        mp3(a, os.path.join(HERE, f"{name}-A.mp3"))
        mp3(b, os.path.join(HERE, f"{name}-B.mp3"))
        picture(name, a, b, os.path.join(HERE, f"{name}.png"), desc)
        numbers[name] = num
        print(name, json.dumps(num, indent=1)[:3000], flush=True)
        json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
