#!/usr/bin/env python3
"""Lo que no supe decir remix (2026-11-25): depth R with the dark-strand curve, light M.

    python3 remix.py        # writes project-remix.json from project-published.json (the previous release)
    master: studio.py master vNNN --genre latinpop --target latinpop_dark

project.json stays the published version (v028). Only `tracks` and `genre` change; `bpm`, `swing`, `seed`,
`patterns`, `arrangement` and the lyrics are frozen, no track is added, and the voice `voz` and `mix` (its reverb)
are untouched (asserted below).

The low mids of the published master (+3 to +4 dB at 97-510 Hz against the reference albums) were built to meet the
borrowed rock curve (journal 62-90). The light M hands that weight back:
- bass: the boost at 165 Hz comes down, its fundamentals (A1 and up, 55-80 Hz) get the weight instead
- segunda guitars: -3 dB at the body's 190 Hz plate mode, the chop's 180 Hz boost down
Nothing is carved and nothing is brightened: an acoustic band (docs/LATIN_POP.md "Layering and EQ carving").
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def setfx(tr, typ, at, **kw):
    for f in tr["fx"]:
        if f["type"] == typ and f.get("hz") == at:
            f.update(kw)
            return
    raise KeyError((typ, at))


def remix(P):
    Q = copy.deepcopy(P)
    Q["genre"] = "latinpop"
    T = Q["tracks"]
    for n, r in ROLES.items():
        T[n]["role"] = r
        T[n]["eq"] = "none"            # roles name the parts for the census; no preset EQ on an acoustic band
    b = T["bass"]
    setfx(b, "eq", 165, gain_db=2.0)
    b["fx"].insert(0, {"type": "eq", "hz": 62, "gain_db": 6.0, "q": 0.8})
    for g in ("segarp", "segst"):      # the guitar body's plate mode at about 190 Hz (journal 90), not the shelf
        T[g]["fx"].append({"type": "eq", "hz": 195, "gain_db": -3.0, "q": 2.0})
    setfx(T["segb"], "eq", 180, gain_db=2.0)
    assert T["voz"] == P["tracks"]["voz"]
    for key in ("bpm", "swing", "seed", "patterns", "arrangement", "mix"):
        assert Q[key] == P[key], key
    return Q


ROLES = {"req": "lead", "reqc": "lead", "reqm": "lead", "req2": "lead", "reqx": "lead", "segarp": "guitar",
         "seg": "guitar", "segb": "guitar", "segst": "guitar", "bass": "bass", "bonh": "perc", "bonk": "perc",
         "bonl": "perc", "mar": "hats"}

if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    json.dump(remix(P), open(os.path.join(HERE, "project-remix.json"), "w"), indent=1)
    print("wrote project-remix.json")
