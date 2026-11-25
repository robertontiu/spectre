#!/usr/bin/env python3
"""The Note She Kept remix (2026-11-25): depth R, light M (docs/PRODUCTION.md "Remixing and remastering").

    python3 remix.py        # writes project-remix.json from project.json

project.json stays the published version (v031). `bpm`, `swing`, `seed`, `patterns`, `arrangement` (and with them
the lyrics) are frozen and no track is added. The approved v031 voice mix is untouched: every `singer` track and the
whole of `mix` (the one shared reverb every voice runs through) are asserted identical below.

An acoustic track: no stacks, no buses, no compression, no new carving. Only boosts that the journal shows were made
for the borrowed rock curve are (partly) undone:
- pedal: the +3 dB at 140 Hz comes out (97-183 Hz sat 10 dB over the five reference albums, 6 dB after the remaster;
  the pedal is the loudest stem at 60-150 Hz, the cello 6 dB under it)
Tried and taken out again (v033): the organ's top boosts (+4 dB at 2.6 kHz, shelf +5 dB from 5 kHz; journal 24 and 30)
lowered to +2 / +2. The master's cut at 4 kHz stayed at -7.9 dB: the top there is the voices and the bells, which
are not to change, so the move bought nothing and the organ stays as published.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES = {"organ_door": "organ", "organ": "organ", "pedal": "bass", "cello": "low-strings", "chorale": "keys",
         "bell_st": "bells", "bellL": "bells", "bellR": "bells"}


def setfx(tr, typ, at, **kw):
    for f in tr["fx"]:
        if f["type"] == typ and f.get("hz") == at:
            f.update(kw)
            return
    raise KeyError((typ, at))


def remix(P):
    Q = copy.deepcopy(P)
    Q["genre"] = "caroling"
    T = Q["tracks"]
    for n, r in ROLES.items():
        T[n]["role"] = r
        T[n]["eq"] = "none"             # roles only name the parts for the clarity census; no preset EQ
    n = len(T["pedal"]["fx"])
    T["pedal"]["fx"] = [f for f in T["pedal"]["fx"] if not (f["type"] == "eq" and f["hz"] == 140)]
    assert len(T["pedal"]["fx"]) == n - 1
    voices = [k for k, t in P["tracks"].items() if t["inst"]["type"] == "singer"]
    assert len(voices) == 11, voices
    for v in voices:
        assert T[v] == P["tracks"][v], v
    for key in ("bpm", "swing", "seed", "patterns", "arrangement", "mix", "master", "title"):
        assert Q[key] == P[key], key
    assert list(T) == list(P["tracks"])
    return Q


if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    json.dump(remix(P), open(os.path.join(HERE, "project-remix.json"), "w"), indent=1)
    print("wrote project-remix.json")
