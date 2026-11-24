#!/usr/bin/env python3
"""build.py [loop|full]: writes project.json for session 013 (Spectre, trance radio edit, decay)."""
import json, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "full"

# ---------- the parent: an 8-note cell over 2 bars (steps in 16ths) ----------
CELL = [(0, "F#5", 3), (3, "A5", 3), (6, "C#6", 4), (10, "B5", 2),
        (12, "A5", 4), (16, "B5", 3), (19, "A5", 3), (22, "G5", 10)]
KEEP = {8: [0, 1, 2, 3, 4, 5, 6, 7], 4: [0, 2, 5, 7], 2: [2, 7], 1: [7]}


def cell(n, reps=1, octave=0, end=None):
    """the cell with n notes left, repeated reps times (2 bars each)"""
    out = []
    for r in range(reps):
        for i in KEEP[n]:
            s, p, l = CELL[i]
            if octave:
                p = p[:-1] + str(int(p[-1]) + octave)
            if end and i == 7 and r == reps - 1:
                l = end
            out.append("%d:%s:%d" % (s + 32 * r, p, l))
    return " ".join(out)


def chops(n, reps=1, words=("hold",), rest_last=False):
    """the daughter: the voice picks up the notes the lead lost (an octave lower)"""
    lost = [i for i in range(8) if i not in KEEP[n]]
    out, lyr, k = [], [], 0
    for r in range(reps):
        if rest_last and r == reps - 1:
            break
        for i in lost:
            s, p, l = CELL[i]
            p = p[:-1] + str(int(p[-1]) - 1)
            out.append("%d:%s:%d" % (s + 32 * r, p, min(l, 2)))
            lyr.append(words[k % len(words)])
            k += 1
    return {"notes": " ".join(out), "lyrics": " ".join(lyr)}


def steps(st, pitch="C#6", alt=None, bars=2, reps=1):
    out = []
    for r in range(reps):
        for j, x in enumerate(st):
            p = alt.get(x, pitch) if alt else pitch
            out.append("%d:%s:1" % (x + r * bars * 16, p))
    return " ".join(out)


def roll(roots, octs=False):
    """rolling bass: three 16ths between kicks, one root per bar"""
    out = []
    for b, r in enumerate(roots):
        for beat in range(4):
            for j in (1, 2, 3):
                p = r
                if octs and j == 2 and beat in (1, 3):
                    p = r[:-1] + str(int(r[-1]) + 1)
                out.append("%d:%s:1" % (b * 16 + beat * 4 + j, p))
    return " ".join(out)


ROOTS = ["F#1", "F#1", "F#1", "G1", "D2", "D2", "E2", "G1"]

