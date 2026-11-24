#!/usr/bin/env python3
"""Spectre's builder for session 008 ("Anyway"): writes project.json. Edit here, run, render."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

ROOM = lambda size=0.35, mix=0.22: {"type": "room", "size": size, "mix": mix}

tracks = {
    # ---------------- the kit
    "kick": {"inst": {"type": "kitkick", "tune": 72, "decay": 0.18, "beater": 0.6}, "humanize_ms": 5, "gain_db": 2,
             "fx": [{"type": "hpf", "hz": 40}, {"type": "eq", "hz": 60, "gain_db": -6, "q": 1.0}, {"type": "eq", "hz": 76, "gain_db": -7, "q": 1.5}, {"type": "eq", "hz": 120, "gain_db": 3, "q": 1.0}, {"type": "eq", "hz": 400, "gain_db": -4, "q": 1.0}, {"type": "eq", "hz": 3000, "gain_db": 2, "q": 1.0}, {"type": "comp", "threshold_db": -12, "ratio": 2, "attack_ms": 12, "release_ms": 80}, {"type": "sat", "amount": 0.1}, ROOM(0.3, 0.15)]},
    "snare": {"inst": {"type": "kitsnare", "tune": 180, "wires": 0.45, "rim": 0.6, "body": 1.3}, "humanize_ms": 6, "push_ms": 5, "gain_db": 6.5,
              "fx": [{"type": "eq", "hz": 190, "gain_db": -5, "q": 2.0}, {"type": "eq", "hz": 140, "gain_db": 2, "q": 1.0}, {"type": "highshelf", "hz": 4500, "gain_db": -8}, {"type": "lpf", "hz": 9000}, {"type": "eq", "hz": 2500, "gain_db": 4, "q": 1.0}, {"type": "comp", "threshold_db": -12, "ratio": 2, "attack_ms": 12, "release_ms": 90}, ROOM(0.4, 0.3)], "send_reverb": 0.14},
    "hat": {"inst": {"type": "kithat", "open": 0.0}, "humanize_ms": 6, "dyn": [1.0, 0.55, 0.8, 0.55], "pan": 0.3, "gain_db": -5,
            "fx": [{"type": "highshelf", "hz": 7000, "gain_db": -5}, {"type": "lpf", "hz": 12000}, ROOM(0.3, 0.2)]},
    "ohat": {"inst": {"type": "kithat", "open": 0.4}, "humanize_ms": 6, "pan": 0.3, "choke_by": "hat", "gain_db": -7,
             "dyn": [1.0, 0.6, 0.85, 0.6], "fx": [{"type": "highshelf", "hz": 7000, "gain_db": -4}, ROOM(0.3, 0.2)]},
    "phat": {"inst": {"type": "kithat", "pedal": True}, "humanize_ms": 6, "pan": 0.3, "gain_db": -2, "fx": [ROOM(0.3, 0.2)]},
    "ride": {"inst": {"type": "kitride", "decay": 3.0, "bell": 0.35}, "humanize_ms": 6, "pan": -0.35, "gain_db": -3,
             "dyn": [1.0, 0.6, 0.85, 0.6], "fx": [{"type": "highshelf", "hz": 6500, "gain_db": -5}, {"type": "lpf", "hz": 13000}, ROOM(0.35, 0.2)]},
    "crash": {"inst": {"type": "kitcrash", "decay": 2.6}, "humanize_ms": 4, "pan": -0.45, "gain_db": 20, "fx": [{"type": "highshelf", "hz": 8000, "gain_db": -3}, ROOM(0.4, 0.2)]},
    "tom1": {"inst": {"type": "kittom", "tune": 160, "decay": 0.45}, "humanize_ms": 5, "pan": 0.25, "fx": [ROOM(0.4, 0.25)]},
    "tom2": {"inst": {"type": "kittom", "tune": 92, "decay": 0.6}, "humanize_ms": 5, "pan": -0.3, "fx": [ROOM(0.4, 0.25)]},
    # ---------------- bass
    "bass": {"inst": {"type": "ebass", "pick": 0.6, "drive": 0.25, "tone": 3000}, "humanize_ms": 5, "legato": 0.9, "gain_db": -4,
             "fx": [{"type": "hpf", "hz": 40}, {"type": "lowshelf", "hz": 70, "gain_db": 3}, {"type": "eq", "hz": 82, "gain_db": -3, "q": 1.4}, {"type": "eq", "hz": 130, "gain_db": 3, "q": 1.0}, {"type": "eq", "hz": 160, "gain_db": 6, "q": 1.2}, {"type": "eq", "hz": 240, "gain_db": 3, "q": 0.9}]},
    # ---------------- guitars
    "clean": {"inst": {"type": "cleanguitar", "chorus": 0.6, "bright": 0.4}, "humanize_ms": 8, "send_reverb": 0.25, "send_delay": 0.12,
              "fx": [{"type": "hpf", "hz": 110}, {"type": "eq", "hz": 250, "gain_db": 3, "q": 0.9}]},
    "cleanV": {"inst": {"type": "cleanguitar", "chorus": 0.5, "bright": 0.25}, "humanize_ms": 12, "push_ms": 22, "send_reverb": 0.3, "send_delay": 0.12, "vel_jitter": 0.1,
               "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 250, "gain_db": 3, "q": 0.9}, {"type": "lpf", "hz": 3800}]},
    "chug": {"inst": {"type": "eguitar", "drive": 0.65, "mute": 0.8, "dark": 0.45}, "pan": -0.85, "humanize_ms": 5, "gain_db": -7,
             "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 220, "gain_db": 3, "q": 0.9}, {"type": "lowshelf", "hz": 300, "gain_db": 2}]},
    "chug2": {"inst": {"type": "eguitar", "drive": 0.55, "mute": 0.75, "dark": 0.55, "pickup": 0.15}, "pan": 0.85, "humanize_ms": 6, "push_ms": 3, "gain_db": -8,
              "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 220, "gain_db": 3, "q": 0.9}, {"type": "lowshelf", "hz": 300, "gain_db": 2}]},
    "gtrL": {"inst": {"type": "eguitar", "drive": 0.7, "dark": 0.45}, "pan": -0.85, "humanize_ms": 7, "gain_db": -2,
             "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 160, "gain_db": 3, "q": 1.0}, {"type": "eq", "hz": 200, "gain_db": 3, "q": 0.8}, {"type": "lowshelf", "hz": 320, "gain_db": 5}]},
    "gtrR": {"inst": {"type": "eguitar", "drive": 0.55, "dark": 0.55, "pickup": 0.15}, "pan": 0.85, "humanize_ms": 7, "push_ms": 3, "gain_db": -2,
             "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 180, "gain_db": 4, "q": 0.8}, {"type": "eq", "hz": 260, "gain_db": 3, "q": 0.8}, {"type": "lowshelf", "hz": 320, "gain_db": 4}]},
    # ---------------- keys
    "organ": {"inst": {"type": "organ"}, "gain_db": -5, "width": 0.6, "send_reverb": 0.2,
              "fx": [{"type": "hpf", "hz": 120}, {"type": "lpf", "hz": 3000}]},
    "lead": {"inst": {"type": "eguitar", "drive": 0.55, "dark": 0.35, "pickup": 0.22, "sustain": 2.5}, "pan": 0.2, "humanize_ms": 8, "gain_db": -4,
             "send_reverb": 0.3, "send_delay": 0.2, "legato": 1.0,
             "fx": [{"type": "hpf", "hz": 250}, {"type": "eq", "hz": 1500, "gain_db": 2, "q": 0.8}, {"type": "lpf", "hz": 6000}]},
    "piano": {"inst": {"type": "piano", "felt": 0.3}, "gain_db": -2, "send_reverb": 0.25, "humanize_ms": 8, "width": 0.4,
              "fx": [{"type": "hpf", "hz": 180}]},
    # ---------------- the voice
    "vox": {"inst": {"type": "vox", "voice": "alto", "vowel": "oo", "vowel2": "oh", "morph": 0.6, "vibrato": 0.25, "breath": 0.35, "ring": 0.6},
            "humanize_ms": 12, "send_reverb": 0.3, "send_delay": 0.14,
            "fx": [{"type": "hpf", "hz": 160}, {"type": "lpf", "hz": 10000}, {"type": "eq", "hz": 2800, "gain_db": 3, "q": 0.9}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
    "voxV": {"inst": {"type": "vox", "voice": "alto", "vowel": "oo", "vowel2": "oh", "morph": 0.6, "vibrato": 0.2, "breath": 0.28, "ring": 0.5, "scoop": 0.7},
             "humanize_ms": 16, "push_ms": 28, "send_reverb": 0.3, "send_delay": 0.14,
             "fx": [{"type": "hpf", "hz": 160}, {"type": "lpf", "hz": 10000}, {"type": "eq", "hz": 2800, "gain_db": 3, "q": 0.9}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
    "voxC": {"inst": {"type": "vox", "voice": "alto", "vowel": "oh", "vowel2": "ah", "morph": 0.4, "vibrato": 0.3, "breath": 0.25, "bright": 0.75, "ring": 0.75},
             "humanize_ms": 12, "send_reverb": 0.32, "send_delay": 0.16,
             "fx": [{"type": "hpf", "hz": 180}, {"type": "lpf", "hz": 10000}, {"type": "eq", "hz": 2800, "gain_db": 5, "q": 0.9}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
    "voxD": {"inst": {"type": "vox", "voice": "tenor", "vowel": "oh", "vowel2": "ah", "morph": 0.5, "vibrato": 0.22, "breath": 0.3, "bright": 0.55},
             "humanize_ms": 14, "push_ms": 8, "send_reverb": 0.35, "gain_db": -4, "pan": -0.25,
             "fx": [{"type": "hpf", "hz": 140}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
}

VERSE = "C#m:16 Aadd9:16 E:16 Bsus4:8 B:8"
PRE = "A:16 B:16 C#m:16 B:16"
CHORUS = "E:16 B/D#:16 C#m7:16 A:16 E:16 B:16 Asus2:16 A:16"


def x2(ch):
    return ch + " " + ch


patterns = {
    # ---------------- drums
    "v1beat": {"bars": 2, "kick": "x.........x.....x...............", "phat": "....x.......x.......x.......x...", "snare": "............g...............o..."},
    "vbeat": {"bars": 1, "kick": "x.......x.x.....", "snare": "....x.......x...", "hat": "x.x.x.x.x.x.x.x."},
    "prebeat": {"bars": 1, "kick": "x...x...x...x...", "snare": "....x.......x...", "hat": "x.x.x.x.x.x.x.o.", "ohat": "..............x."},
    "cbeat": {"bars": 1, "kick": "x.....x.x.x.....", "snare": "..o.X.....o.X...", "ohat": "x.x.x.x.x.x.x.x."},
    "crash1": {"bars": 8, "crash": "X" + "." * 127},
    "fillA": {"bars": 1, "kick": "x...............", "snare": "....x...xxxx....", "tom1": "............xx..", "tom2": "..............xx"},
    # ---------------- music
    "verse": {"bars": 8,
              "cleanV": {"chords": x2(VERSE), "style": "arp", "rate": 2, "pattern": "updown", "register": "C#3", "voicing": "guitar", "vel": 0.65},
              "bass": {"chords": x2(VERSE), "style": "stabs", "rhythm": "x.......x.......", "voicing": "root", "register": "F#2", "stab_len": 7, "vel": 0.75},
              "voxV": "2:E4:2 4:G#4:3 7:G#4:1 8:G#4:4 12:F#4:2 14:E4:4 "
                     "20:E4:2 22:F#4:2 24:G#4:4 28:F#4:6 "
                     "34:E4:2 36:G#4:2 38:B4:4 42:G#4:2 44:F#4:6 "
                     "52:D#4:2 54:E4:2 56:F#4:6 "
                     "66:E4:2 68:G#4:3 71:G#4:1 72:B4:4 76:G#4:2 78:F#4:4 "
                     "84:E4:2 86:F#4:2 88:G#4:4 92:A4:2 94:G#4:4 "
                     "98:E4:2 100:G#4:2 102:B4:4 106:C#5:2 108:B4:4 "
                     "114:G#4:2 116:F#4:2 118:E4:8"},
    "pre": {"bars": 4,
            "chug": {"chords": PRE, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "E2", "stab_len": 2, "vel": 0.75, "strum": "down", "strum_ms": 5},
            "chug2": {"chords": PRE, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.7, "strum": "down", "strum_ms": 6},
            "bass": {"chords": PRE, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "root", "register": "F#2", "stab_len": 2, "vel": 0.8},
            "clean": {"chords": PRE, "style": "arp", "rate": 2, "pattern": "up", "register": "E3", "voicing": "guitar", "vel": 0.5},
            "vox": "2:C#5:2 4:B4:2 6:A4:4 10:B4:2 12:C#5:4 "
                   "18:D#5:2 20:C#5:2 22:B4:6 28:F#4:4 "
                   "34:E5:2 36:D#5:2 38:C#5:6 44:B4:2 46:C#5:2 "
                   "48:D#5:10"},
    "chorus": {"bars": 8,
               "gtrL": {"chords": CHORUS, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "E2", "stab_len": 2, "vel": 0.85, "strum": "down", "strum_ms": 7},
               "gtrR": {"chords": CHORUS, "style": "stabs", "rhythm": "x..x..x.x.x.x...", "voicing": "guitar", "register": "E3", "stab_len": 3, "vel": 0.8, "strum": "alt", "strum_ms": 14},
               "bass": {"chords": CHORUS, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "root", "register": "E2", "stab_len": 2, "vel": 0.85},
               "organ": {"chords": CHORUS, "style": "sustain", "register": "E3", "voicing": "close", "vel": 0.6},
               },
    "hook": {"bars": 8,
               "voxC": "0:B4:2 2:E5:6 8:E5:2 10:F#5:2 12:G#5:4 "
                       "16:F#5:6 22:E5:2 24:D#5:4 28:B4:4 "
                       "32:C#5:2 34:E5:6 40:E5:2 42:F#5:2 44:G#5:4 "
                       "48:F#5:4 52:E5:10 "
                       "64:B4:2 66:E5:6 72:E5:2 74:F#5:2 76:G#5:4 "
                       "80:G#5:6 86:F#5:2 88:E5:4 92:D#5:4 "
                       "96:E5:4 100:C#5:4 104:B4:8 "
                       "112:C#5:4 116:B4:10"},

    # ---------------- arrangement patterns
    "introgtr": {"bars": 4, "cleanV": {"chords": VERSE, "style": "arp", "rate": 2, "pattern": "updown", "register": "C#3", "voicing": "guitar", "vel": 0.6}},
    "heart": {"bars": 1, "kick": "x.........x.....", "phat": "....x.......x..."},
    "v2beat": {"bars": 1, "kick": "x.......x.x.....", "snare": "....x.......x..o", "ride": "x.x.x.x.x.x.x.x."},
    "tagbeat": {"bars": 1, "kick": "x.......x.x.....", "snare": "....x.......x...", "hat": "x.x.x.x.x.x.x.x."},
    "fillT": {"bars": 1, "kick": "x.....x.x.......", "snare": "..o.X...........", "ride": "x.x.x.x.........", "tom1": "........xx.x....", "tom2": "............x.xX"},
    "fillS": {"bars": 1, "kick": "x.......x.......", "snare": "....x.......xoxx", "hat": "x.x.x.x.x.x....."},
    "crash4": {"bars": 4, "crash": "X" + "." * 63},
    "tag": {"bars": 4,
            "clean": {"chords": "C#m:16 Aadd9:16 C#m:16 Bsus4:8 B:8", "style": "arp", "rate": 2, "pattern": "updown", "register": "C#3", "voicing": "guitar", "vel": 0.7},
            "bass": {"chords": "C#m:16 Aadd9:16 C#m:16 Bsus4:8 B:8", "style": "stabs", "rhythm": "x.......x.x.....", "voicing": "root", "register": "F#2", "stab_len": 4, "vel": 0.8},
            "gtrR": {"chords": "C#m:16 Aadd9:16 C#m:16 Bsus4:8 B:8", "style": "sustain", "voicing": "guitar", "register": "E3", "vel": 0.6}},
    "verse2": {"bars": 8,
               "clean": {"chords": x2(VERSE), "style": "arp", "rate": 2, "pattern": "updown", "register": "C#3", "voicing": "guitar", "vel": 0.6},
               "bass": {"chords": x2(VERSE), "style": "stabs", "rhythm": "x.....x.x.x.x...", "voicing": "root", "register": "F#2", "stab_len": 2, "vel": 0.75},
               "vox": "2:E4:2 4:G#4:3 7:G#4:1 8:G#4:4 12:F#4:2 14:E4:4 "
                      "20:E4:2 22:F#4:2 24:G#4:2 26:A4:2 28:G#4:6 "
                      "34:E4:2 36:G#4:2 38:B4:4 42:C#5:2 44:B4:6 "
                      "52:D#4:2 54:E4:2 56:F#4:6 "
                      "66:G#4:2 68:B4:3 71:B4:1 72:C#5:4 76:B4:2 78:G#4:4 "
                      "84:E4:2 86:F#4:2 88:G#4:4 92:A4:2 94:B4:4 "
                      "98:B4:2 100:C#5:2 102:E5:4 106:C#5:2 108:B4:4 "
                      "114:G#4:2 116:F#4:2 118:E4:8"},
    "v2chug": {"bars": 8, "chug2": {"chords": x2(VERSE), "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.6, "strum": "down", "strum_ms": 6}},
    "chorusP": {"bars": 8, "piano": {"chords": CHORUS, "style": "stabs", "rhythm": "x...x...x...x...", "register": "E5", "voicing": "close", "stab_len": 3, "vel": 0.55}},
    "cbeat2": {"bars": 1, "kick": "x.....x.x.x.....", "snare": "..o.X.....o.X...", "ride": "x.x.x.x.x.x.x.x."},
    "bridgeA": {"bars": 4,
                "cleanV": {"chords": "C#m:16 G#m:16 A:16 A:16", "style": "arp", "rate": 4, "pattern": "up", "register": "C#3", "voicing": "guitar", "vel": 0.55},
                "voxV": "4:E4:4 8:D#4:4 12:C#4:8 24:B3:4 28:C#4:4 32:E4:8~ 40:D#4:6 52:C#4:10"},
    "bridgeB": {"bars": 4,
                "clean": {"chords": "C#m:16 G#m:16 A:16 B:16", "style": "arp", "rate": 2, "pattern": "up", "register": "C#3", "voicing": "guitar", "vel": 0.6},
                "bass": {"chords": "-:32 A:16 B:16", "style": "stabs", "rhythm": "x.......x.......", "voicing": "root", "register": "F#2", "stab_len": 7, "vel": 0.75},
                "chug": {"chords": "-:32 A:16 B:16", "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "E2", "stab_len": 2, "vel": 0.7, "strum": "down", "strum_ms": 5},
                "kick":  "x...............x...............x.......x.......x...x...x...x...",
                "snare": "................................x...............o.o.x.x.xxxxXXXX",
                "tom2":  ".........................................................x.x....",
                "phat":  "........x...............x.......x.......x.......x.......x......."},
    "voxDbl": {"bars": 8, "voxD": "0:B3:2 2:E4:6 8:E4:2 10:F#4:2 12:G#4:4 "
                                  "16:F#4:6 22:E4:2 24:D#4:4 28:B3:4 "
                                  "32:C#4:2 34:E4:6 40:E4:2 42:F#4:2 44:G#4:4 "
                                  "48:F#4:4 52:E4:10 "
                                  "64:B3:2 66:E4:6 72:E4:2 74:F#4:2 76:G#4:4 "
                                  "80:G#4:6 86:F#4:2 88:E4:4 92:D#4:4 "
                                  "96:E4:4 100:C#4:4 104:B3:8 "
                                  "112:C#4:4 116:B3:10"},
    "hookPeak": {"bars": 8, "voxC": "0:B4:2 2:E5:6 8:E5:2 10:F#5:2 12:G#5:4 "
                                    "16:B5:10~ 26:A5:2 28:G#5:4 "
                                    "32:C#5:2 34:E5:6 40:E5:2 42:F#5:2 44:G#5:4 "
                                    "48:A5:8~ 56:G#5:4 60:F#5:4 "
                                    "64:B4:2 66:E5:6 72:E5:2 74:F#5:2 76:G#5:4 "
                                    "80:G#5:6 86:F#5:2 88:E5:4 92:D#5:4 "
                                    "96:E5:4 100:C#5:4 104:B4:8 "
                                    "112:C#5:4 116:B4:10"},
    "leadPeak": {"bars": 8, "lead": "0:B4:2 2:E5:6 8:E5:2 10:F#5:2 12:G#5:4 "
                                    "16:B5:10~ 26:A5:2 28:G#5:4 "
                                    "32:C#5:2 34:E5:6 40:E5:2 42:F#5:2 44:G#5:4 "
                                    "48:A5:8~ 56:G#5:4 60:F#5:4 "
                                    "64:B4:2 66:E5:6 72:E5:2 74:F#5:2 76:G#5:4 "
                                    "80:G#5:6 86:F#5:2 88:E5:4 92:D#5:4 "
                                    "96:E5:4 100:C#5:4 104:B4:8 "
                                    "112:C#5:4 116:B4:10"},
    "cbeat3": {"bars": 1, "kick": "x.....x.x.x.....", "snare": "..o.X.....o.X...", "ride": "X.x.X.x.X.x.X.x.", "ohat": "..............x."},
    "crashL": {"bars": 4, "crash": "X" + "." * 63},
    "voxDhalf": {"bars": 8, "voxD": "64:B3:2 66:E4:6 72:E4:2 74:F#4:2 76:G#4:4 80:G#4:6 86:F#4:2 88:E4:4 92:D#4:4 96:E4:4 100:C#4:4 104:B3:8 112:C#4:4 116:B3:10"},
    "chorusArp": {"bars": 8, "clean": {"chords": CHORUS, "style": "arp", "rate": 2, "pattern": "updown", "register": "E3", "voicing": "guitar", "vel": 0.55}},
    "outro": {"bars": 8,
              "clean": {"chords": "C#m:16 Aadd9:16 E:16 Bsus4:16 C#m:16 Aadd9:16 E:16 Asus2:16", "style": "arp", "rate": 2, "pattern": "updown", "register": "C#3", "voicing": "guitar", "vel": 0.65},
              "bass": {"chords": "C#m:16 Aadd9:16 E:16 Bsus4:16 C#m:16 Aadd9:16 E:16 Asus2:16", "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "root", "register": "E2", "stab_len": 2, "vel": 0.75},
              "gtrR": {"chords": "C#m:16 Aadd9:16 E:16 Bsus4:16 C#m:16 Aadd9:16 E:16 Asus2:16", "style": "stabs", "rhythm": "x.......x.......", "voicing": "guitar", "register": "E3", "stab_len": 7, "vel": 0.6, "strum": "down", "strum_ms": 18},
              "organ": {"chords": "C#m:16 Aadd9:16 E:16 Bsus4:16 C#m:16 Aadd9:16 E:16 Asus2:16", "style": "sustain", "register": "B3", "voicing": "close", "vel": 0.5},
              "lead": "2:E5:2 4:G#5:3 7:G#5:1 8:G#5:4 12:F#5:2 14:E5:4 20:E5:2 22:F#5:2 24:G#5:4 28:F#5:6 34:E5:2 36:G#5:2 38:B5:4 42:G#5:2 44:F#5:6 52:D#5:2 54:E5:2 56:F#5:6",
              "vox": "66:E4:2 68:G#4:3 71:G#4:1 72:B4:4 76:G#4:2 78:F#4:4 84:E4:2 86:F#4:2 88:G#4:4 92:A4:2 94:B4:4 98:B4:2 100:C#5:2 102:E5:12~ 116:C#5:12"},
    "outEnd": {"bars": 1,
               "bass": {"chords": "Asus2:16", "style": "stabs", "rhythm": "x...............", "voicing": "root", "register": "F#2", "stab_len": 16, "vel": 0.8},
               "gtrR": {"chords": "Asus2:16", "style": "stabs", "rhythm": "x...............", "voicing": "guitar", "register": "E3", "stab_len": 16, "vel": 0.75, "strum": "down", "strum_ms": 30},
               "gtrL": {"chords": "A5:16", "style": "stabs", "rhythm": "x...............", "voicing": "power", "register": "E2", "stab_len": 16, "vel": 0.7, "strum": "down", "strum_ms": 12},
               "organ": {"chords": "Asus2:16", "style": "sustain", "register": "B3", "voicing": "close", "vel": 0.5}},
    "coda": {"bars": 4, "cleanV": {"chords": "Asus2:16 Asus2:16 -:32", "style": "arp", "rate": 4, "pattern": "up", "register": "C#3", "voicing": "guitar", "vel": 0.5}},
    "outbeat": {"bars": 8, "kick": ("x.......x.x....." * 7) + "x...............",
                "snare": ("....x.......x..." * 7) + "................",
                "ride": ("x.x.x.x.x.x.x.x." * 7) + "................",
                "crash": "." * 112 + "X" + "." * 15},
}

arrangement = [
    {"name": "intro", "bars": 8, "play": ["introgtr"], "auto": {"cleanV": {"gain_db": 5}}},
    {"name": "verse1a", "bars": 8, "play": ["verse", "heart"], "auto": {"kick": {"gain_db": -7}, "bass": {"mute": True}}},
    {"name": "verse1b", "bars": 8, "play": ["verse", "v1beat"], "auto": {"kick": {"gain_db": -6}, "snare": {"gain_db": -8}, "bass": {"gain_db": -4}}},
    {"name": "pre1", "bars": 4, "play": ["pre", "prebeat"], "fill": {"pattern": "fillA"},
     "auto": {"chug": {"gain_db": [-8, 0]}, "chug2": {"gain_db": [-8, 0]}, "kick": {"gain_db": [-7, -2]}, "snare": {"gain_db": [-7, 0]}, "hat": {"gain_db": [-4, 0]}, "bass": {"gain_db": [-3, 0]}}},
    {"name": "chorus1", "bars": 8, "play": ["chorus", "hook", "cbeat", "crash1"]},
    {"name": "tag", "bars": 4, "play": ["tag", "tagbeat", "crash4"], "fill": {"pattern": "fillS"}, "auto": {"gtrR": {"gain_db": -6}, "kick": {"gain_db": -5}, "snare": {"gain_db": -6}, "hat": {"gain_db": -3}}},
    {"name": "verse2a", "bars": 8, "play": ["verse2", "v2beat"], "auto": {"kick": {"gain_db": -8}, "snare": {"gain_db": -9}, "ride": {"gain_db": 2}, "bass": {"gain_db": -3}}},
    {"name": "verse2b", "bars": 8, "play": ["verse2", "v2beat", "v2chug"], "auto": {"kick": {"gain_db": -6}, "snare": {"gain_db": -6}, "ride": {"gain_db": 3}, "chug2": {"gain_db": -4}}},
    {"name": "pre2", "bars": 4, "play": ["pre", "prebeat"], "fill": {"pattern": "fillA"},
     "auto": {"chug": {"gain_db": [-6, 0]}, "chug2": {"gain_db": [-6, 0]}, "kick": {"gain_db": [-5, -1]}, "snare": {"gain_db": [-5, 0]}, "hat": {"gain_db": [-3, 0]}}},
    {"name": "chorus2", "bars": 8, "play": ["chorus", "hook", "cbeat2", "crash1", "chorusP", "voxDhalf"], "auto": {"voxD": {"gain_db": -3}}},
    {"name": "bridgeA", "bars": 4, "play": ["bridgeA"]},
    {"name": "bridgeB", "bars": 4, "play": ["bridgeB"], "auto": {"chug": {"gain_db": [-12, -3]}, "kick": {"gain_db": [-8, 0]}},
     "exit": {"cut": {"tracks": "all", "beats": 1}}},
    {"name": "chorus3", "bars": 8, "play": ["chorus", "hook", "cbeat2", "crash1", "chorusP", "voxDbl", "chorusArp"], "fill": {"pattern": "fillT"}},
    {"name": "chorus4", "bars": 8, "play": ["chorus", "hookPeak", "leadPeak", "cbeat3", "crashL", "chorusP", "voxDbl", "chorusArp"],
     "auto": {"ride": {"gain_db": 3}, "lead": {"gain_db": -3}}},
    {"name": "outro", "bars": 8, "play": ["outro", "outbeat"], "fill": {"pattern": "outEnd"}, "auto": {"kick": {"gain_db": -3}, "snare": {"gain_db": -4}, "ride": {"gain_db": -3}}},
    {"name": "coda", "bars": 4, "play": ["coda"]},
]

project = {
    "title": "Anyway",
    "bpm": 122,
    "swing": 0.5,
    "seed": 8,
    "tracks": tracks,
    "patterns": patterns,
    "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.65, "damping": 0.5, "return_db": -6, "lpf": 8000},
            "delay": {"beats": 0.75, "feedback": 0.3, "return_db": -10, "lpf": 4000}},
    "master": {"lufs": -10, "sat": 0.1, "glue": True},
}

json.dump(project, open(os.path.join(HERE, "project.json"), "w"), indent=1)
print("project.json written:", sum(s["bars"] for s in arrangement), "bars")
