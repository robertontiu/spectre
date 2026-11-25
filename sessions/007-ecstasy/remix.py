#!/usr/bin/env python3
"""First Light remix (2026-11-25): the three audible steps of docs/PRODUCTION.md "Remixing and remastering".

    python3 remix.py        # writes project-step1.json, project-step2.json, project-remix.json from project-published.json (the previous release)

project.json stays the published version (v030). Every step only edits `tracks`, `mix`, `genre` and `buses`;
`bpm`, `swing`, `seed`, `patterns` and `arrangement` are frozen, and no track is added (stacks double a track's
own notes inside the track, so every original track's events stay identical: checked against
renders/v030.meta.json after each render).

1. step 1 (render v033, master --genre trance = trance_2015): remaster only, with the kick's carving for the
   old Pestana curve undone (journal 17-23): the EQ (-5 dB at 55 Hz, -11 at 66, +5 at 105) and the hpf 40 come out,
   the kick is tuned to the key's root (Ab1, 52 Hz, from the 56 Hz compromise between the curve's 50 and 63 Hz
   bands) and turned down 4 dB, since uncarved and saturated it was 6 dB hot at 50-63 Hz over the whole track.
2. step 2 (today's engine, the original instruments): role EQ presets from the trance map instead of the old
   per-track carving, the bass's dip at 68 Hz replaced by a dynamic notch keyed by the kick, filtered/ducked
   returns (a short room for the drums, the hall high-passed, cut at 450 Hz and ducked by the lead, a ping-pong
   delay off the grid), a drum bus with a soft clipper, a music bus with 2:1 glue, OTT at partial depth on the lead.
3. remix candidate (re-sound-design): kick, bass, lead (and its octave double), pad and both hats rebuilt as
   stacks with supersaw model 2 and the new sources, following docs/TRANCE.md B and the A/B in examples/production,
   with that study's three findings addressed (100-250 Hz lean, softer transients, shaker hats buried).
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def step1(P):
    P = copy.deepcopy(P)
    k = P["tracks"]["kick"]
    k["inst"].update(tune=52)                                   # Ab1, the key's root (F minor / Ab major)
    k["fx"] = [{"type": "hpf", "hz": 30}, {"type": "sat", "amount": 0.9}, {"type": "gain", "db": -3}]
    return P


def step2(P):
    P = step1(P)
    P["genre"] = "trance"
    T = P["tracks"]
    # drums: role presets, a drum bus that soft-clips (the mix controls the peaks, not the master)
    T["kick"].update(role="kick", eq={"own_db": 0}, bus="drums",
                     fx=[{"type": "sat", "amount": 0.9}, {"type": "gain", "db": -6}])
    T["clap"].update(role="clap", eq="auto", bus="drums", fx=[], send_reverb=0.15, sends={"room": 0.3})
    T["ohat"].update(role="hats", eq="auto", bus="drums",
                     fx=[{"type": "highshelf", "hz": 9000, "gain_db": -5}, {"type": "lpf", "hz": 12000}])
    T["chh"].update(role="hats", eq="auto", bus="drums", gain_db=4.5,
                    fx=[{"type": "highshelf", "hz": 8000, "gain_db": -4}, {"type": "lpf", "hz": 12000}])
    T["snare"].update(role="snare", eq="auto", bus="drums", send_reverb=0.15, sends={"room": 0.3},
                      fx=[{"type": "highshelf", "hz": 5000, "gain_db": -6}])
    # bass: keep its own sub; the map's body and bite; the old static dip at 68 Hz becomes a notch keyed by the kick
    b = T["bass"]
    b["inst"].update(cutoff=420, sub=0.12)                      # without the static dip, less of its own sine
    b["gain_db"] = 1.5                                          # the 100-250 Hz body the old curve's cut took
    b.update(role="bass", eq={"hp": 35}, fx=[{"type": "dyneq", "hz": 52, "q": 1.5, "depth_db": -6, "key": "kick",
                                               "release_ms": 90}])
    # lead: the map's body and 1-4 kHz instead of hpf 300 and a cut at 2.6 kHz; OTT at partial depth
    T["lead"].update(role="lead", eq="auto",
                     fx=[{"type": "eq", "hz": 6000, "gain_db": 2.0, "q": 0.8},
                         {"type": "ott", "depth": 0.3},
                         {"type": "chorus", "rate": 0.3, "depth": 0.25, "mix": 0.25}])
    T["lead"]["gain_db"] = 7.5                                  # 1.5 dB down: it came forward without the cuts
    T["lead2"].update(role="support", eq={"hp": 700}, fx=[], gain_db=2)
    T["saws"].update(role="support", eq={"hp": 200, "cut_db": -1.5}, bus="music",  # their chord roots
                     fx=[T["saws"]["fx"][1],
                         {"type": "mseq", "mid": [{"type": "eq", "hz": 2200, "gain_db": -2, "q": 0.9}]}])
    T["pluck"].update(role="pluck", eq="auto", fx=[], sends={"room": 0.2})
    T["arp"].update(role="arp", eq="auto", fx=[])
    p = T["pad"]
    p.update(role="pad", eq="auto", bus="music", fx=[{"type": "ott", "depth": 0.2}], send_reverb=0.4, width=0.7)
    p["sidechain"] = dict(p["sidechain"], depth=0.65)
    T["vox"].update(role="vocal", eq={"hp": 220}, fx=[])
    T["choir"].update(role="choir", eq="auto", bus="music", fx=[], send_reverb=0.38)
    P["buses"] = {"drums": {"fx": [{"type": "clip", "drive_db": 1.0, "ceiling_db": -1.0, "knee": 0.4}]},
                  "music": {"fx": [{"type": "comp", "threshold_db": -22, "ratio": 2, "attack_ms": 20,
                                    "release_ms": 150}]}}
    # spaces: the hall filtered as the map asks and ducked by the lead; a room for drums and plucks; the delay
    # ping-ponged a few ms off the grid and ducked (it was 100% masked by the hall)
    P["mix"] = {"reverb": {"size": 0.9, "damping": 0.45, "return_db": -5, "predelay_ms": 25, "hpf": 350, "lpf": 9000,
                           "fx": [{"type": "eq", "hz": 450, "gain_db": -3, "q": 1.0}],
                           "duck": {"key": "lead", "depth_db": 5, "release_ms": 300}},
                "delay": {"beats": 0.75, "feedback": 0.38, "return_db": -5, "pingpong": True, "offset_ms": 9,
                          "hpf": 300, "lpf": 6000, "duck": {"key": "lead", "depth_db": 4, "release_ms": 250}},
                "returns": {"room": {"type": "reverb", "size": 0.3, "damping": 0.6, "predelay_ms": 8,
                                     "hpf": 300, "lpf": 9000, "return_db": -6}}}
    return P


def remix(P):
    P = step2(P)
    T = P["tracks"]
    # kick: sub tuned to Ab1, a louder punch for the 100-250 Hz body, a click; the drum bus clips
    T["kick"] = {"role": "kick", "humanize_ms": 0, "vel_jitter": 0.02, "bus": "drums",
                 "fx": [{"type": "clip", "drive_db": 1.0, "ceiling_db": -1.5, "knee": 0.4}, {"type": "gain", "db": -2}],
                 "layers": [
                     {"name": "sub", "inst": {"type": "kicksub", "note": "Ab1", "punch": 14, "hold": 0.025, "tail": 0.06,
                                              "drive": 0.3}, "role": "kick", "eq": {"own_db": 0, "cut_db": 0},
                      "gain_db": -4},
                     {"name": "punch", "inst": {"type": "kickpunch", "tune": 100, "sweep": 4, "decay": 0.03, "thump": 0.4,
                                                "drive": 1.0}, "role": "kick", "eq": {"hp": 80, "own_db": 0}, "gain_db": 3},
                     {"name": "click", "inst": {"type": "kickclick", "tone": 2200}, "role": "kick",
                      "eq": {"hp": 1500, "cut_db": 0, "own_db": 0}, "gain_db": 5,
                      "fx": [{"type": "lpf", "hz": 6000, "slope": 24}]}]}
    # bass: a clean sub, the rolling/offbeat trancebass with its body at 150-250 Hz and bite, an upper bass
    b = T["bass"]
    T["bass"] = {"role": "bass", "humanize_ms": 0, "vel_jitter": 0.03, "sidechain": b["sidechain"],
                 "auto": b.get("auto"),
                 "fx": [{"type": "dyneq", "hz": 52, "q": 1.5, "depth_db": -4, "key": "kick", "release_ms": 90},
                        {"type": "comp", "threshold_db": -20, "ratio": 2, "attack_ms": 10, "release_ms": 80},
                        {"type": "sat", "amount": 0.15}],
                 "layers": [
                     {"name": "sub", "inst": {"type": "sub", "attack": 0.004, "release": 0.03, "harmonics": 0.2},
                      "role": "sub", "gain_db": -3},
                     {"name": "roll", "inst": {"type": "trancebass", "sub": 0, "cutoff": 700, "env": 2600,
                                               "fdecay": 0.06, "drive": 0.35, "reso": 0.2},
                      "role": "bass", "gain_db": 7, "eq": {"hp": 90, "own_db": 4}},
                     {"name": "upper", "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 10},
                                                                              {"shape": "pulse", "pw": 0.3, "level": 0.5}],
                                                "cutoff": 1400, "env": 3500, "fdecay": 0.05, "decay": 0.1,
                                                "sustain_level": 0.25, "release": 0.04},
                      "role": "upper-bass", "octave": 1, "gain_db": 11}]}
    T["bass"] = {k: v for k, v in T["bass"].items() if v is not None}
    # lead: main supersaw model 2 (the published lead's voices, detune, mix, filter envelope), support an octave
    # down (wide, slower), a short bright transient copy above 1 kHz (van Buuren), air, a narrow square centre
    lead = T["lead"]
    i = lead["inst"]
    main = {"type": "supersaw", "model": 2, "voices": i["voices"], "detune": i["detune"], "mix": i["mix"],
            "spread": i["spread"], "attack": i["attack"], "release": i["release"], "cutoff": i["cutoff"] * 1.3,
            "env": i["env"], "fdecay": i["fdecay"], "drift": 0.35, "vibrato": 10, "vib_delay": 0.3}
    T["lead"] = {"role": "lead", "humanize_ms": 0, "sidechain": dict(lead["sidechain"], depth=0.45), "send_reverb": lead["send_reverb"],
                 "send_delay": lead["send_delay"], "gain_db": 0,
                 "fx": [{"type": "comp", "threshold_db": -18, "ratio": 2, "attack_ms": 15, "release_ms": 150},
                        {"type": "chorus", "rate": 0.3, "depth": 0.2, "mix": 0.15}],
                 "layers": [
                     {"name": "main", "inst": main, "role": "lead", "gain_db": 9},
                     {"name": "support", "inst": dict(main, voices=7, detune=30, attack=0.03, release=0.55, spread=1.0,
                                                      drift=0.5, vibrato=0),
                      "octave": -1, "role": "support", "gain_db": 3, "width": 0.6, "eq": {"hp": 150, "cut_db": 0}},
                     {"name": "transient", "inst": {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3,
                                                                                  "detune": 8}],
                                                    "cutoff": 3000, "env": 6000, "fdecay": 0.04, "attack": 0.001,
                                                    "decay": 0.07, "sustain_level": 0, "release": 0.05},
                      "role": "lead", "eq": "none", "gain_db": 15,
                      "fx": [{"type": "hpf", "hz": 1000, "slope": 24}]},
                     {"name": "air", "inst": {"type": "air", "octave": 1, "noise": 0.45, "attack": 0.02,
                                              "release": 0.25}, "role": "air", "gain_db": 12},
                     {"name": "centre", "inst": {"type": "polysynth", "osc": [{"shape": "square"}], "cutoff": 2200,
                                                 "attack": 0.005, "release": 0.2},
                      "role": "lead", "eq": "none", "gain_db": 0, "fx": [{"type": "hpf", "hz": 200, "slope": 12}]}]}
    l2 = T["lead2"]
    j = l2["inst"]
    m2 = {"type": "supersaw", "model": 2, "voices": j["voices"], "detune": j["detune"], "mix": j["mix"],
          "spread": j["spread"], "transpose": 12, "attack": j["attack"], "release": j["release"],
          "cutoff": j["cutoff"] * 1.3, "drift": 0.4}
    T["lead2"] = {"role": "support", "humanize_ms": 0, "sidechain": l2["sidechain"], "send_reverb": l2["send_reverb"],
                  "send_delay": l2["send_delay"], "fx": [{"type": "ott", "depth": 0.2}],
                  "layers": [{"name": "main", "inst": m2, "role": "support", "eq": {"hp": 700}, "gain_db": 4},
                             {"name": "air", "inst": {"type": "air", "octave": 1, "noise": 0.3, "attack": 0.03,
                                                      "release": 0.3}, "role": "air", "gain_db": 8}]}
    # pad: a moving polysynth body, a bright supersaw layer an octave up; OTT and a deeper sidechain on the bus
    pad = T["pad"]
    T["pad"] = {"role": "pad", "humanize_ms": 0, "bus": "music", "width": 0.7, "send_reverb": 0.4,
                "sidechain": pad["sidechain"], "fx": [],
                "layers": [
                    {"name": "body", "inst": {"type": "polysynth",
                                              "osc": [{"shape": "saw", "voices": 5, "detune": 14},
                                                      {"shape": "triangle", "octave": -1, "level": 0.25}],
                                              "attack": 1.4, "release": 2.5, "cutoff": 2400,
                                              "lfo": [{"dest": "cutoff", "rate": 0.15, "depth": 0.4}], "drift": 0.5},
                     "role": "pad", "gain_db": 12, "eq": {"cut_db": -1.5}},
                    {"name": "bright", "inst": {"type": "supersaw", "model": 2, "voices": 7, "detune": 18, "mix": 0.6,
                                                "attack": 1.6, "release": 2.5, "cutoff": 7000, "noise": 0.2},
                     "role": "support", "octave": 1, "gain_db": 2, "width": 1.0}]}
    # hats: tonal metal (the brighter top from partials, not hiss), the published noise hats kept underneath
    chh, oh = T["chh"], T["ohat"]
    T["chh"] = {"role": "hats", "bus": "drums", "humanize_ms": chh["humanize_ms"], "dyn": chh["dyn"],
                "pan": chh["pan"], "gain_db": 0,
                "layers": [{"name": "metal", "inst": {"type": "metalhat", "decay": 0.035, "tone": 9000, "lp": 11000},
                            "role": "hats", "gain_db": 8},
                           {"name": "shaker", "inst": {"type": "shaker"}, "role": "hats", "gain_db": 2,
                            "fx": [{"type": "lpf", "hz": 9000}]}]}
    T["ohat"] = {"role": "hats", "bus": "drums", "humanize_ms": oh["humanize_ms"], "pan": oh["pan"], "gain_db": 0,
                 "layers": [{"name": "metal", "inst": {"type": "metalhat", "open": True, "decay": 0.16, "lp": 11000},
                             "role": "hats", "gain_db": 3},
                            {"name": "noise", "inst": dict(oh["inst"]), "role": "hats", "gain_db": 0,
                             "fx": [{"type": "highshelf", "hz": 9000, "gain_db": -6}, {"type": "lpf", "hz": 10000}]}]}
    # levels: each stack matched to the step-2 track it replaces over rel2's first 8 bars (the kick by its peak, the
    # others by A-weighted energy), then the deliberate moves (see LEVEL_MOVES)
    for g, d in LEVEL_MATCH.items():
        T[g]["fx"] = list(T[g].get("fx") or []) + [{"type": "gain", "db": round(d + LEVEL_MOVES.get(g, 0.0), 2)}]
    return P


LEVEL_MATCH = {"kick": 0.4, "bass": -4.24, "lead": 1.23, "lead2": -1.03, "pad": -10.87, "chh": 1.88, "ohat": 2.46}
LEVEL_MOVES = {"kick": 0.0,    # peak-matched (the full-track balance at 50 and 100-250 Hz set the layers inside it)
               "chh": 0.0,     # the A/B found the shaker 100% masked by the lead stack's air: the metal layer brings it
                               # out; louder, the outro (hats alone with the kick) read 8-9 dB over the curve on a phone
               "ohat": -1.5,
               "pad": -2.0,    # the polysynth body under the breakdowns' low-pass read 1.5-2 LU louder than the old pad
               "bass": 1.0}   # the driven kick punch now carries 100-250 Hz; a louder bass flattened the crest


if __name__ == "__main__":
    P = json.load(open(os.path.join(HERE, "project-published.json")))  # the previous release; project.json is now the remix
    for name, fn in (("project-step1.json", step1), ("project-step2.json", step2), ("project-remix.json", remix)):
        json.dump(fn(P), open(os.path.join(HERE, name), "w"), indent=1)
        print("wrote", name)