tracks = {
    "kick": {"inst": {"type": "clubkick", "tune": 56, "tail": 0.05, "hold": 0.022, "punch": 1.4, "click": 0.3, "top": 0.08, "drive": 0.3},
             "humanize_ms": 0, "vel_jitter": 0.02,
             "fx": [{"type": "hpf", "hz": 30}, {"type": "eq", "hz": 56, "gain_db": -7.5, "q": 0.8}, {"type": "eq", "hz": 66, "gain_db": -11, "q": 1.4},
                    {"type": "eq", "hz": 105, "gain_db": 5, "q": 0.9}, {"type": "sat", "amount": 0.9}, {"type": "gain", "db": -0.5}]},
    # a 31 Hz thump under every kick: the floor of the kick, felt not heard
    "ksub": {"inst": {"type": "sine", "attack": 0.004, "release": 0.07}, "humanize_ms": 0, "vel_jitter": 0, "legato": 0.9,
             "fx": [{"type": "lpf", "hz": 60}], "gain_db": -6},
    "clap": {"inst": {"type": "handclap", "clappers": 5, "spread_ms": 8, "room": 0.3, "hands": "mixed"}, "humanize_ms": 1,
             "send_reverb": 0.22, "gain_db": -7, "width": 0.4, "fx": [{"type": "hpf", "hz": 250}]},
    "ohat": {"inst": {"type": "openhat", "decay": 0.09, "tone": 8500}, "humanize_ms": 1, "pan": 0.12, "gain_db": 9.5,
             "fx": [{"type": "highshelf", "hz": 9000, "gain_db": -6}, {"type": "lpf", "hz": 12000}]},
    "chh": {"inst": {"type": "hat", "decay": 0.028}, "humanize_ms": 1, "dyn": [0.35, 0.6, 0.45, 0.85], "pan": -0.18, "gain_db": 7,
            "fx": [{"type": "lpf", "hz": 10000}, {"type": "highshelf", "hz": 8000, "gain_db": -4}]},
    "snare": {"inst": {"type": "snare", "tone": 220, "decay": 0.11, "snap": 0.8}, "humanize_ms": 0, "send_reverb": 0.3, "gain_db": -11,
              "fx": [{"type": "hpf", "hz": 150}, {"type": "highshelf", "hz": 5000, "gain_db": -6}]},
    "bass": {"inst": {"type": "trancebass", "cutoff": 320, "env": 2400, "fdecay": 0.06, "sub": 0.25, "drive": 0.4, "reso": 0.25},
             "sidechain": {"source": "kick", "depth": 0.88, "release_ms": 90}, "humanize_ms": 0, "vel_jitter": 0.03,
             "fx": [{"type": "hpf", "hz": 24}, {"type": "lowshelf", "hz": 36, "gain_db": 1.5}, {"type": "eq", "hz": 42, "gain_db": -7, "q": 3.0}, {"type": "eq", "hz": 68, "gain_db": -8, "q": 1.0}, {"type": "eq", "hz": 140, "gain_db": 3, "q": 1.0}], "gain_db": 6},
    # the parent: the lead with an edge
    "lead": {"inst": {"type": "supersaw", "voices": 7, "detune": 20, "mix": 0.62, "spread": 0.85, "attack": 0.004, "release": 0.12,
                      "cutoff": 4200, "reso": 0.35, "env": 3000, "fdecay": 0.18},
             "sidechain": {"source": "kick", "depth": 0.3, "release_ms": 140},
             "fx": [{"type": "hpf", "hz": 300}, {"type": "sat", "amount": 0.35}, {"type": "eq", "hz": 2600, "gain_db": -2, "q": 1.2},
                    {"type": "eq", "hz": 7000, "gain_db": 2.5, "q": 0.8}],
             "send_reverb": 0.3, "send_delay": 0.22, "humanize_ms": 0, "legato": 0.62, "gain_db": 4},
    # gated minor pressure under it
    "saws": {"inst": {"type": "supersaw", "voices": 7, "detune": 22, "mix": 0.7, "attack": 0.01, "release": 0.2, "cutoff": 9000},
             "sidechain": {"source": "kick", "depth": 0.6, "release_ms": 150},
             "fx": [{"type": "hpf", "hz": 260}, {"type": "gate", "pattern": "x.xx.x.xx.x.xx.x", "depth": 0.9, "duty": 0.6, "smooth_ms": 4}],
             "send_reverb": 0.25, "send_delay": 0.1, "humanize_ms": 0, "gain_db": 7},
    # the tick: tuned, in key, on the grid
    "tick": {"inst": {"type": "supersaw", "voices": 3, "detune": 8, "sustain_level": 0.0, "decay": 0.07, "cutoff": 1800, "env": 7000,
                      "fdecay": 0.03, "release": 0.05, "reso": 0.3},
             "fx": [{"type": "hpf", "hz": 600}], "send_delay": 0.3, "send_reverb": 0.3, "humanize_ms": 0, "pan": 0.2, "gain_db": 10},
    # the daughter: the chop
    "chop": {"inst": {"type": "singer", "source": "svs", "voice": "leona-power", "svs_fade_in_ms": 3, "svs_fade_out_ms": 25},
             "sidechain": {"source": "kick", "depth": 0.2, "release_ms": 120},
             "send_reverb": 0.18, "reverb_predelay_ms": 60, "send_delay": 0.18,
             "fx": [{"type": "hpf", "hz": 220}, {"type": "eq", "hz": 800, "gain_db": -2.5, "q": 1.0}, {"type": "comp", "threshold_db": -24, "ratio": 5}, {"type": "highshelf", "hz": 8000, "gain_db": 2},
                    {"type": "gain", "db": 10}], "gain_db": 10},
    # the line with words
    "line": {"inst": {"type": "singer", "source": "svs", "voice": "hanami-power", "svs_fade_in_ms": 20, "svs_fade_out_ms": 120},
             "send_reverb": 0.4, "reverb_predelay_ms": 60, "send_delay": 0.25,
             "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 800, "gain_db": -2, "q": 0.9}, {"type": "comp", "threshold_db": -22, "ratio": 4},
                    {"type": "highshelf", "hz": 8000, "gain_db": 3}, {"type": "gain", "db": 10}], "gain_db": 10},
    # the daughter's edge: a hard, bright stab doubling each chop an octave up (the voice's teeth)
    "edge": {"inst": {"type": "supersaw", "voices": 3, "detune": 9, "mix": 0.5, "sustain_level": 0.0, "decay": 0.11, "cutoff": 2500, "reso": 0.55,
                      "env": 9000, "fdecay": 0.05, "release": 0.06, "transpose": 12},
             "sidechain": {"source": "kick", "depth": 0.2, "release_ms": 120},
             "fx": [{"type": "hpf", "hz": 1200}, {"type": "sat", "amount": 0.5}, {"type": "lpf", "hz": 11000}],
             "send_reverb": 0.15, "send_delay": 0.2, "humanize_ms": 0, "pan": -0.15, "width": 0.3, "gain_db": 13},
    # the far voice: the same line, wet and filtered (intro, breakdown, tail)
    "far": {"inst": {"type": "singer", "source": "svs", "voice": "hanami", "svs_fade_in_ms": 30, "svs_fade_out_ms": 200, "double": 0.25, "double_pan": 0.7},
            "send_reverb": 0.75, "reverb_predelay_ms": 60, "send_delay": 0.45,
            "fx": [{"type": "hpf", "hz": 200}, {"type": "eq", "hz": 800, "gain_db": -2, "q": 0.9}, {"type": "comp", "threshold_db": -22, "ratio": 3},
                   {"type": "highshelf", "hz": 8000, "gain_db": 2}, {"type": "gain", "db": 6}], "gain_db": 10, "width": 0.3},
    # dark wordless voices, a third apart, rocking F#-G: the nucleus
    "chD": {"inst": {"type": "singer", "source": "svs", "voice": "hanami-dark", "svs_fade_in_ms": 300, "svs_fade_out_ms": 400, "seed": 3},
            "sidechain": {"source": "kick", "depth": 0.75, "release_ms": 190},
            "send_reverb": 0.7, "send_delay": 0.15, "pan": -0.35,
            "fx": [{"type": "hpf", "hz": 220}, {"type": "gain", "db": -8}], "gain_db": 8},
    "chS": {"inst": {"type": "singer", "source": "svs", "voice": "leona-soft", "gender": -0.5, "svs_fade_in_ms": 300, "svs_fade_out_ms": 400, "seed": 5},
            "sidechain": {"source": "kick", "depth": 0.75, "release_ms": 190},
            "send_reverb": 0.7, "send_delay": 0.15, "pan": 0.35,
            "fx": [{"type": "hpf", "hz": 250}, {"type": "lpf", "hz": 6000}, {"type": "gain", "db": -8}], "gain_db": 8},
    "pad": {"inst": {"type": "supersaw", "voices": 7, "detune": 16, "mix": 0.6, "attack": 1.0, "release": 2.0, "cutoff": 1500},
            "sidechain": {"source": "kick", "depth": 0.75, "release_ms": 190},
            "fx": [{"type": "hpf", "hz": 200}], "send_reverb": 0.35, "humanize_ms": 0, "gain_db": 0, "width": 0.4},
}

