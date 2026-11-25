#!/usr/bin/env python3
"""Half of Me remix (2026-11-25): depth S, after First Light's (sessions/007-ecstasy/remix.py, journal 32-34).

    python3 remix.py        # writes project-remix.json from project-published.json (the previous release)

project.json stays the published version (v032). The remix only edits `tracks`, `mix`, `genre` and `buses`;
`bpm`, `swing`, `seed`, `patterns` and `arrangement` are frozen and no track is added (stacks double a track's own
notes inside the track), so every original track's events stay identical (remix_check.py events v032 vNNN).

What changes:
- kick: the carving for the old Pestana curve (-7.5 dB at 56 Hz, -11 at 66, +5 at 105) comes out; a stack of
  `kicksub` on F#1 (the key's root, 46 Hz), `kickpunch`, `kickclick`; the drum bus soft-clips. The old sine thump
  under it (`ksub`, B0) is muted: the stack's sub layer is that part now.
- bass: `sub` + the published `trancebass` without its sine and opened + an upper bass an octave up; the static dip
  at 68 Hz becomes a notch at 46 Hz keyed by the kick. The bass line sits on the kick's note (F#1): its sub stays
  low (docs/TRANCE.md B).
- lead: supersaw model 2 with the published voices, detune, mix, resonance and filter envelope, a support layer an
  octave down, a transient above 1 kHz, air, a square centre.
- saws (gated), pad, hats: role EQ; the pad a polysynth body plus a bright layer; hats tonal metal over the
  published noise hats.
- spaces: the voices stay exactly as they are (docs/TRANCE.md "Mixing the voice"): `mix.reverb` and `mix.delay`,
  which carry every voice's tail, are untouched. The synths and drums move to their own returns: a hall (the same
  size, high-passed, cut at 450 Hz, ducked by the lead), a ping-pong echo, a short room.
- no voice track is edited.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = ("chop", "line", "lthrow", "fthrow", "throw", "far", "chD", "chS")


def remix(P):
    Q = copy.deepcopy(P)
    Q["genre"] = "trance"
    T = Q["tracks"]
    # ---- drums
    k = T["kick"]
    T["kick"] = {"role": "kick", "humanize_ms": 0, "vel_jitter": k["vel_jitter"], "bus": "drums",
                 "fx": [{"type": "clip", "drive_db": 1.0, "ceiling_db": -1.5, "knee": 0.4},
                        {"type": "gain", "db": G["kick"]}],
                 "layers": [
                     {"name": "sub", "inst": {"type": "kicksub", "note": "F#1", "punch": 14, "drop": 0.028,
                                              "hold": 0.025, "tail": 0.06, "drive": 0.3}, "role": "kick",
                      "eq": {"own_db": 0, "cut_db": 0}, "gain_db": -4},
                     {"name": "punch", "inst": {"type": "kickpunch", "tune": 100, "sweep": 4, "decay": 0.03,
                                                "thump": 0.4, "drive": 1.0}, "role": "kick",
                      "eq": {"hp": 62, "own_db": 0}, "gain_db": 3},
                     {"name": "click", "inst": {"type": "kickclick", "tone": 2200}, "role": "kick",
                      "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}, "gain_db": 5,
                      "fx": [{"type": "lpf", "hz": 6000, "slope": 24}]}]}
    T["ksub"]["mute"] = True
    T["clap"].update(role="clap", eq="auto", bus="drums", fx=[], send_reverb=0, sends={"hall": 0.22, "room": 0.3})
    T["snare"].update(role="snare", eq="auto", bus="drums", send_reverb=0, sends={"hall": 0.3, "room": 0.3},
                      fx=[{"type": "highshelf", "hz": 5000, "gain_db": -6}])
    chh, oh = T["chh"], T["ohat"]
    T["chh"] = {"role": "hats", "bus": "drums", "humanize_ms": chh["humanize_ms"], "dyn": chh["dyn"],
                "pan": chh["pan"], "gain_db": 0, "fx": [{"type": "gain", "db": G["chh"]}],
                "layers": [{"name": "metal", "inst": {"type": "metalhat", "decay": 0.035, "tone": 9000, "lp": 11000},
                            "role": "hats", "gain_db": 8},
                           {"name": "noise", "inst": dict(chh["inst"]), "role": "hats", "gain_db": 2,
                            "fx": [{"type": "lpf", "hz": 9000}]}]}
    T["ohat"] = {"role": "hats", "bus": "drums", "humanize_ms": oh["humanize_ms"], "pan": oh["pan"], "gain_db": 0,
                 "fx": [{"type": "gain", "db": G["ohat"]}],
                 "layers": [{"name": "metal", "inst": {"type": "metalhat", "open": True, "decay": 0.16, "lp": 11000},
                             "role": "hats", "gain_db": 3},
                            {"name": "noise", "inst": dict(oh["inst"]), "role": "hats", "gain_db": 0,
                             "fx": [{"type": "highshelf", "hz": 9000, "gain_db": -6}, {"type": "lpf", "hz": 10000}]}]}
    # ---- bass
    b = T["bass"]
    T["bass"] = {"role": "bass", "humanize_ms": 0, "vel_jitter": b["vel_jitter"], "sidechain": b["sidechain"],
                 "fx": [{"type": "dyneq", "hz": 46, "q": 1.5, "depth_db": -4, "key": "kick", "release_ms": 90},
                        {"type": "comp", "threshold_db": -20, "ratio": 2, "attack_ms": 10, "release_ms": 80},
                        {"type": "sat", "amount": 0.15}, {"type": "gain", "db": G["bass"]}],
                 "layers": [
                     {"name": "sub", "inst": {"type": "sub", "attack": 0.004, "release": 0.03, "harmonics": 0.2},
                      "role": "sub", "gain_db": G["bass.sub"]},
                     {"name": "roll", "inst": {"type": "trancebass", "sub": 0, "cutoff": 700,
                                               "env": b["inst"]["env"], "fdecay": b["inst"]["fdecay"],
                                               "drive": 0.35, "reso": 0.2},
                      "role": "bass", "gain_db": 7, "eq": {"hp": 72, "own_db": 4}},
                     {"name": "upper", "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 10},
                                                                              {"shape": "pulse", "pw": 0.3, "level": 0.5}],
                                                "cutoff": 1400, "env": 3500, "fdecay": 0.05, "decay": 0.1,
                                                "sustain_level": 0.25, "release": 0.04},
                      "role": "upper-bass", "octave": 1, "gain_db": 8}]}
    # ---- lead: the published stab (voices, detune, mix, resonance, filter envelope, legato) on model 2
    lead = T["lead"]
    i = lead["inst"]
    main = {"type": "supersaw", "model": 2, "voices": i["voices"], "detune": i["detune"], "mix": i["mix"],
            "spread": i["spread"], "attack": i["attack"], "release": i["release"], "cutoff": i["cutoff"] * 1.3,
            "reso": i["reso"], "env": i["env"], "fdecay": i["fdecay"], "drift": 0.35, "vibrato": 10, "vib_delay": 0.3}
    T["lead"] = {"role": "lead", "humanize_ms": 0, "legato": lead["legato"],
                 "sidechain": dict(lead["sidechain"], depth=0.45),
                 "send_reverb": 0, "send_delay": 0, "sends": {"hall": lead["send_reverb"], "echo": lead["send_delay"]},
                 "gain_db": 0,
                 "fx": [{"type": "sat", "amount": 0.2},
                        {"type": "mseq", "mid": [{"type": "eq", "hz": 3200, "gain_db": -2, "q": 0.8}]},  # the voice's band
                        {"type": "comp", "threshold_db": -18, "ratio": 2, "attack_ms": 15, "release_ms": 150},
                        {"type": "chorus", "rate": 0.3, "depth": 0.2, "mix": 0.15}, {"type": "gain", "db": G["lead"]}],
                 "layers": [
                     {"name": "main", "inst": main, "role": "lead", "gain_db": 9},
                     {"name": "support", "inst": dict(main, voices=7, detune=30, attack=0.02, release=0.3, spread=1.0,
                                                      drift=0.5, vibrato=0),
                      "octave": -1, "role": "support", "gain_db": 3, "width": 0.6, "eq": {"hp": 150, "cut_db": 0}},
                     {"name": "transient", "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3,
                                                                                  "detune": 8}],
                                                    "cutoff": 3000, "env": 6000, "fdecay": 0.04, "attack": 0.001,
                                                    "decay": 0.07, "sustain_level": 0, "release": 0.05},
                      "role": "lead", "eq": "none", "gain_db": 15, "fx": [{"type": "hpf", "hz": 1000, "slope": 24}]},
                     {"name": "air", "inst": {"type": "air", "octave": 1, "noise": 0.45, "attack": 0.02,
                                              "release": 0.2}, "role": "air", "gain_db": 12},
                     {"name": "centre", "inst": {"type": "polysynth", "osc": [{"shape": "square"}], "cutoff": 2200,
                                                 "attack": 0.005, "release": 0.12},
                      "role": "lead", "eq": "none", "gain_db": 0, "fx": [{"type": "hpf", "hz": 200, "slope": 12}]}]}
    # ---- gated saws: the map's supporting row; the dip that makes room for the voice (2.5 kHz) only in the centre
    s = T["saws"]
    gate = [f for f in s["fx"] if f["type"] == "gate"]
    s.update(role="support", eq={"hp": 230, "cut_db": -2}, bus="music", send_reverb=0, send_delay=0,
             sends={"hall": s["send_reverb"], "echo": s["send_delay"]},
             fx=gate + [{"type": "mseq", "mid": [{"type": "eq", "hz": 2500, "gain_db": -2.5, "q": 0.7}]},
                        {"type": "gain", "db": G["saws"]}])
    # ---- pad: a moving body and a bright layer
    pad = T["pad"]
    T["pad"] = {"role": "pad", "humanize_ms": 0, "bus": "music", "width": 0.6, "send_reverb": 0,
                "sends": {"hall": pad["send_reverb"]}, "sidechain": pad["sidechain"],
                "fx": [{"type": "gain", "db": G["pad"]}],
                "layers": [
                    {"name": "body", "inst": {"type": "polysynth",
                                              "osc": [{"shape": "saw", "voices": 5, "detune": 14},
                                                      {"shape": "triangle", "octave": -1, "level": 0.25}],
                                              "attack": 1.0, "release": 2.0, "cutoff": 2000,
                                              "lfo": [{"dest": "cutoff", "rate": 0.15, "depth": 0.4}], "drift": 0.5},
                     "role": "pad", "gain_db": 12, "eq": {"cut_db": -1.5}},
                    {"name": "bright", "inst": {"type": "supersaw", "model": 2, "voices": 7, "detune": 18, "mix": 0.6,
                                                "attack": 1.2, "release": 2.0, "cutoff": 6000, "noise": 0.2},
                     "role": "support", "octave": 1, "gain_db": 2, "width": 1.0}]}
    # ---- small parts: named for the census; their sound and sends stay
    T["tick"].update(role="pluck", eq="none")
    T["edge"].update(role="pluck", eq="none")
    T["rz"].update(role="arp", eq="none")
    Q["buses"] = {"drums": {"fx": [{"type": "clip", "drive_db": 1.0, "ceiling_db": -1.0, "knee": 0.4}]},
                  "music": {"fx": [{"type": "comp", "threshold_db": -22, "ratio": 2, "attack_ms": 20,
                                    "release_ms": 150}]}}
    r, d = Q["mix"]["reverb"], Q["mix"]["delay"]
    Q["mix"]["returns"] = {
        "hall": {"type": "reverb", "size": r["size"], "damping": r["damping"], "predelay_ms": 25, "hpf": 350,
                 "lpf": 8000, "return_db": r["return_db"] + G["hall"],
                 "fx": [{"type": "eq", "hz": 450, "gain_db": -3, "q": 1.0}],
                 "duck": {"key": "lead", "depth_db": 5, "release_ms": 300}},
        "echo": {"type": "delay", "beats": d["beats"], "feedback": d["feedback"], "pingpong": True, "offset_ms": 9,
                 "hpf": 300, "lpf": 6000, "return_db": d["return_db"] + 3,
                 "duck": {"key": "lead", "depth_db": 4, "release_ms": 250}},
        "room": {"type": "reverb", "size": 0.3, "damping": 0.6, "predelay_ms": 8, "hpf": 300, "lpf": 9000,
                 "return_db": -6}}
    for v in VOICES:
        assert T[v] == P["tracks"][v], v          # the voices stay as they are
    assert Q["mix"]["reverb"] == P["mix"]["reverb"] and Q["mix"]["delay"] == P["mix"]["delay"]
    for key in ("bpm", "swing", "seed", "patterns", "arrangement"):
        assert Q[key] == P[key], key
    return Q


# Levels (dB): each rebuilt part set against the published stem's A-weighted level in the main drop
# (listen --clarity, mainA / mainC), then the deliberate moves named in the journal.
G = {"kick": 0.5, "chh": 0.9, "ohat": 1.0, "bass": -0.5, "bass.sub": -5.0, "lead": 3.8, "saws": -0.5, "pad": -12.9,
     "hall": 1.5}


if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    json.dump(remix(P), open(os.path.join(HERE, "project-remix.json"), "w"), indent=1)
    print("wrote project-remix.json")
