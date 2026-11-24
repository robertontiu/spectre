#!/usr/bin/env python3
"""Spectre's builder for session 007: writes project.json. Edit here, run, render."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

SC_BASS = {"source": "kick", "depth": 0.88, "release_ms": 95}
SC_MUSIC = {"source": "kick", "depth": 0.6, "release_ms": 160}

tracks = {
    # ---------------- the heart
    "kick": {"inst": {"type": "clubkick", "tune": 56, "tail": 0.05, "hold": 0.022, "punch": 1.4, "click": 0.2, "top": 0.05, "drive": 0.3},
             "humanize_ms": 0, "vel_jitter": 0.02,
             "fx": [{"type": "hpf", "hz": 40}, {"type": "eq", "hz": 55, "gain_db": -5, "q": 0.8},
                    {"type": "eq", "hz": 66, "gain_db": -11, "q": 1.4}, {"type": "eq", "hz": 105, "gain_db": 5, "q": 0.9},
                    {"type": "sat", "amount": 0.9}, {"type": "gain", "db": 1}]},
    # v029 (owner's request): the old `clap` here ("spread": 0.6 is in seconds: one 4 ms click plus a stray second
    # click 0.6 s later, turned up 10 dB and saturated) is replaced by the synthesized `handclap`, peaks about
    # 6 dB under the kick. Until v028 it was:
    # {"inst": {"type": "clap", "tone": 1200, "decay": 0.2, "spread": 0.6}, "humanize_ms": 1, "send_reverb": 0.25,
    #  "gain_db": 10, "width": 0.4, "fx": [{"type": "sat", "amount": 0.5}, {"type": "highshelf", "hz": 10000, "gain_db": -5}, {"type": "gain", "db": -2.5}]}
    "clap": {"inst": {"type": "handclap", "clappers": 5, "spread_ms": 9, "room": 0.3}, "humanize_ms": 1, "send_reverb": 0.25,
             "gain_db": -7, "width": 0.4, "fx": [{"type": "hpf", "hz": 250}]},
    "ohat": {"inst": {"type": "openhat", "decay": 0.1, "tone": 8500}, "humanize_ms": 1, "pan": 0.12, "gain_db": 8,
             "fx": [{"type": "highshelf", "hz": 9000, "gain_db": -6}, {"type": "lpf", "hz": 12000}, {"type": "eq", "hz": 6500, "gain_db": 2, "q": 1.0}]},
    "chh": {"inst": {"type": "shaker"}, "humanize_ms": 2, "dyn": [0.3, 0.55, 0.4, 0.75], "pan": -0.2,
            "gain_db": 4, "fx": [{"type": "lpf", "hz": 9000}, {"type": "highshelf", "hz": 7000, "gain_db": -4}]},
    "bass": {"inst": {"type": "trancebass", "cutoff": 300, "env": 2000, "fdecay": 0.07, "sub": 0.25, "drive": 0.35},
             "sidechain": SC_BASS, "humanize_ms": 0, "vel_jitter": 0.03,
             "fx": [{"type": "hpf", "hz": 45}, {"type": "eq", "hz": 68, "gain_db": -8, "q": 1.0},
                    {"type": "eq", "hz": 140, "gain_db": 3, "q": 1.0}]},
    # ---------------- the light
    "lead": {"inst": {"type": "supersaw", "voices": 9, "detune": 24, "mix": 0.72, "spread": 0.9,
                      "attack": 0.008, "release": 0.4, "cutoff": 5200, "env": 1800, "fdecay": 0.25},
             "sidechain": {"source": "kick", "depth": 0.3, "release_ms": 150},
             "fx": [{"type": "hpf", "hz": 300}, {"type": "eq", "hz": 2600, "gain_db": -2.5, "q": 1.2},
                    {"type": "highshelf", "hz": 10000, "gain_db": -3}, {"type": "eq", "hz": 6000, "gain_db": 2.5, "q": 0.8}, {"type": "chorus", "rate": 0.3, "depth": 0.25, "mix": 0.25}],
             "send_reverb": 0.45, "send_delay": 0.28, "humanize_ms": 0, "gain_db": 9},
    "saws": {"inst": {"type": "supersaw", "voices": 7, "detune": 22, "mix": 0.7, "attack": 0.01, "release": 0.25,
                      "cutoff": 6000},
             "sidechain": SC_MUSIC,
             "fx": [{"type": "hpf", "hz": 250},
                    {"type": "gate", "pattern": "x.xx.xx.x.xx.x.x", "depth": 0.85, "duty": 0.75, "smooth_ms": 4}],
             "send_reverb": 0.3, "send_delay": 0.12, "humanize_ms": 0, "gain_db": 6},
    "lead2": {"inst": {"type": "supersaw", "voices": 7, "detune": 18, "mix": 0.6, "spread": 1.0, "transpose": 12,
                       "attack": 0.01, "release": 0.5, "cutoff": 6000},
              "sidechain": {"source": "kick", "depth": 0.3, "release_ms": 150},
              "fx": [{"type": "hpf", "hz": 900}, {"type": "highshelf", "hz": 8000, "gain_db": -4}],
              "send_reverb": 0.55, "send_delay": 0.3, "humanize_ms": 0, "gain_db": 4},
    "pluck": {"inst": {"type": "supersaw", "voices": 5, "detune": 14, "sustain_level": 0.0, "decay": 0.18, "cutoff": 800,
                       "env": 5000, "fdecay": 0.07, "release": 0.12, "transpose": -12},
              "fx": [{"type": "hpf", "hz": 250}], "send_delay": 0.35, "send_reverb": 0.3, "humanize_ms": 0, "pan": 0.1,
              "gain_db": 6},
    "arp": {"inst": {"type": "supersaw", "voices": 5, "detune": 12, "sustain_level": 0.0, "decay": 0.14, "cutoff": 1200,
                     "env": 4000, "fdecay": 0.06, "release": 0.1},
            "sidechain": {"source": "kick", "depth": 0.45, "release_ms": 120},
            "fx": [{"type": "hpf", "hz": 300}], "send_delay": 0.25, "send_reverb": 0.25, "humanize_ms": 0, "pan": -0.1,
            "gain_db": 11, "width": 0.3},
    "pad": {"inst": {"type": "supersaw", "voices": 7, "detune": 16, "mix": 0.6, "attack": 1.4, "release": 2.5, "cutoff": 2200},
            "sidechain": {"source": "kick", "depth": 0.5, "release_ms": 180},
            "fx": [{"type": "hpf", "hz": 200}], "send_reverb": 0.55, "humanize_ms": 0, "gain_db": 2, "width": 0.4},
    "vox": {"inst": {"type": "vox", "voice": "soprano", "vowel": "ah", "vowel2": "oo", "morph": 1.6, "vibrato": 0.28,
                     "breath": 0.25, "glide_ms": 140, "attack": 0.08, "release": 0.6},
            "send_reverb": 0.6, "send_delay": 0.25, "fx": [{"type": "hpf", "hz": 220}], "humanize_ms": 10, "gain_db": -3},
    "choir": {"inst": {"type": "choir", "vowel": "ah", "attack": 0.4, "release": 1.5},
              "sidechain": {"source": "kick", "depth": 0.4, "release_ms": 180},
              "fx": [{"type": "hpf", "hz": 250}], "send_reverb": 0.5, "humanize_ms": 6, "gain_db": 10, "width": 0.8},
    "snare": {"inst": {"type": "snare", "tone": 220, "decay": 0.11, "snap": 0.8}, "humanize_ms": 0, "send_reverb": 0.3,
              "gain_db": -11, "fx": [{"type": "hpf", "hz": 150}, {"type": "highshelf", "hz": 5000, "gain_db": -6}]},
}


def shift(spec, octaves=0, stretch=1, offset=0):
    """octave-shift / time-stretch a note string"""
    out = []
    for tok in spec.split():
        st, note, ln = tok.split(":")[:3]
        name, octv = note[:-1], int(note[-1])
        out.append(f"{int(st) * stretch + offset}:{name}{octv + octaves}:{ln if stretch == 1 else int(ln) * stretch}")
    return " ".join(out)


GROOVE = "Fm:16 Db:16 Ab:16 Eb:8 Ebsus4:8"
LIGHT = "Db:16 Ab:16 Eb:16 Eb:8 F:8"
HOOK_DARK = ("0:C5:3 3:F5:3 6:Ab5:2 8:G5:4 12:F5:4 "
             "16:F5:3 19:Ab5:3 22:Db6:2 24:C6:8 "
             "32:C6:3 35:Eb6:3 38:C6:2 40:Bb5:4 44:Ab5:4 "
             "48:G5:3 51:Bb5:3 54:C6:2 56:Ab5:8")
HOOK_LIGHT = HOOK_DARK.replace("56:Ab5:8", "56:A5:8")
HOOK_HIGH = ("0:F5:3 3:Ab5:3 6:C6:2 8:Db6:4 12:C6:4 "
             "16:C6:3 19:Eb6:3 22:F6:2 24:Eb6:8 "
             "32:Eb6:3 35:G6:3 38:Eb6:2 40:Db6:4 44:C6:4 "
             "48:Bb5:3 51:Eb6:3 54:C6:2 56:A5:8")
HOOK_WAVE = HOOK_LIGHT + " " + shift(HOOK_HIGH, 0, 1, 64)
GROOVE_SLOW = "Fm:32 Db:32 Ab:32 Eb:16 Ebsus4:16"
LIGHT_SLOW = "Db:32 Ab:32 Eb:32 Eb:16 F:16"
VOX_DARK = shift(HOOK_DARK, -1, 2)
VOX_LIGHT = shift(HOOK_LIGHT, -1, 2)


def bass(ch, rolling=False, bars=4):
    if rolling:
        return {"bars": bars, "bass": {"chords": ch, "style": "stabs", "rhythm": ".xxx.xxx.xxx.xxx", "voicing": "root",
                                       "register": "F2", "stab_len": 1, "vel": 0.85}}
    return {"bars": bars, "bass": {"chords": ch, "style": "stabs", "rhythm": "..x...x...x...x.", "voicing": "root",
                                   "register": "F2", "stab_len": 2, "vel": 0.9}}


patterns = {
    "four": {"bars": 1, "kick": "x...x...x...x..."},
    "shake": {"bars": 1, "chh": "xxxxxxxxxxxxxxxx"},
    "hats": {"bars": 1, "ohat": "..x...x...x...x.", "chh": "xxxxxxxxxxxxxxxx"},
    "claps": {"bars": 1, "clap": "....x.......x..."},
    "offb": bass(GROOVE),
    "offbL": bass(LIGHT),
    "rollL": bass(LIGHT, rolling=True),
    "gated": {"bars": 4, "saws": {"chords": GROOVE, "style": "sustain", "register": "Ab4", "voicing": "close", "vel": 0.75}},
    "gatedL": {"bars": 4, "saws": {"chords": LIGHT, "style": "sustain", "register": "Ab4", "voicing": "close", "vel": 0.75}},
    "hook": {"bars": 4, "lead": HOOK_DARK},
    "hookL": {"bars": 4, "lead": HOOK_LIGHT},
    "hookL2": {"bars": 4, "lead2": HOOK_LIGHT},
    "wave": {"bars": 8, "lead": HOOK_WAVE, "lead2": HOOK_WAVE},
    "plk": {"bars": 4, "pluck": HOOK_DARK},
    "plkL": {"bars": 4, "pluck": HOOK_LIGHT},
    "arps": {"bars": 4, "arp": {"chords": GROOVE, "style": "arp", "rate": 1, "pattern": "updown", "octaves": 2,
                                "register": "F4", "voicing": "close", "vel": 0.7}},
    "pads": {"bars": 4, "pad": {"chords": GROOVE, "style": "sustain", "register": "F4", "voicing": "spread", "vel": 0.7}},
    "padsL": {"bars": 4, "pad": {"chords": LIGHT, "style": "sustain", "register": "F4", "voicing": "spread", "vel": 0.7}},
    "padsS": {"bars": 8, "pad": {"chords": GROOVE_SLOW, "style": "sustain", "register": "F4", "voicing": "spread", "vel": 0.7}},
    "padsLS": {"bars": 8, "pad": {"chords": LIGHT_SLOW, "style": "sustain", "register": "F4", "voicing": "spread", "vel": 0.7}},
    "voxD": {"bars": 8, "vox": VOX_DARK},
    "voxDlate": {"bars": 16, "vox": shift(HOOK_DARK, -1, 2, 128)},
    "gatedLlate": {"bars": 16, "saws": {"chords": "-:128 " + LIGHT + " " + LIGHT, "style": "sustain", "register": "Ab4",
                                        "voicing": "close", "vel": 0.6}},
    "voxL": {"bars": 8, "vox": VOX_LIGHT},
    "voxH": {"bars": 8, "vox": shift(HOOK_HIGH, -1, 2)},
    "arpsLlate": {"bars": 16, "arp": {"chords": "-:128 " + LIGHT + " " + LIGHT, "style": "arp", "rate": 1, "pattern": "updown",
                                      "octaves": 2, "register": "F4", "voicing": "close", "vel": 0.7}},
    "choirL": {"bars": 4, "choir": {"chords": LIGHT, "style": "sustain", "register": "Ab4", "voicing": "spread", "vel": 0.7}},
    "roll8": {"bars": 8, "snare": "x...x...x...x..." * 2 + "x.x.x.x.x.x.x.x." * 2 + "xxxxxxxxxxxxxxxx" * 2 + "RRRRRRRRRRRRRRRR" * 2},
    "roll16": {"bars": 16, "snare": "x...x...x...x..." * 4 + "x.x.x.x.x.x.x.x." * 4 + "xxxxxxxxxxxxxxxx" * 4 + "RRRRRRRRRRRRRRRR" * 4},
}

DR = ["four", "hats", "claps"]
arrangement = [
    # the long dark
    {"name": "introA", "bars": 16, "play": ["four", "shake", "offb"]},
    {"name": "introB", "bars": 16, "play": DR + ["offb", "plk"], "auto": {"pluck": {"lpf": [500, 1400]}, "ohat": {"gain_db": -3}}},
    {"name": "dark1", "bars": 16, "play": DR + ["offb", "arps"], "auto": {"arp": {"lpf": [700, 3000]}, "ohat": {"gain_db": -2}}},
    {"name": "dark2", "bars": 16, "play": DR + ["offb", "arps", "gated", "pads"], "auto": {"saws": {"lpf": [1200, 4000]}}},
    {"name": "build1", "bars": 8, "play": ["four", "hats", "offb", "gated", "arps", "pads", "roll8"],
     "auto": {"saws": {"hpf": [250, 1200]}, "pad": {"hpf": [200, 900]}, "arp": {"hpf": [300, 1500]}, "snare": {"gain_db": [-12, 0]}},
     "exit": {"riser": 8, "cut": {"tracks": "all", "beats": 1}}},
    {"name": "drop1", "bars": 24, "play": DR + ["offb", "gated", "hook"], "enter": {"crash": 0.7, "impact": 0.4},
     "auto": {"lead": {"lpf": [1500, 3000], "gain_db": -2}, "saws": {"lpf": 3000, "gain_db": -3}}},
    # the held breath
    {"name": "bd1a", "bars": 16, "play": ["padsS", "voxDlate"], "enter": {"downlifter": 4},
     "auto": {"pad": {"gain_db": [-8, -4], "lpf": [700, 2000]}}},
    {"name": "bd1b", "bars": 16, "play": ["padsLS", "voxL", "gatedLlate"],
     "auto": {"pad": {"gain_db": -4, "lpf": [2000, 7000]}, "saws": {"gain_db": [-14, -6], "lpf": [800, 4000]}}},
    {"name": "build2", "bars": 16, "play": ["gatedL", "padsL", "roll16", "plkL"],
     "auto": {"saws": {"hpf": [250, 1500]}, "pad": {"hpf": [200, 1200]}, "pluck": {"hpf": [250, 1500]},
              "snare": {"gain_db": [-14, 0]}},
     "exit": {"rise": 16, "riser": 8, "silence": 1}},
    # first light
    {"name": "rel1", "bars": 32, "play": DR + ["offbL", "gatedL", "hookL", "padsL"], "enter": {"crash": 0.9, "impact": 0.7}},
    {"name": "bd2", "bars": 16, "play": ["padsLS", "voxH", "arpsLlate"], "enter": {"downlifter": 4},
     "auto": {"pad": {"gain_db": -4}, "arp": {"lpf": [600, 3000], "gain_db": [-10, -3]}}},
    {"name": "build3", "bars": 8, "play": ["gatedL", "padsL", "roll8"],
     "auto": {"saws": {"hpf": [250, 1500]}, "pad": {"hpf": [200, 1200]}, "snare": {"gain_db": [-10, 0]}},
     "exit": {"rise": 8, "riser": 8, "silence": 1}},
    {"name": "rel2", "bars": 32, "play": DR + ["rollL", "gatedL", "wave", "padsL", "choirL"],
     "enter": {"crash": 1.0, "impact": 0.8}},
    # back to the heart
    {"name": "outro", "bars": 24, "play": DR + ["offbL"], "auto": {"bass": {"lpf": [3000, 600]}, "ohat": {"gain_db": -3}}},
]

P = {
    "title": "First Light",
    "bpm": 138,
    "swing": 0.5,
    "seed": 7,
    "tracks": tracks,
    "patterns": patterns,
    "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.9, "damping": 0.45, "return_db": -5, "lpf": 8000},
            "delay": {"beats": 0.75, "feedback": 0.38, "return_db": -9, "lpf": 4500}},
    "master": {"lufs": -10, "sat": 0.1, "glue": True},
}

json.dump(P, open(os.path.join(HERE, "project.json"), "w"), indent=1)
print("bars:", sum(s["bars"] for s in arrangement), "len s:", round(sum(s["bars"] for s in arrangement) * 4 * 60 / 138, 1))