T16 = [0, 2, 3, 6, 7, 10, 11, 14, 16, 18, 21, 22, 25, 27, 28, 30]
T8 = [0, 3, 7, 10, 16, 21, 25, 28]
T4 = [3, 10, 21, 28]
T2 = [3, 21]
T1 = [21]
ALT = {11: "F#6", 27: "G6", 3: "C#6"}
LINE = "0:F#4:4 4:A4:2 6:B4:6 12:A4:4 16:G4:14"
WORDS = ("half", "me", "light", "hold")

patterns = {
    "four": {"bars": 1, "kick": "x...x...x...x...", "ksub": "0:B0:1 4:B0:1 8:B0:1 12:B0:1"},
    "hats": {"bars": 1, "ohat": "..x...x...x...x.", "chh": "xxxxxxxxxxxxxxxx"},
    "claps": {"bars": 1, "clap": "....x.......x..."},
    "roll": {"bars": 8, "bass": roll(ROOTS)},
    "gated": {"bars": 8, "saws": {"chords": "F#m:48 G/F#:16 Bm/D:32 Em:16 G:16", "style": "sustain", "register": "C#4", "voicing": "close", "vel": 0.8}},
    "p8": {"bars": 8, "lead": cell(8, 4)},
    "c1": {"bars": 8, "chop": {"notes": "118:G4:2 120:G4:6", "lyrics": "hold hold"}},
    "p8call": {"bars": 8, "lead": cell(8, 3)},
    "call": {"bars": 8, "line": {"notes": "96:F#4:4 100:A4:2 102:B4:6 108:A4:4 112:G4:14", "lyrics": "half of me is light"}},
    "p4": {"bars": 8, "lead": cell(4, 4)},
    "d4": {"bars": 8, "chop": dict(zip(("notes", "lyrics"), chops(4, 4)))},
    "ticks": {"bars": 2, "tick": "2:C#6:1 7:C#6:1 11:F#6:1 14:C#6:1 21:C#6:1 27:G6:1 30:C#6:1"},
}

