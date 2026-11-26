#!/usr/bin/env python3
"""A/Bs of the bass-music tools (2026-11-25; docs/DUBSTEP.md "Engine mapping"; docs/MANUAL.md "Bass music"): for each
new sound, A = the old approximation the research names ("Without it"), B = the new tool, same notes; then a drop
excerpt with the voice, modulation and fx chain together. 140 bpm, 8 bars (13.7 s), through the engine's quick master
(both loudness-matched at -10.5 LUFS, no tonal EQ), 192 kbps MP3, mel spectrograms (<case>.png), numbers.json.

    python3 examples/production/dubstep/build.py            # every case
    python3 examples/production/dubstep/build.py growl      # one

Run tools/remix/waitfree.sh render first. Writes only into this folder (temporary WAVs in a removed temp folder).
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import studio as ST  # noqa: E402

SR = ST.SR
BPM = 140
BAR = 4 * 60 / BPM


def proj(tracks, patterns, arrangement, returns=None, buses=None, seed=5):
    return {"title": "demo", "bpm": BPM, "swing": 0.5, "seed": seed, "seeds": "per-track", "genre": "dubstep",
            "tracks": tracks, "patterns": patterns, "arrangement": arrangement, "buses": buses or {},
            "mix": {"reverb": {"size": 0.6, "return_db": -10}, "returns": returns or {}}, "master": {"lufs": -10.5}}


def T(inst, **kw):
    d = {"inst": inst, "humanize_ms": 0, "vel_jitter": 0}
    d.update(kw)
    return d


KICK = {"role": "kick", "humanize_ms": 0, "vel_jitter": 0.02,
        "layers": [{"name": "sub", "inst": {"type": "kicksub", "note": "F1", "tail": 0.1}, "role": "kick",
                    "eq": {"own_db": 0, "cut_db": 0}},
                   {"name": "click", "inst": {"type": "kickclick", "tone": 3000}, "role": "kick",
                    "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}}]}
DRUMS = {"bars": 1, "kick": "X...............", "snare": "........X......."}
SNARE_OLD = T({"type": "kitsnare", "tune": 200}, role="snare")
SNARE_NEW = T({"type": "snare909", "tune": 200}, role="snare")
LINE = "0:F1:6 8:F1:4 14:Ab1:2 16:F1:6 24:Eb1:8"                     # the 2-bar bass phrase every case plays
LINE_R = "0:F1:6/r=1/8t 8:F1:4/r=1/16 14:Ab1:2/r=1/16 16:F1:6/r=1/8 24:Eb1:8/r=1/4"   # per-note rates
ARR = [{"name": "a", "bars": 8, "play": ["d", "b"]}]
W18T = 1 / (2 / 3 * BAR / 8)                                           # 1/8 triplet in Hz at 140 (7.0)

GROWL = {"type": "fmgrowl", "ops": [{"ratio": 1}, {"ratio": 2, "index": 1.5}, {"ratio": 1, "index": 1.0}],
         "feedback": 0.6, "voices": 3, "detune": 14, "fold": 0.15, "drive": 0.55, "vowel": "oo", "vowel_mix": 0.7,
         "cutoff": 9000, "release": 0.05,
         "mod": [{"dest": "index", "rate": "1/8t", "shape": "tri", "depth": 4.0},
                 {"dest": "vowel", "rate": "1/4", "shape": "saw", "depth": 3.0},
                 {"type": "env", "dest": "pitch", "attack": 0.0, "decay": 0.08, "depth": 7}]}
OLD_WOBBLE = {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 14}], "cutoff": 400, "reso": 0.6,
              "sustain_level": 1.0, "release": 0.05, "lfo": [{"dest": "cutoff", "rate": W18T, "depth": 2.5,
                                                              "shape": "triangle", "phase": "retrig"}]}
OLD_FX = [{"type": "drive", "db": 14}, {"type": "bitcrush", "bits": 8}, {"type": "ott", "depth": 0.4}]
SUB = T({"type": "sub", "harmonics": 0.1}, role="sub", eq="auto", sidechain={"source": "kick", "depth": 0.7, "release_ms": 90})


def two(old_bass, new_bass, extra_tracks=None, line_old=LINE, line_new=LINE_R, returns=None):
    pats_a = {"d": dict(DRUMS), "b": {"bars": 2, "bass": line_old, "sub": LINE}}
    pats_b = {"d": dict(DRUMS), "b": {"bars": 2, "bass": line_new, "sub": LINE}}
    base = {"kick": KICK, "snare": SNARE_NEW, "sub": SUB}
    base.update(extra_tracks or {})
    A = proj(dict(base, bass=old_bass), pats_a, ARR, returns)
    B = proj(dict(base, bass=new_bass), pats_b, ARR, returns)
    return A, B


def case_growl():
    A, B = two(T(OLD_WOBBLE, role="upper-bass", eq="auto", fx=OLD_FX),
               T(GROWL, role="upper-bass", eq="auto", fx=[{"type": "suppress", "depth": 5}]))
    return A, B, ("A: the old approximation (polysynth saws, resonant low-pass wobbled at 7 Hz = 1/8 triplet, drive, "
                  "bitcrush, OTT); B: `fmgrowl` (3 operators, feedback, unison 3), FM index wobbled at 1/8 triplet and the "
                  "vowel swept per beat, per-note rates (r=1/8t, 1/16, 1/8, 1/4), a pitch blip on each note")


def case_mod():
    base = {"type": "polysynth", "osc": [{"shape": "saw", "voices": 2, "detune": 10}, {"shape": "square", "level": 0.5}],
            "cutoff": 300, "reso": 0.5, "sustain_level": 1.0, "release": 0.04}
    a = copy.deepcopy(base)
    a["lfo"] = [{"dest": "cutoff", "rate": W18T, "depth": 3.0, "shape": "triangle", "phase": "retrig"}]
    b = copy.deepcopy(base)
    b["lfo"] = [{"dest": "cutoff", "rate": "1/8t", "depth": 3.0, "shape": "triangle"}]
    A, B = two(T(a, role="upper-bass", eq="auto", fx=[{"type": "drive", "db": 10}]),
               T(b, role="upper-bass", eq="auto", fx=[{"type": "drive", "db": 10}]))
    return A, B, ("A: a polysynth wobble at one rate for the whole phrase (7 Hz typed by hand); B: the same patch with the "
                  "rate as a note value and changed per note: 1/8t, 1/16, 1/16, 1/8, 1/4 (the wobble's rhythm is the riff)")


def case_vowel():
    saw = {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 12}], "sustain_level": 1.0,
           "release": 0.05}
    a = dict(saw, filter="bp", cutoff=700, reso=0.7, lfo=[{"dest": "cutoff", "rate": 1 / (BAR / 4), "depth": 1.5,
                                                        "shape": "saw", "phase": "retrig"}])
    b = dict(saw, filter="none")
    A, B = two(T(a, role="upper-bass", eq="auto", fx=[{"type": "drive", "db": 8}]),
               T(b, role="upper-bass", eq="auto", fx=[{"type": "vowel", "vowel": "oo", "rate": "1/4", "shape": "tri",
                                                         "depth": 4, "q": 1.2}, {"type": "drive", "db": 8}]),
               line_new=LINE)
    return A, B, ("A: one band-pass with resonance whose cutoff is swept each beat (a filter sweep); B: the `vowel` "
                  "formant filter swept oo-oh-ah-eh-ee each beat (three formants, Peterson & Barney): the bass 'talks'")


def case_wavetable():
    a = {"type": "polysynth", "osc": [{"shape": "pulse", "voices": 3, "detune": 18, "pw": 0.5}], "cutoff": 3000,
         "sustain_level": 1.0, "release": 0.05,
         "lfo": [{"dest": "pw", "rate": 1 / (2 * BAR), "depth": 0.4, "shape": "triangle", "phase": "retrig"}]}
    b = {"type": "wavetable", "table": "vocal", "pos": 0.1, "voices": 3, "detune": 18, "cutoff": 6000, "drive": 0.3,
         "mod": [{"dest": "pos", "rate": "1/2", "shape": "tri", "depth": 0.85}]}
    A, B = two(T(a, role="upper-bass", eq="auto", fx=[{"type": "drive", "db": 6}]),
               T(b, role="upper-bass", eq="auto"), line_new=LINE)
    return A, B, ("A: pulse-width modulation, the closest the old engine had; B: `wavetable` on the 'vocal' table, its "
                  "position swept over half a bar and back (a neuro-style morph)")


def case_resample():
    grow = T(GROWL, role="upper-bass", eq="auto")
    pats = {"d": dict(DRUMS), "b": {"bars": 2, "bass": LINE_R, "sub": LINE}}
    A = proj({"kick": KICK, "snare": SNARE_NEW, "sub": SUB, "bass": grow}, pats, ARR)
    chops = T({"type": "sampler", "source": "src", "from_bar": 1, "bars": 1, "mode": "slice", "slices": 8},
              role="upper-bass", eq="auto")
    rev = T({"type": "sampler", "source": "src", "from_bar": 2, "bars": 1, "reverse": True, "root": "F2"},
            role="upper-bass", eq="auto", gain_db=-4)
    src = dict(grow, mute=True)
    patsB = {"d": dict(DRUMS), "s": {"bars": 2, "src": LINE_R},
             "b": {"bars": 2, "sub": LINE, "chops": "0:C3:2 2:D3:1 3:D3:1 4:F3:2 6:C3:2 8:G3:2 10:A3:1 11:A3:1 12:B3:2 14:E3:2 "
                   "16:C3:2 18:D3:1 19:D3:1 20:F3:2 22:C3:2", "rev": "24:F2:4 28:C2:4"}}
    arrB = [{"name": "a", "bars": 8, "play": ["d", "b", "s"]}]
    B = proj({"kick": KICK, "snare": SNARE_NEW, "sub": SUB, "src": src, "chops": chops, "rev": rev}, patsB, arrB)
    return A, B, ("A: the growl phrase played live; B: the same growl printed (muted source) and played back by "
                  "`sampler`s: its first bar cut into 8 slices re-sequenced as 16ths, and its second bar reversed and "
                  "pitched down a fifth and an octave at the end of the phrase")


def case_multiband():
    a = copy.deepcopy(GROWL)
    a.update(fold=0.0, drive=0.0)
    A, B = two(T(a, role="upper-bass", fx=[{"type": "hpf", "hz": 40}, {"type": "drive", "db": 18},
                                           {"type": "ott", "depth": 0.5}]),
               T(a, role="upper-bass", fx=[{"type": "hpf", "hz": 40},
                                            {"type": "multiband", "split": [150, 2500],
                                             "bands": [[{"type": "comp", "threshold_db": -18, "ratio": 3}],
                                                       [{"type": "fold", "amount": 0.5}, {"type": "ott", "depth": 0.5}],
                                                       [{"type": "hardclip", "drive_db": 12}]],
                                             "widths": [0, 1.0, 1.4]}]))
    return A, B, ("A: one distortion over the whole growl (drive 18 dB, OTT): the low end distorts with the top; B: "
                  "`multiband`: below 150 Hz compressed, clean and mono; 150 Hz-2.5 kHz folded and OTT; above 2.5 kHz "
                  "hard-clipped and widened")


def case_dist():
    a = copy.deepcopy(GROWL)
    a.update(fold=0.0, drive=0.0, vowel=None)
    a["mod"] = a["mod"][:1]
    A, B = two(T(a, role="upper-bass", eq="auto", fx=[{"type": "drive", "db": 16}]),
               T(a, role="upper-bass", eq="auto", fx=[{"type": "fold", "amount": 0.45}, {"type": "asym", "amount": 0.5,
                                                                                         "bias": 0.3},
                                                       {"type": "hardclip", "drive_db": 6}]))
    return A, B, ("A: the old `drive` (tanh, odd harmonics); B: wavefolder, then asymmetric saturation (even "
                  "harmonics), then a hard clip")


def case_comb():
    a = copy.deepcopy(GROWL)
    a.update(vowel=None)
    A, B = two(T(a, role="upper-bass", eq="auto", fx=[{"type": "chorus", "rate": 0.8, "mix": 0.4}]),
               T(a, role="upper-bass", eq="auto", fx=[{"type": "comb", "note": "F4", "feedback": 0.85, "depth": 0.3,
                                                       "rate": "1/8", "mix": 0.6},
                                                      {"type": "flanger", "rate": "1/2", "feedback": 0.6, "mix": 0.4}]))
    return A, B, ("A: the old `chorus`; B: a comb tuned to F4 (feedback 0.85, its delay swept every 8th: metallic, "
                  "'screech'), then a flanger on the half bar")


def case_vocoder():
    chords = "0:F2:14 16:Db2:14"
    tr = T({"type": "fmgrowl", "ops": [{"ratio": 1}, {"ratio": 3, "index": 2}], "feedback": 0.3, "drive": 0.5,
            "release": 0.4, "mod": [{"dest": "index", "rate": "1/8", "depth": 3, "shape": "saw"}]}, role="upper-bass",
           eq="auto")
    pats = {"d": dict(DRUMS), "b": {"bars": 2, "bass": chords, "sub": "0:F1:14 16:Db1:14"}}
    A = proj({"kick": KICK, "snare": SNARE_NEW, "sub": SUB, "bass": tr}, pats, ARR)
    trb = copy.deepcopy(tr)
    trb["fx"] = [{"type": "vocoder", "notes": ["F3", "Ab3", "C4", "Eb4"], "mix": 0.7}]
    B = proj({"kick": KICK, "snare": SNARE_NEW, "sub": SUB, "bass": trb}, pats, ARR)
    return A, B, ("colour bass: A a growl on single notes; B the same growl through a `vocoder` whose carrier is "
                  "Fm7 (F, Ab, C, Eb): its movement now rings as a chord")


def case_gatedverb():
    pats = {"d": {"bars": 1, "kick": "X...............", "snare": "........X.......", "hats": "x.x.x.x.x.x.x.x."}}
    arr = [{"name": "a", "bars": 8, "play": ["d"]}]
    sn = T({"type": "snare909", "tune": 200}, role="snare", sends={"verb": 0.6})
    hats = T({"type": "metalhat"}, role="hats", eq="auto")
    A = proj({"kick": KICK, "snare": sn, "hats": hats}, pats, arr, {"verb": {"type": "reverb", "size": 0.8, "return_db": -4}})
    B = proj({"kick": KICK, "snare": sn, "hats": hats}, pats, arr,
             {"verb": {"type": "reverb", "size": 0.8, "return_db": -4, "gate": {"hold_ms": 150, "release_ms": 25}}})
    return A, B, "A: the 909 snare into a long reverb; B: the same reverb gated (`gate`: hold 150 ms, release 25 ms)"


def drop(new):
    """An 8-bar drop: kick, snare (+clap), hats, sub, the lead bass, chops in bars 5-8."""
    if new:
        bass = T(dict(GROWL, vowel_mix=0.6), role="upper-bass", eq="auto", bus="bass",
                 fx=[{"type": "multiband", "split": [180, 2500],
                      "bands": [[], [{"type": "fold", "amount": 0.3}, {"type": "ott", "depth": 0.4}],
                                [{"type": "hardclip", "drive_db": 6}]], "widths": [0, 1.0, 1.3], "gains_db": [0, 0, 3]},
                     {"type": "suppress", "depth": 5}, {"type": "mseq", "side_hpf": 160}])
        sn = T({"type": "snare909", "tune": 200}, role="snare", bus="drums", sends={"verb": 0.4})
        clap = T({"type": "clap909"}, role="clap", bus="drums", gain_db=-3)
        chop = T({"type": "sampler", "source": "bass", "from_bar": 1, "bars": 1, "mode": "slice", "slices": 8},
                 role="upper-bass", eq="auto", bus="bass", gain_db=-3)
        line = LINE_R
        returns = {"verb": {"type": "reverb", "size": 0.6, "return_db": -8, "gate": {"hold_ms": 140, "release_ms": 25}}}
    else:
        bass = T(OLD_WOBBLE, role="upper-bass", eq="auto", bus="bass", fx=OLD_FX)
        sn = T({"type": "kitsnare", "tune": 200}, role="snare", bus="drums", sends={"verb": 0.4})
        clap = T({"type": "handclap"}, role="clap", bus="drums", gain_db=-3)
        chop = T(dict(OLD_WOBBLE, lfo=[{"dest": "cutoff", "rate": 2 * W18T, "depth": 2.5, "phase": "retrig"}]),
                 role="upper-bass", eq="auto", bus="bass", fx=OLD_FX, gain_db=-3)
        line = LINE
        returns = {"verb": {"type": "reverb", "size": 0.6, "return_db": -8}}
    sub = dict(SUB, inst={"type": "sub", "harmonics": 0.35}, gain_db=3) if new else SUB
    tracks = {"kick": dict(KICK, bus="drums"), "snare": sn, "clap": clap,
              "hats": T({"type": "metalhat"}, role="hats", eq="auto", bus="drums"), "sub": sub, "bass": bass,
              "chop": chop}
    pats = {"d": {"bars": 1, "kick": "X.........x.....", "snare": "........X.......", "clap": "........X.......",
                  "hats": "..x...x...x...xx"},
            "b": {"bars": 2, "bass": line, "sub": LINE},
            "c": {"bars": 1, "chop": "0:C3:2 2:D3:1 3:D3:1 4:F3:2 6:C3:2 8:G3:2 10:A3:1 11:A3:1 12:B3:2 14:E3:2"}}
    arr = [{"name": "dropA", "bars": 4, "play": ["d", "b"], "enter": {"impact": 0.8}},
           {"name": "dropB", "bars": 4, "play": ["d", "b", "c"]}]
    buses = {"drums": {"fx": [{"type": "clip", "drive_db": 2, "ceiling_db": -1.5}]},
             "bass": {"fx": [{"type": "comp", "threshold_db": -16, "ratio": 2}, {"type": "clip", "drive_db": 1,
                                                                                    "ceiling_db": -1}],
                      "sidechain": {"source": "kick", "depth": 0.5, "release_ms": 120}}}
    return proj(tracks, pats, arr, returns, buses)


def case_drop():
    return drop(False), drop(True), ("an 8-bar drop. A: the old approximations (polysynth wobble with drive, bitcrush "
                                     "and OTT; kitsnare and handclap; the chops a faster wobble). B: `fmgrowl` with "
                                     "synced per-note mods through `multiband`, `suppress` and `mseq`; `snare909` and "
                                     "`clap909` into a gated reverb; chops by `sampler` from the growl")


CASES = {"growl": case_growl, "mod": case_mod, "vowel": case_vowel, "wavetable": case_wavetable,
         "resample": case_resample, "multiband": case_multiband, "dist": case_dist, "comb": case_comb,
         "vocoder": case_vocoder, "gatedverb": case_gatedverb, "drop": case_drop}


# ------------------------------------------------------------------ measurements

def band_db(x, lo, hi):
    X = np.abs(np.fft.rfft(np.asarray(x, dtype=np.float64))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return float(10 * np.log10(X[(f >= lo) & (f < hi)].sum() + 1e-20))


def mod_rate(x, lo=300, hi=6000):
    """The rate (Hz) at which the band's level moves: the first autocorrelation peak of its dB envelope (5 ms frames)
    between 1/14 and 1/1.5 s, refined by parabolic interpolation."""
    from scipy import signal
    y = signal.sosfilt(signal.butter(4, [lo, hi], btype="band", fs=SR, output="sos"), x)
    h = 220
    e = np.sqrt(np.convolve(y ** 2, np.ones(h) / h, mode="same")[::h])
    e = 20 * np.log10(e + 1e-9)
    e = e - e.mean()
    ac = np.correlate(e, e, "full")[len(e) - 1:]
    fps = SR / h
    a0, a1 = int(fps / 14), min(int(fps / 1.5), len(ac) - 2)
    pk, _ = signal.find_peaks(ac[a0:a1])
    if not len(pk):
        return None
    k = a0 + pk[np.argmax(ac[a0:a1][pk])]
    d = 0.5 * (ac[k - 1] - ac[k + 1]) / (ac[k - 1] - 2 * ac[k] + ac[k + 1] + 1e-12)
    return round(float(fps / (k + d)), 2)


def measure(name, a, b, stems_a, stems_b):
    m = {}
    if name in ("growl", "mod"):
        for k, st in (("A", stems_a), ("B", stems_b)):
            x = st["bass"]
            m[f"{k} bass stem, the notes at steps 0, 8, 16, 24 of each phrase: wobble rate (Hz), median of 4 phrases "
              f"(B asks 1/8t = 7.0, 1/16 = 9.33, 1/8 = 4.67, 1/4 = 2.33)"] = [
                round(float(np.median([mod_rate(x[int((ph * 2 * BAR + s0 * BAR / 16) * SR):
                                            int((ph * 2 * BAR + s1 * BAR / 16) * SR)]) or 0 for ph in range(4)])), 2)
                for s0, s1 in ((0, 6), (8, 12), (16, 22), (24, 32))]
    if name == "multiband":
        for k, st in (("A", stems_a), ("B", stems_b)):
            x = st["bass"]
            m[f"{k} bass stem: 40-150 Hz energy against 150 Hz-2.5 kHz, dB"] = round(band_db(x, 40, 150) - band_db(x, 150, 2500), 1)
            m[f"{k} bass stem: the F1 fundamental band (40-50 Hz) against 50-150 Hz (distortion products under the "
              f"crossover), dB"] = round(band_db(x, 40, 50) - band_db(x, 50, 150), 1)
    if name == "vocoder":
        from hand import note_to_midi, midi_to_hz
        for k, st in (("A", stems_a), ("B", stems_b)):
            x = np.concatenate([st["bass"][int(ph * 2 * BAR * SR):int((ph * 2 + 1) * BAR * SR)] for ph in range(4)])
            tot = band_db(x, 150, 1500)
            # Ab and Eb are not harmonics of the F2 the growl plays: energy there comes from the resonator
            share = 10 * np.log10(sum(10 ** (band_db(x, midi_to_hz(note_to_midi(nt)) * 2 ** -(1 / 24),
                                                     midi_to_hz(note_to_midi(nt)) * 2 ** (1 / 24)) / 10)
                                      for nt in ("Ab3", "Eb4", "Ab4")) + 1e-20) - tot
            m[f"{k} F2 bars: energy within a quarter tone of Ab3, Eb4, Ab4 (not harmonics of F2) against 150-1500 Hz, dB"] = \
                round(float(share), 1)
    if name == "gatedverb":
        for k, st in (("A", stems_a), ("B", stems_b)):
            x = st["(verb)"]
            k16 = int(BAR / 16 * SR)
            hit = [x[int((b0 * BAR + BAR / 2) * SR) + i * k16:int((b0 * BAR + BAR / 2) * SR) + (i + 1) * k16]
                   for b0 in range(1, 7) for i in range(8)]
            lv = [20 * np.log10(np.sqrt(np.mean(np.concatenate([hit[j * 8 + i] for j in range(6)]) ** 2)) + 1e-12)
                  for i in range(8)]
            m[f"{k} reverb return after each snare, per 16th (dB re the first)"] = [round(float(v - lv[0]), 1) for v in lv]
    if name == "drop":
        T_ = json.load(open(os.path.join(REPO, "engine", "targets.json")))["dubstep_2015"]
        for k, x in (("A", a), ("B", b)):
            X = np.abs(np.fft.rfft(x.mean(0))) ** 2
            f = np.fft.rfftfreq(x.shape[1], 1 / SR)
            cs = np.array([float(h) for h in T_["curve"]])
            tgt = np.array(list(T_["curve"].values()), dtype=float)
            mine = np.array([10 * np.log10(X[(f >= c * 2 ** -(1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in cs])
            mine -= mine[np.argmin(np.abs(cs - 1000))]
            sel = (cs >= 31) & (cs <= 16000)
            dev = mine[sel] - tgt[sel]
            m[f"{k} 1/3-octave balance against dubstep_2015 (re 1 kHz): RMS dB, and 31.5-80 / 100-250 / 2-5k / 8-12.5k"] = [
                round(float(np.sqrt(np.mean(dev ** 2))), 1),
                round(float(dev[(cs[sel] >= 31) & (cs[sel] <= 80)].mean()), 1),
                round(float(dev[(cs[sel] >= 100) & (cs[sel] <= 250)].mean()), 1),
                round(float(dev[(cs[sel] >= 2000) & (cs[sel] <= 5000)].mean()), 1),
                round(float(dev[(cs[sel] >= 8000) & (cs[sel] <= 12500)].mean()), 1)]
    return m


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


def main():
    names = sys.argv[1:] or list(CASES)
    npath = os.path.join(HERE, "numbers.json")
    numbers = json.load(open(npath)) if os.path.exists(npath) else {}
    for name in names:
        A, B, desc = CASES[name]()
        outs, stems = [], []
        for P in (A, B):
            st = {}
            mix, meta = ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.mean(0).copy()))
            n = int(min(meta["duration"] + 0.4, mix.shape[1] / SR) * SR)
            x = mix[:, :n].copy()
            fo = int(0.3 * SR)
            x[:, -fo:] *= np.linspace(1, 0, fo)
            outs.append(x)
            stems.append(st)
        a, b = outs
        mp3(a, os.path.join(HERE, f"{name}-A.mp3"))
        mp3(b, os.path.join(HERE, f"{name}-B.mp3"))
        picture(name, a, b, os.path.join(HERE, f"{name}.png"), desc)
        numbers[name] = dict(what=desc, **measure(name, a, b, stems[0], stems[1]))
        print(name, json.dumps(numbers[name], indent=1), flush=True)
        json.dump(numbers, open(npath, "w"), indent=1)


if __name__ == "__main__":
    main()
