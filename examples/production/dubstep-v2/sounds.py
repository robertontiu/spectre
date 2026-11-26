"""The engine's version of each dubstep sound role, as stems: OLD (the 2026-11-25 bass-music tools as the dubstep A/B
and session 017 "Captive" use them) and NEW (the fitted presets of engine/bass_presets.json and the "fx_model": 2
transitions). Used by refs.py (measurement) and fit.py. Renders nothing into any session folder."""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import studio as ST  # noqa: E402
import instruments as I  # noqa: E402
import dubstep2 as D2  # noqa: E402


def _first_ab():
    """The first dubstep A/B module (examples/production/dubstep/build.py: GROWL, OLD_WOBBLE, KICK ...), loaded under
    its own name (this folder has a build.py too)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("dubstep_ab1", os.path.join(REPO, "examples", "production", "dubstep",
                                                                                "build.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


DB = _first_ab()

SR = ST.SR
BPM = 140
BAR = 4 * 60 / BPM
P17 = json.load(open(os.path.join(REPO, "sessions", "017-captive", "project.json")))
NOTES = {"growl": ("0:F#1:16/r=1/8", 1), "riddim": ("0:F#1:16/r=1/8", 1), "wobble": ("0:F#1:32", 2),
         "reese": ("0:F#1:32", 2), "screech": ("0:F#3:16", 1), "snare": ("X...............", 1),
         "clap": ("X...............", 1), "kick": ("X...............", 1), "hats": ("x...............", 1)}
ROLE = {"hats": "hat"}


def proj(tracks, pats, bars, returns=None, fx_model=None):
    P = {"title": "cmp", "bpm": BPM, "swing": 0.5, "seed": 5, "seeds": "per-track", "genre": "dubstep",
         "tracks": tracks, "patterns": pats, "arrangement": [{"name": "a", "bars": bars, "play": list(pats)}],
         "buses": {}, "mix": {"reverb": {"size": 0.6, "return_db": -10}, "returns": returns or {}},
         "master": {"lufs": -10.5}}
    if fx_model:
        P["fx_model"] = fx_model
    return P


def stem(P, name):
    st = {}
    ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.copy()), quiet=True)
    return st[name]


def t17(name):
    tr = copy.deepcopy(P17["tracks"][name])
    for k in ("sends", "sidechain", "bus"):
        tr.pop(k, None)
    return tr


def one(tr, notes, bars=1, name="x"):
    return stem(proj({name: tr}, {"p": {"bars": bars, name: notes}}, bars), name)


def old_sounds():
    """{label: (role, stereo)}: the engine before this pass."""
    S = {}
    S["growl: dubstep A/B GROWL, held F1, 1 bar"] = ("growl", one(DB.T(DB.GROWL, role="upper-bass", eq="auto"), "0:F1:16"))
    S["growl: 017 captor stack, held F#1, 1 bar, r=1/8"] = ("growl", one(t17("captor"), "0:F#1:16/r=1/8"))
    S["growl: 017 captor stack, drop 1A phrase, 4 bars"] = ("growl", one(t17("captor"), P17["patterns"]["d1A"]["captor"], 4))
    S["riddim: 017 husk, drop 2 phrase, 2 bars"] = ("riddim", one(t17("husk"), P17["patterns"]["d2"]["husk"], 2))
    S["riddim: 017 husk, held F#1, 1 bar, r=1/8"] = ("riddim", one(t17("husk"), "0:F#1:16/r=1/8"))
    wob = copy.deepcopy(DB.OLD_WOBBLE)
    wob["lfo"] = [{"dest": "cutoff", "rate": "1/8", "depth": 2.5, "shape": "triangle"}]
    S["wobble: polysynth saw, LP LFO 1/8, drive+bitcrush+OTT, held F1, 2 bars"] = ("wobble", one(
        DB.T(wob, role="upper-bass", eq="auto", fx=DB.OLD_FX), "0:F1:32", 2))
    fw = {"type": "fmgrowl", "ops": [{"ratio": 1}, {"ratio": 1, "index": 1}], "drive": 0.4, "cutoff": 3000,
          "mod": [{"dest": "index", "rate": "1/8", "shape": "saw", "depth": 4},
                  {"dest": "cutoff", "rate": "1/8", "shape": "saw", "depth": 2}]}
    S["wobble: fmgrowl saw index+cutoff 1/8, held F1, 2 bars"] = ("wobble", one(DB.T(fw, role="upper-bass", eq="auto"),
                                                                             "0:F1:32", 2))
    reese = {"type": "polysynth", "osc": [{"shape": "saw", "voices": 2, "detune": 25},
                                          {"shape": "saw", "voices": 2, "detune": 9}],
             "cutoff": 2500, "sustain_level": 1, "release": 0.1, "lfo": [{"dest": "detune", "rate": "1/16d", "depth": 0.3}]}
    S["reese: polysynth detuned saws (DUBSTEP.md mapping), held F1, 2 bars"] = ("reese", one(
        DB.T(reese, role="upper-bass", eq="auto"), "0:F1:32", 2))
    S["sub: 017 sub, held F#1, 1 bar"] = ("sub", one(t17("sub"), "0:F#1:16"))
    S["sub: sub harmonics 0.35 (A/B drop), held F1"] = ("sub", one(DB.T({"type": "sub", "harmonics": 0.35}, role="sub",
                                                                         eq="auto"), "0:F1:16"))
    S["snare: 017 stack (909 tune 200 + 909 clap), dry"] = ("snare", one(t17("snare"), "X...............", 1, "snare"))
    S["clap: clap909"] = ("clap", one(DB.T({"type": "clap909"}, role="clap"), "X...............", 1, "clap"))
    S["kick: 017 stack (sub C#2, punch, click)"] = ("kick", one(t17("kick"), "X...............", 1, "kick"))
    S["kick: A/B KICK (kicksub F1 + click)"] = ("kick", one(copy.deepcopy(DB.KICK), "X...............", 1, "kick"))
    S["hat: metalhat decay 0.04 (017)"] = ("hat", one(t17("hats"), "x...............", 1, "hats"))
    cap = t17("captor")
    cap["layers"] = [L for L in cap["layers"] if L["name"] == "teeth"]
    S["screech: 017 captor teeth layer (comb), F#1, 1 bar"] = ("screech", one(cap, "0:F#1:16/r=1/8"))
    cb = copy.deepcopy(DB.GROWL)
    cb.update(vowel=None)
    S["screech: A/B comb case (growl + comb F4 + flanger), F2"] = ("screech", one(DB.T(cb, role="upper-bass", eq="auto", fx=[
        {"type": "comb", "note": "F4", "feedback": 0.85, "depth": 0.3, "rate": "1/8", "mix": 0.6},
        {"type": "flanger", "rate": "1/2", "feedback": 0.6, "mix": 0.4}]), "0:F2:16"))
    S["riser: riser (noise sweep), 2 bars"] = ("riser", np.stack([I.riser(2 * BAR)] * 2))
    S["riser: rise (pitch riser), 2 bars"] = ("riser", np.stack([I.pitch_riser(2 * BAR)] * 2))
    S["impact: impact"] = ("impact", np.stack([I.impact()] * 2))
    S["downlifter: downlifter, 1 bar"] = ("downlifter", np.stack([I.downlifter(BAR)] * 2))
    try:   # needs the voicebanks (engine/third_party.json); skipped without them
        S["vocalchop: 017 voice 'still here' (singer, hanami-soft)"] = ("vocalchop", one(
            t17("voice"), P17["patterns"]["sing1"]["voice"], 4, "voice"))
    except Exception as e:  # pragma: no cover
        print("vocal chop skipped:", e)
    return S


def new_sounds():
    """{label: (role, stereo)}: the fitted presets and the fx_model 2 transitions."""
    S = {}
    for name, (notes, bars) in NOTES.items():
        S[f"{ROLE.get(name, name)}: preset {name}, {notes.split(':')[1] if ':' in notes else 'one hit'}"] = (
            ROLE.get(name, name), one({"preset": name}, notes, bars, name))
    S["growl: preset growl, drop 1A phrase, 4 bars"] = ("growl", one({"preset": "growl"},
                                                                     P17["patterns"]["d1A"]["captor"], 4))
    S["riser: riser (fx_model 2), 2 bars"] = ("riser", D2.riser(2 * BAR))
    S["riser: rise (fx_model 2), 2 bars"] = ("riser", D2.pitch_riser(2 * BAR))
    S["impact: impact (fx_model 2)"] = ("impact", D2.impact())
    S["downlifter: downlifter (fx_model 2), 1 bar"] = ("downlifter", D2.downlifter(BAR))
    return S