patterns.update({
    "four6": {"bars": 8, "kick": "x...x...x...x..." * 6 + "." * 32},
    "kdecayC": {"bars": 4, "kick": "x...x...x...x...|x...x...x...x...|x.......x.......|x...............",
                "ksub": "0:B0:1 4:B0:1 8:B0:1 12:B0:1 16:B0:1 20:B0:1 24:B0:1 28:B0:1 32:B0:1 40:B0:1 48:B0:1"},
    "kdecayD": {"bars": 4, "kick": "x...............|................|x...............|................", "ksub": "0:B0:1 32:B0:1"},
    "rollBD": {"bars": 16, "bass": roll(["F#1"] * 8 + ["D2"] * 4 + ["F#1"] * 4)},
    "rollO": {"bars": 8, "bass": roll(ROOTS, True)},
    "ticks16": {"bars": 2, "tick": steps(T16, alt=ALT)},
    "ticks8": {"bars": 2, "tick": steps(T8, alt=ALT)},
    "ticks4": {"bars": 2, "tick": steps(T4, alt=ALT)},
    "ticks2": {"bars": 2, "tick": steps(T2)},
    "ticks1": {"bars": 2, "tick": steps(T1)},
    "ticksBD": {"bars": 16, "tick": " ".join(steps(t, alt=ALT).replace(":1", ":1") if False else
                                             " ".join("%d:%s:1" % (x + off, ALT.get(x, "C#6")) for x in t)
                                             for t, off in [(T16, 0), (T8, 32), (T4, 64), (T2, 96), (T1, 128), (T1, 160), (T1, 192), (T1, 224)])},
    "p8m": {"bars": 8, "lead": cell(8, 4) + " " + cell(8, 4, octave=-1)},
    "p2": {"bars": 8, "lead": cell(2, 4)},
    "p1": {"bars": 8, "lead": cell(1, 4)},
    "p1x": {"bars": 4, "lead": cell(1, 2)},
    "d4": {"bars": 8, "chop": chops(4, 4, WORDS), "edge": chops(4, 4, WORDS)["notes"]},
    "d6": {"bars": 8, "chop": chops(2, 4, WORDS), "edge": chops(2, 4, WORDS)["notes"]},
    "d7": {"bars": 8, "chop": chops(1, 4, WORDS, rest_last=True), "edge": chops(1, 4, WORDS, rest_last=True)["notes"]},
    "t4": {"bars": 4, "chop": chops(4, 2, WORDS), "edge": chops(4, 2, WORDS)["notes"]},
    "t2": {"bars": 4, "chop": {"notes": "3:A4:2 19:A4:2 35:A4:2 51:A4:2", "lyrics": "half me light hold"}},
    "t1": {"bars": 4, "chop": {"notes": "19:A4:2 51:A4:2", "lyrics": "hold hold"}},
    # the far line
    "farI": {"bars": 8, "far": {"notes": LINE + " " + " ".join("%d:%s" % (int(t.split(":")[0]) + 64, t.split(":", 1)[1]) for t in LINE.split()),
                                "lyrics": "half of me is light half of me is light"}},
    "farB": {"bars": 16, "far": {"notes": " ".join("%d:%s" % (int(t.split(":")[0]) + 32, t.split(":", 1)[1]) for t in LINE.split())
                                 + " 128:F#4:4 132:A4:2 134:B4:6 140:A4:4 144:G4:10 156:B4:4 160:C#5:8 168:G4:16",
                                 "lyrics": "half of me is light half of what is left holds on _"}},
    "farEnd": {"bars": 4, "far": {"notes": "38:F#4:4 42:A4:2 44:B4:6 50:A4:4", "lyrics": "half of me is"}},
    "callD": {"bars": 8, "line": {"notes": "96:F#4:4 100:A4:2 102:B4:6 108:A4:4 112:G4:14", "lyrics": "half of me is light"}},
    # the dark voices and the pad
    "choir": {"bars": 16, "chD": {"notes": "0:F#4:60 64:G4:60 128:F#4:60 192:G4:60", "lyrics": "ah ah ah ah"},
              "chS": {"notes": "0:A4:60 64:B4:60 128:A4:60 192:B4:60", "lyrics": "ah ah ah ah"}},
    "choir8": {"bars": 8, "chD": {"notes": "0:F#4:44 48:G4:14 64:F#4:28 96:G4:30", "lyrics": "ah ah ah ah"},
               "chS": {"notes": "0:A4:44 48:B4:14 64:A4:28 96:B4:30", "lyrics": "ah ah ah ah"}},
    "pads": {"bars": 16, "pad": {"chords": "F#m:64 G/F#:64 Bm/D:64 G/F#:64", "style": "sustain", "register": "C#4", "voicing": "spread", "vel": 0.7}},
    "pads8": {"bars": 8, "pad": {"chords": "F#m:48 G/F#:16 Bm/D:32 Em:16 G:16", "style": "sustain", "register": "C#4", "voicing": "spread", "vel": 0.7}},
    # builds
    "b1chop": {"bars": 8, "chop": {"notes": "0:G4:4 16:G4:4 32:G4:4 40:G4:4 48:G4:4 56:G4:4 "
                                   + " ".join("%d:A4:2" % (66 + 4 * i) for i in range(4)) + " " + " ".join("%d:B4:2" % (82 + 4 * i) for i in range(4))
                                   + " " + " ".join("%d:C#5:2" % (96 + 2 * i) for i in range(8)), "lyrics": " ".join(["hold"] * 22)}},
    "roll8": {"bars": 8, "snare": "x...x...x...x...|x...x...x...x...|x.x.x.x.x.x.x.x.|x.x.x.x.x.x.x.x.|xxxxxxxxxxxxxxxx|xxxxxxxxxxxxxxxx|RRRRRRRRRRRRRRRR|RRRRRRRRRRRR...."},
    "roll4": {"bars": 4, "snare": "x...x...x...x...|x.x.x.x.x.x.x.x.|xxxxxxxxxxxxxxxx|xxxxxxxxRRRRRRRR"},
    "roll2": {"bars": 2, "snare": "RRRRRRRRRRRRRRRR|RRRRRRRR........", "kick": "x...x...x...x...|x...x..........."},
    "holdG": {"bars": 2, "chop": {"notes": "0:G4:34", "lyrics": "hold"}},
})

