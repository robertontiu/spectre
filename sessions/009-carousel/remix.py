#!/usr/bin/env python3
"""Here You Are remix (2026-11-25): depth M + R (docs/PRODUCTION.md "Remixing and remastering").

    python3 remix.py        # writes project-remix.json from project-published.json (the previous release)

project.json stays the published version (v034). Only `tracks` and `genre` change; `bpm`, `swing`, `seed`,
`patterns`, `arrangement` and the lyrics are frozen, no track is added, and the sung hook `voxC`, the other voices
and `mix` (the reverb and delay the approved chorus voice runs through) are untouched (asserted below).

What changes (docs/POP_ROCK.md "Layering and EQ carving": every part under the voice gets a slot of its own):
- kick: the carving for the old curve (-12 dB at 56 Hz, +6 at 115) is halved (-6, +4): the shell's weight at 56 Hz is its slot
- bass: 60-150 Hz and its definition at 900 Hz; the +5 dB at 240 Hz (the guitars' body) comes out, -2 dB at 350 Hz
- rhythm guitars: their low shelves at 350 Hz come down 2-2.5 dB, the body stays;
  the two takes pulled apart in tone (left low and anchored, right higher)
- organ: high-passed at 200 Hz, opened to 5 kHz, its 1-3 kHz slot, and a level at which it measures as present
- cymbals, snare, tambourine, the clean figure: less of the darkening that was fitted to the old curve
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = ("voxV", "voxC", "voxB", "voxD", "voxCw")


def setfx(tr, typ, at, **kw):
    """Change the fx of that type at that frequency in place (the chain's order stays)."""
    for f in tr["fx"]:
        if f["type"] == typ and f.get("hz") == at:
            f.update(kw)
            return
    raise KeyError((typ, at))


def dropfx(tr, typ, hz):
    n = len(tr["fx"])
    tr["fx"] = [f for f in tr["fx"] if not (f["type"] == typ and f.get("hz") == hz)]
    assert len(tr["fx"]) == n - 1, (typ, hz)


def remix(P):
    Q = copy.deepcopy(P)
    Q["genre"] = "rock"
    T = Q["tracks"]
    for n, r in ROLES.items():
        T[n]["role"] = r
        T[n]["eq"] = "none"            # the roles name the parts for the census; the EQ is written out below
    # kick: its own fundamental back
    setfx(T["kick"], "eq", 56, gain_db=-6)
    setfx(T["kick"], "eq", 115, gain_db=4)
    T["kick"]["gain_db"] += G["kick"]
    # bass
    b = T["bass"]
    setfx(b, "eq", 135, gain_db=7)
    setfx(b, "eq", 240, gain_db=2.0)
    setfx(b, "eq", 800, hz=900, gain_db=4.5)
    b["fx"].append({"type": "eq", "hz": 350, "gain_db": -2, "q": 1.0})
    b["gain_db"] += G["bass"]
    # rhythm guitars
    setfx(T["gtrL"], "lowshelf", 350, gain_db=6)
    setfx(T["gtrR"], "lowshelf", 350, gain_db=4.5)
    T["gtrL"]["gain_db"] += G["gtr"]; T["gtrR"]["gain_db"] += G["gtr"]
    # organ
    T["organ"]["fx"] = [{"type": "hpf", "hz": 200, "slope": 12}, {"type": "eq", "hz": 350, "gain_db": -3, "q": 1.0},
                        {"type": "eq", "hz": 1800, "gain_db": 3, "q": 0.7}, {"type": "lpf", "hz": 5000}]
    T["organ"]["gain_db"] += G["organ"]
    # the top: cymbals, snare, tambourine, the clean figure
    setfx(T["hat"], "highshelf", 7000, gain_db=-2)
    setfx(T["ohat"], "highshelf", 7000, gain_db=-1.5)
    setfx(T["ride"], "highshelf", 6500, gain_db=-2.5)
    setfx(T["bell"], "highshelf", 6500, gain_db=-2.5)
    setfx(T["crash"], "highshelf", 8000, gain_db=-1)
    setfx(T["snare"], "highshelf", 4500, gain_db=-5)
    setfx(T["snare"], "lpf", 9000, hz=11000)
    setfx(T["tamb"], "lpf", 9500, hz=11500)
    T["tamb"]["gain_db"] += G["tamb"]
    setfx(T["fig"], "lpf", 7500, hz=9500)
    setfx(T["figM"], "lpf", 6500, hz=8000)
    for v in VOICES:
        assert T[v] == P["tracks"][v], v
    for key in ("bpm", "swing", "seed", "patterns", "arrangement", "mix"):
        assert Q[key] == P[key], key
    return Q


ROLES = {"kick": "kick", "snare": "snare", "hat": "hats", "ohat": "hats", "phat": "hats", "ride": "cymbals",
         "bell": "cymbals", "crash": "cymbals", "tamb": "hats", "bass": "bass", "gtrL": "guitar", "gtrR": "guitar",
         "chug": "guitar", "organ": "organ"}
G = {"kick": -1.5, "bass": 0.0, "gtr": 0.5, "organ": 0.0, "tamb": 2.0}

if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    json.dump(remix(P), open(os.path.join(HERE, "project-remix.json"), "w"), indent=1)
    print("wrote project-remix.json")
