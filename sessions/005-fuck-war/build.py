#!/usr/bin/env python3
"""Spectre's builder for session 005: writes project.json. Edit here, run, render."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def trem(note, start, length, vel_hi=0.9, vel_lo=0.6, step=0.5):
    """tremolo roll (tsymbaly) of repeated 32nds"""
    out, s, i = [], start, 0
    while s < start + length - 1e-9:
        v = vel_hi if i == 0 else (0.75 if i % 2 == 0 else vel_lo)
        out.append(f"{s:g}:{note}:{step:g}:{v:.2f}")
        s += step
        i += 1
    return " ".join(out)


tracks = {
    # ---------------- the war
    "siren": {"inst": {"type": "lead", "cutoff": 4000, "square": 0.5, "vibrato": 0.0, "glide_ms": 2600, "attack": 0.6, "release": 0.08, "transpose": -0.35},
              "gain_db": -5, "width": 0.8, "humanize_ms": 0, "vel_jitter": 0, "send_reverb": 0.5,
              "fx": [{"type": "hpf", "hz": 400}, {"type": "drive", "db": 14}, {"type": "eq", "hz": 2200, "gain_db": 4, "q": 0.7}, {"type": "lpf", "hz": 5000}]},
    "clank": {"inst": {"type": "rim"}, "gain_db": -4, "pan": 0.35, "humanize_ms": 0, "vel_jitter": 0,
              "dyn": [1.0, 0.7, 0.85, 0.7], "swing": 0.5,
              "fx": [{"type": "hpf", "hz": 500}, {"type": "srr", "hz": 6000}, {"type": "bitcrush", "bits": 6}, {"type": "drive", "db": 6}]},
    "engine": {"inst": {"type": "bass", "cutoff": 260, "sub": 0.2, "drive": 0.8, "attack": 0.4, "release": 0.05, "transpose": -0.35},
               "gain_db": -2, "humanize_ms": 0, "vel_jitter": 0,
               "fx": [{"type": "hpf", "hz": 70}, {"type": "drive", "db": 12}, {"type": "tremolo", "rate": 9.33, "depth": 0.35}, {"type": "hpf", "hz": 120},
                      {"type": "eq", "hz": 400, "gain_db": 3, "q": 1.0}, {"type": "lpf", "hz": 1200}, {"type": "gain", "db": -10}]},
    # ---------------- the beat
    "kick": {"inst": {"type": "kick", "tune": 62, "decay": 0.16, "punch": 1.6, "click": 0.7, "drive": 0.6},
             "gain_db": -2, "humanize_ms": 1,
             "fx": [{"type": "drive", "db": 4}, {"type": "eq", "hz": 62, "gain_db": -3, "q": 1.2}, {"type": "eq", "hz": 95, "gain_db": 4, "q": 1.0},
                    {"type": "eq", "hz": 2500, "gain_db": 3, "q": 0.9}, {"type": "gain", "db": -4}]},
    "snare": {"inst": {"type": "snare", "tone": 210, "decay": 0.05, "snap": 0.7, "body": 1.2, "drive": 0.9},
              "gain_db": 3, "humanize_ms": 1, "send_reverb": 0.0,
              "fx": [{"type": "hpf", "hz": 130}, {"type": "drive", "db": 6}, {"type": "eq", "hz": 1800, "gain_db": 3, "q": 1.0}, {"type": "highshelf", "hz": 3500, "gain_db": -4}]},
    # 2026-11-24 (owner's request, off-beat audit): the old `clap` here took `spread` in seconds, so its 3-burst
    # clap never sounded (a bare 4 ms click, the later bursts fell outside its buffer or played off the beat).
    # Replaced by `handclap` (model 2), drive dropped, peaks 6 dB under the kick. It was:
    # "clap": {"inst": {"type": "clap", "tone": 1100, "decay": 0.07, "spread": 1.0}, "gain_db": 14, "push_ms": -5, "width": 0.8, "send_reverb": 0.04, "fx": [{"type": "hpf", "hz": 200}, {"type": "drive", "db": 5}, {"type": "highshelf", "hz": 4500, "gain_db": -2}]},
    "clap": {"inst": {"type": "handclap", "clappers": 5, "spread_ms": 9}, "gain_db": -10.6, "width": 0.8, "push_ms": -5, "send_reverb": 0.04, "fx": [{"type": "hpf", "hz": 200}, {"type": "highshelf", "hz": 4500, "gain_db": -2}]},
    "hat": {"inst": {"type": "hat", "decay": 0.03, "tone": 8500}, "gain_db": 9, "pan": 0.2, "humanize_ms": 2,
            "dyn": [1.0, 0.55, 0.8, 0.6], "fx": [{"type": "hpf", "hz": 400}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
    "808": {"inst": {"type": "808", "decay": 1.0, "drive": 0.7, "punch": 0.7, "tone": 0.45, "glide_ms": 80},
            "gain_db": -6, "legato": 0.95, "sidechain": {"source": "kick", "depth": 0.55, "release_ms": 90},
            "fx": [{"type": "drive", "db": 9}, {"type": "sat", "amount": 0.4}, {"type": "eq", "hz": 41, "gain_db": -7, "q": 1.4},
                   {"type": "eq", "hz": 52, "gain_db": 4, "q": 1.2}, {"type": "eq", "hz": 82, "gain_db": 4, "q": 0.8}, {"type": "eq", "hz": 123, "gain_db": 3, "q": 1.0}, {"type": "eq", "hz": 165, "gain_db": 3, "q": 1.0},
                   {"type": "lpf", "hz": 3000}, {"type": "gain", "db": -6}]},
    # ---------------- the people
    "choir": {"inst": {"type": "choir", "vowel": "ah", "attack": 0.03, "release": 0.25},
              "gain_db": 16, "pan": -0.3, "width": 0.5, "humanize_ms": 12, "push_ms": 10, "send_reverb": 0.25,
              "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 650, "gain_db": -3, "q": 1.2}, {"type": "drive", "db": 7}, {"type": "eq", "hz": 550, "gain_db": -3, "q": 0.9},
                     {"type": "eq", "hz": 1600, "gain_db": 3, "q": 0.8}, {"type": "eq", "hz": 4800, "gain_db": 3, "q": 0.9}]},
    "choirHi": {"inst": {"type": "choir", "vowel": "ee", "attack": 0.04, "release": 0.25, "transpose": 12},
                "gain_db": 12, "pan": 0.35, "width": 0.5, "humanize_ms": 15, "push_ms": 16, "send_reverb": 0.3,
                "fx": [{"type": "hpf", "hz": 400}, {"type": "drive", "db": 8}, {"type": "eq", "hz": 2500, "gain_db": 3, "q": 0.8},
                       {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
    "drone": {"inst": {"type": "choir", "vowel": "oh", "attack": 0.3, "release": 0.6},
              "gain_db": 5, "width": 0.7, "humanize_ms": 20, "send_reverb": 0.3,
              "fx": [{"type": "hpf", "hz": 140}, {"type": "drive", "db": 4}, {"type": "eq", "hz": 480, "gain_db": -4, "q": 0.9}]},
    "shout": {"inst": {"type": "choir", "vowel": "ah", "attack": 0.005, "release": 0.12},
              "gain_db": 12, "width": 0.9, "humanize_ms": 8, "send_reverb": 0.15,
              "fx": [{"type": "hpf", "hz": 200}, {"type": "drive", "db": 14}, {"type": "eq", "hz": 1400, "gain_db": 4, "q": 0.8},
                     {"type": "highshelf", "hz": 6000, "gain_db": -1}]},
    "shout2": {"inst": {"type": "choir", "vowel": "oh", "attack": 0.01, "release": 0.2},
               "gain_db": 13, "width": 0.9, "humanize_ms": 10, "send_reverb": 0.2,
               "fx": [{"type": "hpf", "hz": 200}, {"type": "drive", "db": 14}, {"type": "eq", "hz": 1100, "gain_db": 3, "q": 0.8},
                      {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
    "choirLo": {"inst": {"type": "choir", "vowel": "ah", "attack": 0.04, "release": 0.25, "transpose": -12},
                "gain_db": 10, "pan": 0.0, "width": 0.8, "humanize_ms": 18, "push_ms": 14, "send_reverb": 0.25,
                "fx": [{"type": "hpf", "hz": 160}, {"type": "drive", "db": 7}, {"type": "eq", "hz": 520, "gain_db": -4, "q": 0.9}]},
    "cry": {"inst": {"type": "choir", "vowel": "ee", "attack": 0.08, "release": 0.4},
            "gain_db": 17, "pan": 0.1, "width": 0.6, "humanize_ms": 10, "push_ms": 12, "send_reverb": 0.35, "send_delay": 0.1,
            "fx": [{"type": "hpf", "hz": 500}, {"type": "drive", "db": 10}, {"type": "eq", "hz": 3000, "gain_db": -2, "q": 1.0},
                   {"type": "highshelf", "hz": 6000, "gain_db": -5}]},
    "lira": {"inst": {"type": "lira", "buzz": 0.35, "buzz_rate": 9.33, "attack": 0.3, "release": 0.6},
             "gain_db": 2, "pan": -0.2, "width": 0.4, "send_reverb": 0.2, "fx": [{"type": "hpf", "hz": 150}]},
    "trembita": {"inst": {"type": "trembita", "attack": 0.35, "bright": 0.45, "blare": 0.2, "breath": 0.15},
                 "gain_db": 4, "pan": 0.0, "send_reverb": 0.7, "send_delay": 0.15, "fx": [{"type": "hpf", "hz": 70}]},
    "fiddle": {"inst": {"type": "fiddle", "vibrato": 0.25, "grit": 0.45, "bow_noise": 0.15, "glide_ms": 90},
               "gain_db": 4, "pan": 0.25, "legato": 0.95, "humanize_ms": 10, "push_ms": 15, "send_reverb": 0.35,
               "fx": [{"type": "hpf", "hz": 250}, {"type": "drive", "db": 4}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
    "shaker": {"inst": {"type": "shaker"}, "gain_db": 2, "pan": -0.4, "humanize_ms": 9, "push_ms": 8, "vel_jitter": 0.15,
               "fx": [{"type": "hpf", "hz": 600}]},
    "tsym": {"inst": {"type": "cimbalom", "hard": 0.8, "damp": 0.35}, "gain_db": 1, "pan": 0.45, "humanize_ms": 7, "push_ms": 12, "vel_jitter": 0.1,
             "send_reverb": 0.15, "fx": [{"type": "hpf", "hz": 150}, {"type": "drive", "db": 3}, {"type": "eq", "hz": 500, "gain_db": -3, "q": 1.0}]},
}

MEL = "0:B4:3 3:B4:1 4:C#5:2 6:B4:2 8:A#4:4 12:G4:2 14:A#4:2 16:B4:6 22:A#4:2 24:G4:2 26:F#4:2 28:E4:4 " \
      "32:E4:2 34:G4:2 36:A#4:3 39:G4:1 40:F#4:4 44:E4:2 46:D4:2 48:E4:6"
SHOUT = "56:E3:1.5! 56:B3:1.5! 56:E4:1.5! 56:B4:1.5!"                       # FUCK: short, clipped, open fifths
SHOUT2 = "60:E3:4! 60:B3:4! 60:E4:4! 60:G4:4!"                              # WAR: longer, rounder, falling to G

def tsym_bar(o):
    return f"{o}:E3:2 {o+2}:B3:1 {o+3}:E4:1 {o+4}:B3:2 {o+6}:E4:2 {o+8}:E3:2 {o+10}:B3:1 {o+11}:E4:1 {o+12}:A#3:2 {o+14}:B3:2"


TSYM = " ".join(tsym_bar(o) for o in (0, 16, 32)) + " " + trem("B4", 48, 8, 0.7, 0.45) + " " + trem("E4", 48, 8, 0.6, 0.4) \
       + " 56:E4:2! 56:B4:2! 60:E4:3! 60:G4:3!"

TSYM_V = " ".join(tsym_bar(o) for o in (0, 16, 32, 48))
TSYM_V8 = " ".join(tsym_bar(o) for o in (0, 16, 32, 48, 64, 80, 96)) + " " + trem("B4", 112, 8, 0.7, 0.45) + " " + trem("E4", 112, 8, 0.6, 0.4) \
          + " 120:E4:2! 120:B4:2! 124:E4:3! 124:G4:3!"
MEL3 = " ".join(t for t in MEL.split() if float(t.split(":")[0]) < 48)
HOLD = "0:B4:30 32:A#4:30 0:E4:30 32:E4:30 0:B3:62 0:E3:62"


def shift(seq, o):
    out = []
    for t in seq.split():
        f = t.split(":")
        f[0] = f"{float(f[0]) + o:g}"
        out.append(":".join(f))
    return " ".join(out)


patterns = {
    "beat": {"bars": 4,
             "kick":  "X.....x...x....." "X.....x...x..x.." "X.....x...x....." "X.....x.X...X...",
             "snare": "........X......." "........X......." "........X......." "........X...X...",
             "clap":  "........X......." "........X......." "........X......." "........X...X...",
             "hat":   "x.x.x.x.x.x.x.x." "x.x.x.x.x.xtx.x." "x.x.x.x.x.x.x.x." "x.x.x.x........."},
    "bass": {"bars": 4,
             "808": "0:E1:6! 6:E1:2 10:E1:4 14:G1:2~ 16:E1:6 22:E1:2 26:D1:4 30:E1:2~ "
                    "32:E1:6 38:E1:2 42:E1:4 46:A#1:2~ 48:E1:6 56:E1:3! 60:E1:4!"},
    "mel": {"bars": 4, "choir": MEL, "choirHi": MEL, "drone": "0:E3:30 0:B3:30 32:E3:22 32:B3:22"},
    "mel1": {"bars": 4, "choir": MEL, "drone": "0:E3:30 0:B3:30 32:E3:22 32:B3:22"},
    "melBig": {"bars": 4, "choir": MEL, "choirHi": MEL, "choirLo": MEL, "drone": "0:E3:30 0:B3:30 32:E3:22 32:B3:22"},
    "solo": {"bars": 4, "choir": MEL3},
    "tsymA": {"bars": 4, "tsym": TSYM},
    "shoutP": {"bars": 4, "shout": SHOUT, "shout2": SHOUT2},
    "hitDrums": {"bars": 4, "kick": "." * 56 + "X...X...", "snare": "." * 56 + "X...X...", "clap": "." * 56 + "X...X...",
                 "808": "56:E1:3! 60:E1:4!", "tsym": "56:E4:2! 56:B4:2! 60:E4:3! 60:G4:3!"},
    # the war machine: it runs until the people shout, then it is silenced for two beats
    "machine": {"bars": 4, "clank": "xxxxxxxxxxxxxxxx" * 3 + "xxxxxxxx........",
                "engine": "0:E2:56", "siren": "0:B3:2 2:E5:30~ 32:E5:8 40:B3:16~"},
    "machineFull": {"bars": 4, "clank": "xxxxxxxxxxxxxxxx" * 4, "engine": "0:E2:64", "siren": "0:B3:2 2:E5:30~ 32:E5:8 40:B3:24~"},
    "machineV": {"bars": 8, "clank": "x.xxx.xxx.xxx.xx" * 7 + "x.xxx.xx........", "engine": "0:E2:120",
                 "siren": "64:B3:2 66:E5:30~ 96:E5:8 104:B3:16~"},
    "machineBroken": {"bars": 8, "clank": "x..x....x...x..." "................" "x.x.xx.........." "........" "x..x...." 
                      "x..x....x...x..." "................" "x.xxx..........." "................",
                      "engine": "0:E2:20 32:E2:12 80:E2:16"},
    # verse: room for the rapper
    "beatV": {"bars": 8,
              "kick":  ("X.........x....." "X.....x........." ) * 3 + "X.........x....." "X.......X...X...",
              "snare": "........X......." * 7 + "........X...X...",
              "clap":  "........X......." * 7 + "........X...X...",
              "hat":   ("x.x.x.x.x.x.x.x." "x.x.x.x.x.x.xrx.") * 3 + "x.x.x.x.x.x.x.x." "x.x.x.x........."},
    "bassV": {"bars": 8, "808": "0:E1:10! 10:E1:6 16:E1:12 28:D1:4~ 32:E1:10! 42:E1:6 48:E1:8 56:G1:4~ 60:A#1:4~ "
                                "64:E1:10! 74:E1:6 80:E1:12 92:D1:4~ 96:E1:10! 106:E1:6 112:E1:6 120:E1:3! 124:E1:4!"},
    "tsymV8": {"bars": 8, "tsym": TSYM_V8},
    "liraP": {"bars": 4, "lira": "0:E3:64 0:B3:64"},
    "shoutV": {"bars": 8, "shout": shift(SHOUT, 64), "shout2": shift(SHOUT2, 64)},
    # the cost: silence, the death horn, a lament
    "costP": {"bars": 8,
              "trembita": "16:B2:8 24:E3:12~ 36:E3:4 40:B2:12~ 52:E2:12~",
              "lira": "64:E3:62 64:B3:62",
              "fiddle": "64:B4:6 70:C#5:2~ 72:B4:2 74:A#4:2 76:G4:4 80:A#4:3 83:G4:1 84:F#4:4 88:E4:8 "
                        "96:G4:2 98:F#4:2 100:E4:4 104:D4:2 106:E4:16~"},
    # refusal: the voices come back and hold against the machine
    "holdP": {"bars": 4, "choir": HOLD, "choirHi": "0:B4:30 32:A#4:30", "drone": "0:E3:62 0:B3:62"},
    "sirenDie": {"bars": 4, "siren": "0:E5:8 8:C#5:8~ 16:A#4:8~ 24:F#4:8~ 32:E4:8~ 40:B3:8~ 48:E3:12~",
                 "clank": "x.x.x.x.x..x...x" "..x....x.....x.." "......x........." "................"},
    "peopleBeat": {"bars": 4, "kick": "X......x..x....." "X......x..x..x.." "X......x..x....." "X.......X...X...",
                   "clap": "........X......o" "........X..o...." "........X......o" "........X...X...",
                   "snare": "." * 56 + "X...X...",
                   "shaker": "xoxoxoxoxoxoxoxo" * 3 + "xoxoxoxo........"},
    "people": {"bars": 4, "shaker": "xoxoxoxoxoxoxoxo" * 3 + "xoxoxoxo........"},
    "cryP": {"bars": 4, "cry": "0:B5:10 10:C#6:2 12:B5:4 16:A#5:8 24:G5:4 28:A#5:4 32:B5:12 44:A#5:2 46:G5:2 48:F#5:4 52:E5:4"},
    "humP": {"bars": 8, "drone": "0:E3:30 0:B3:30 32:E3:30 32:A#3:30 64:E3:30 64:B3:30 96:E3:22 96:G3:22"},
    "lastCall": {"bars": 4, "trembita": "18:E2:30 48:B1:12~"},
    "fiddleV": {"bars": 8, "fiddle": "0:B4:14 16:A#4:14 32:G4:14 48:F#4:6 54:E4:8 64:E4:14 80:G4:14 96:A#4:12 108:B4:4~ 112:B4:6"},
}

arrangement = [
    {"name": "alarm", "bars": 8, "play": ["machineFull"],
     "auto": {"clank": {"gain_db": [-14, 0]}, "engine": {"gain_db": [-10, 0]}},
     "exit": {"cut": {"tracks": "all", "beats": 1}}},
    {"name": "voice", "bars": 4, "play": ["solo", "liraP", "hitDrums", "shoutP"],
     "auto": {"lira": {"gain_db": [-12, -4]}}},
    {"name": "hook1", "bars": 8, "play": ["beat", "bass", "mel1", "tsymA", "shoutP", "machine"],
     "auto": {"shout": {"gain_db": [-4, -4]}, "shout2": {"gain_db": [-4, -4]}}},
    {"name": "verse1", "bars": 8, "play": ["beatV", "bassV", "tsymV8", "liraP", "machineV", "shoutV"],
     "auto": {"clank": {"gain_db": [-6, -6]}, "lira": {"gain_db": [-8, -8]}, "tsym": {"gain_db": [-5, -5]}, "808": {"gain_db": [-2, -2]}}},
    {"name": "verse1b", "bars": 8, "play": ["beatV", "bassV", "tsymV8", "liraP", "machineV", "shoutV", "humP"],
     "auto": {"clank": {"gain_db": [-6, -3]}, "lira": {"gain_db": [-8, -8]}, "tsym": {"gain_db": [-5, -5]}, "808": {"gain_db": [-2, -2]},
              "drone": {"gain_db": [0, 7]}}},
    {"name": "hook2", "bars": 8, "play": ["beat", "bass", "mel", "tsymA", "shoutP", "machine"],
     "exit": {"cut": {"tracks": "all", "beats": 1}}},
    {"name": "cost", "bars": 8, "play": ["costP"],
     "auto": {"808": {"mute": True}, "kick": {"mute": True}, "shout2": {"mute": True}, "tsym": {"mute": True},
              "lira": {"gain_db": [-10, -4], "lpf": [1200, 3000]}}},
    {"name": "refuse", "bars": 4, "play": ["machineFull", "holdP"],
     "auto": {"choir": {"gain_db": [-10, 2]}, "choirHi": {"gain_db": [-10, 2]}}},
    {"name": "drown", "bars": 4, "play": ["sirenDie", "peopleBeat", "tsymA", "mel", "shoutP"],
     "auto": {"siren": {"gain_db": [0, -14]}}},
    {"name": "verse2", "bars": 16, "play": ["beatV", "bassV", "tsymV8", "liraP", "fiddleV", "machineBroken", "shoutV"],
     "auto": {"lira": {"gain_db": [-8, -8]}, "tsym": {"gain_db": [-5, -5]}, "808": {"gain_db": [-2, -2]}},
     "exit": {"cut": {"tracks": ["kick", "808", "hat", "snare", "clap", "tsym", "clank", "engine", "fiddle", "lira"], "beats": 4}}},
    {"name": "hook3", "bars": 8, "play": ["beat", "bass", "melBig", "tsymA", "shoutP", "people"],
     "auto": {"choir": {"gain_db": [3, 3]}, "choirHi": {"gain_db": [3, 3]}, "choirLo": {"gain_db": [3, 3]},
              "shout": {"gain_db": [3, 3]}, "shout2": {"gain_db": [3, 3]}, "clap": {"gain_db": [3, 3]}}},
    {"name": "hook3b", "bars": 8, "play": ["beat", "bass", "melBig", "tsymA", "shoutP", "people", "cryP"],
     "auto": {"choir": {"gain_db": [3, 3]}, "choirHi": {"gain_db": [3, 4]}, "choirLo": {"gain_db": [3, 3]},
              "shout": {"gain_db": [3, 4]}, "shout2": {"gain_db": [3, 4]}, "clap": {"gain_db": [3, 3]}}},
    {"name": "outro", "bars": 8, "play": ["mel", "liraP", "shoutP"],
     "auto": {"lira": {"gain_db": [-6, -10]}}},
    {"name": "end", "bars": 4, "play": ["lastCall"], "auto": {"trembita": {"gain_db": [-2, -12]}}},
]

project = {"title": "Fuck Every War", "bpm": 140, "swing": 0.5, "seed": 5,
           "tracks": tracks, "patterns": patterns, "arrangement": arrangement,
           "mix": {"reverb": {"size": 0.7, "damping": 0.55, "return_db": -5, "lpf": 6500},
                   "delay": {"beats": 0.75, "feedback": 0.3, "return_db": -8, "lpf": 3000}},
           "master": {"lufs": -10.5, "sat": 0.15, "tape": 0.0, "glue": True}}

with open(os.path.join(HERE, "project.json"), "w") as f:
    json.dump(project, f, indent=1)
print("wrote project.json")