if MODE == "loop":
    arrangement = [
        {"name": "loop", "bars": 8, "play": ["four", "hats", "claps", "roll", "gated", "p8call", "call", "ticks"]},
        {"name": "loop2", "bars": 8, "play": ["four", "hats", "claps", "roll", "gated", "p4", "d4", "ticks"]},
    ]
else:
    arrangement = [
        # the voice opens; the roll and the tick are the pulse under it
        {"name": "intro", "bars": 8, "play": ["roll", "ticks", "farI", "c1"],
         "auto": {"bass": {"hpf": [140, 50], "gain_db": [-4, 0]}, "far": {"lpf": [1600, 6000], "gain_db": 2}, "tick": {"gain_db": [-4, 0]}}},
        {"name": "themeA", "bars": 8, "play": ["four", "roll", "ticks", "p8", "c1"], "enter": {"impact": 0.5},
         "auto": {"lead": {"lpf": [700, 1500]}, "kick": {"gain_db": -1.5}, "bass": {"gain_db": -2}}},
        {"name": "themeB", "bars": 8, "play": ["four", "hats", "claps", "roll", "ticks", "p8", "gated", "c1"],
         "auto": {"lead": {"lpf": [1500, 3200]}, "saws": {"lpf": [900, 2500], "gain_db": -3}, "kick": {"gain_db": -1.5}, "bass": {"gain_db": -2}}},
        {"name": "build1", "bars": 8, "play": ["four6", "hats", "roll", "gated", "roll8", "b1chop", "p8"],
         "auto": {"saws": {"hpf": [260, 1400], "lpf": [2500, 5000]}, "bass": {"hpf": [45, 400], "gain_db": [0, -4]}, "lead": {"hpf": [300, 2200], "gain_db": [0, -3]}, "ohat": {"gain_db": [0, -6]}, "snare": {"gain_db": [-12, 0]},
                  "chop": {"hpf": [1200, 250]}},
         "exit": {"riser": 6, "rise": 16, "cut": {"tracks": "all", "beats": 1}}},
        {"name": "drop1a", "bars": 8, "exit": {"cut": {"tracks": ["kick"], "beats": 1}}, "auto": {"saws": {"gain_db": -3, "lpf": 2400}, "line": {"gain_db": -2.5}, "chh": {"gain_db": -3}, "bass": {"gain_db": -1}, "lead": {"gain_db": -1}}, "play": ["four", "hats", "claps", "roll", "gated", "p8call", "callD", "ticks"], "enter": {"impact": 0.6, "crash": 0.7}},
        {"name": "drop1b", "bars": 8, "auto": {"saws": {"gain_db": [-2.5, -1], "lpf": [2400, 4200]}, "bass": {"gain_db": -1}, "lead": {"gain_db": -1}}, "play": ["four", "hats", "claps", "roll", "gated", "p8", "c1", "ticks"]},
        # breakdown: dense, then thinning; the roll never stops
        {"name": "breakdown", "bars": 16, "play": ["rollBD", "ticksBD", "pads", "farB", "choir"], "enter": {"downlifter": 4},
         "auto": {"bass": {"lpf": [400, 180], "gain_db": [-5, -10]}, "pad": {"gain_db": [-10, -3], "lpf": [900, 2600]}, "chD": {"gain_db": [-6, 0]}, "chS": {"gain_db": [-6, 0]}, "far": {"gain_db": 1}}},
        # build 2: the roll tightens, then stops early; the voice holds the G alone
        {"name": "build2a", "bars": 4, "play": ["four", "hats", "roll", "gated", "roll4", "p1x"],
         "auto": {"saws": {"hpf": [260, 900], "lpf": [2600, 4000]}, "bass": {"hpf": [45, 160]}, "snare": {"gain_db": [-12, -4]}}},
        {"name": "build2b", "bars": 2, "play": ["hats", "roll", "gated", "roll2"],
         "auto": {"saws": {"hpf": [900, 1800]}, "bass": {"hpf": [160, 350]}, "snare": {"gain_db": [-6, -4], "lpf": [9000, 6000]}},
         "exit": {"rise": 6, "cut": {"tracks": ["snare", "kick", "bass", "saws", "ohat", "chh"], "beats": 2}}},
        {"name": "hold", "bars": 2, "play": ["holdG", "ticks1"],
         "auto": {"bass": {"mute": True}, "saws": {"mute": True}, "snare": {"mute": True}, "kick": {"mute": True}, "chop": {"gain_db": -9}}},
        # main drop: four half-lives
        {"name": "mainA", "bars": 8, "exit": {"cut": {"tracks": ["kick"], "beats": 1}}, "auto": {"bass": {"gain_db": 1, "lpf": [500, 800]}, "saws": {"gain_db": 2, "lpf": [2600, 3200]}, "lead": {"gain_db": -1}, "chop": {"gain_db": 0}}, "play": ["four", "hats", "claps", "rollO", "gated", "p8m", "c1", "ticks"], "enter": {"impact": 0.8, "crash": 0.8}},
        {"name": "mainB", "bars": 8, "exit": {"reverse": 2, "cut": {"tracks": ["kick", "clap"], "beats": 1}}, "auto": {"bass": {"gain_db": 1, "lpf": [800, 1300]}, "saws": {"gain_db": 2, "lpf": [3200, 4500]}, "lead": {"gain_db": 1}, "chop": {"gain_db": 2.5}}, "play": ["four", "hats", "claps", "rollO", "gated", "p4", "d4", "ticks"]},
        {"name": "mainC", "bars": 8, "exit": {"cut": {"tracks": ["kick"], "beats": 1}}, "auto": {"bass": {"gain_db": 1, "lpf": [1300, 2600]}, "saws": {"gain_db": 3, "lpf": [4500, 7000]}, "lead": {"gain_db": 1}, "chop": {"gain_db": 2}, "edge": {"gain_db": 2}, "chh": {"gain_db": 1.5}, "ohat": {"gain_db": 1}, "pad": {"gain_db": -4}, "chD": {"gain_db": -2}, "chS": {"gain_db": -2}}, "play": ["four", "hats", "claps", "rollO", "gated", "p2", "d6", "ticks", "choir8", "pads8"], "enter": {"crash": 0.5}},
        {"name": "mainD", "bars": 8, "exit": {"reverse": 2, "cut": {"tracks": ["kick", "clap", "saws"], "beats": 2}}, "auto": {"bass": {"gain_db": 1, "lpf": [2600, 9000]}, "saws": {"gain_db": 4, "lpf": [7000, 12000]}, "lead": {"gain_db": 1}, "chop": {"gain_db": 3}, "edge": {"gain_db": 4}, "chh": {"gain_db": 3}, "ohat": {"gain_db": 2}, "line": {"gain_db": -1.5}, "pad": {"gain_db": -4}, "chD": {"gain_db": -2}, "chS": {"gain_db": -2}}, "play": ["four", "hats", "claps", "rollO", "gated", "p1", "d7", "callD", "ticks", "choir8", "pads8"]},
        # tail: the daughter decays too; never zero; cut off mid-phrase
        {"name": "tailA", "bars": 4, "play": ["four", "hats", "rollO", "p1x", "t4", "ticks4"], "enter": {"crash": 0.5}},
        {"name": "tailB", "bars": 4, "play": ["four", "hats", "rollO", "p1x", "t2", "ticks2"]},
        {"name": "tailC", "bars": 4, "play": ["kdecayC", "rollO", "p1x", "t1", "ticks1"]},
        {"name": "tailD", "bars": 4, "play": ["kdecayD", "roll", "p1x", "ticks1", "farEnd"], "auto": {"far": {"gain_db": 3}, "lead": {"gain_db": 2}}},
    ]

project = {
    "title": "decay", "bpm": 140, "swing": 0.5, "seed": 13,
    "tracks": tracks, "patterns": patterns, "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.88, "damping": 0.5, "return_db": -6, "lpf": 7500},
            "delay": {"beats": 0.75, "feedback": 0.42, "return_db": -9, "lpf": 4200}},
    "master": {"lufs": -10, "sat": 0.1, "glue": True},
}
json.dump(project, open("project.json", "w"), indent=1)
print("wrote project.json:", MODE, sum(s["bars"] for s in arrangement), "bars")
