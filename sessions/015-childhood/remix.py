#!/usr/bin/env python3
"""Again, Again remix (2026-11-25): depth R with the genre's own curve, M by orchestration balance only
(docs/PRODUCTION.md "Remixing and remastering"; docs/CHAMBER_SCORE.md "Layering and EQ carving").

    python3 remix.py        # writes project-remix.json from project.json

project.json stays the published version (v028). Only fx gains and one track level change: `bpm`, `swing`, `seed`,
`patterns`, `arrangement` and `mix` (the one hall) are frozen, no track or layer is added, every instrument keeps its
`inst` parameters, sends and pans (asserted below). Nothing new is carved: every move takes back, partly, an EQ move
the journal shows was made to satisfy the borrowed `rock` curve.

- low mids (journal entries 15 and 20: "the body the master asked for at 100-160"):
  the waltz piano's shelf under 170 Hz, the watcher's piano's shelf, the plucked cello's shelf under 200 Hz and
  part of its level. These are the doublings at 100-250 Hz: piano left hand and plucked cello on the same downbeat.
- the swell's top (entry 26: "shelves above 4 kHz on the three bowed tracks and the solo cello", fitted to a curve
  10 dB too bright for scores at 6-12 kHz): the shelves on violins, violas and the solo cello.
The shelves on the plucked and struck instruments (piano, guitar, plucked violin, far celesta, entries 17, 21, 27)
stay: the sections they play in measure under the new target at 2-12 kHz, not over it.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# track: (fx type, hz, new gain_db)     published value in the comment
FX = [
    ("piano", "lowshelf", 170, 0.5),     # +2
    ("pianoM", "lowshelf", 170, 1.0),    # +2
    ("floor", "lowshelf", 200, 1.0),     # +2.5
    ("vlns", "highshelf", 4000, 0.5),    # +3
    ("vlas", "highshelf", 4000, 1.5),    # +3
    ("cello", "highshelf", 4000, 1.5),   # +3
]
GAIN = {"floor": -0.5}                   # entry 20 raised it 1.5 dB with the shelf


def setfx(tr, typ, at, **kw):
    """Change the fx of that type at that frequency in place (the chain's order stays)."""
    for f in tr["fx"]:
        if f["type"] == typ and f.get("hz") == at:
            f.update(kw)
            return
    raise KeyError((typ, at))


def remix(P):
    Q = copy.deepcopy(P)
    T = Q["tracks"]
    for name, typ, hz, g in FX:
        setfx(T[name], typ, hz, gain_db=g)
    for name, d in GAIN.items():
        T[name]["gain_db"] += d
    # invariants
    for key in ("title", "bpm", "swing", "seed", "patterns", "arrangement", "mix", "master"):
        assert Q[key] == P[key], key
    assert list(T) == list(P["tracks"]), "tracks added, removed or reordered"
    touched = {n for n, *_ in FX} | set(GAIN)
    for n, t in T.items():
        p = P["tracks"][n]
        if n not in touched:
            assert t == p, n
            continue
        for k in set(t) | set(p):
            if k not in ("fx", "gain_db"):
                assert t.get(k) == p.get(k), (n, k)
        assert [(f["type"], f.get("hz")) for f in t.get("fx", [])] == [(f["type"], f.get("hz")) for f in p.get("fx", [])], n
    return Q


if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    json.dump(remix(P), open(os.path.join(HERE, "project-remix.json"), "w"), indent=1)
    print("wrote project-remix.json")
