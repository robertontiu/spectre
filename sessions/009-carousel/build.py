#!/usr/bin/env python3
"""Spectre's builder for session 009 ("Here You Are"): writes project.json. Edit here, run, render."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOP = "--loop" in sys.argv

ROOM = lambda size=0.35, mix=0.22: {"type": "room", "size": size, "mix": mix}

# ------------------------------------------------------------------ helpers
# The ride: sixteenths grouped 3+3+3+3+2+2, the first of each group is the top note, accented.
TONES = {  # (hi, mid, lo)
    "A": ("E5", "C#5", "A4"), "F#m": ("E5", "C#5", "F#4"), "D": ("F#5", "D5", "A4"),
    "Es": ("E5", "B4", "A4"), "E": ("E5", "B4", "G#4"), "Bm": ("F#5", "D5", "B4"),
    "A/C#": ("E5", "C#5", "A4"), "Dm": ("F5", "D5", "A4"), "G": ("G5", "D5", "B4"),
    "C#m": ("E5", "C#5", "G#4"), "Dh": ("A5", "F#5", "D5"), "Ah": ("A5", "E5", "C#5"), "Eh": ("G#5", "E5", "B4"),
    "F#mh": ("A5", "F#5", "C#5"),
}
GROUPS = [(0, 3), (3, 3), (6, 3), (9, 3), (12, 2), (14, 2)]


def fig(bars, acc=0.85, soft=0.5, only_acc=False, ln=2, half=None):
    """bars: list of chord keys (one per bar) or (key1, key2) for a split bar."""
    out = []
    for b, ch in enumerate(bars):
        for (g0, n) in GROUPS:
            key = ch if isinstance(ch, str) else (ch[0] if g0 < 8 else ch[1])
            if key is None:
                continue
            hi, mid, lo = TONES[key]
            seq = [hi, lo, mid] if n == 3 else [hi, lo]
            for i, note in enumerate(seq):
                if only_acc and i > 0:
                    continue
                v = acc if i == 0 else soft
                out.append("%d:%s:%d:%.2f" % (b * 16 + g0 + i, note, (n + 1) if only_acc else ln, v))
    return " ".join(out)


def bass(bars, rhythm="x.x.x.x.x.x.x.x.", ln=2, vel=0.8):
    """bars: list of notes (one per bar) or tuples (two halves); rhythm per bar in 16ths; 'X' accent."""
    out = []
    for b, n in enumerate(bars):
        for i, c in enumerate(rhythm):
            if c == ".":
                continue
            note = n if (n is None or isinstance(n, str)) else (n[0] if i < 8 else n[1])
            if note is None:
                continue
            out.append("%d:%s:%d:%.2f" % (b * 16 + i, note, ln, vel * (1.1 if c == "X" else 1.0)))
    return " ".join(out)


def shift(notes, off):
    """shift a note string by `off` 16ths"""
    out = []
    for t in notes.split():
        p = t.split(":")
        p[0] = str(int(p[0]) + off)
        out.append(":".join(p))
    return " ".join(out)


def octave(notes, n):
    out = []
    for t in notes.split():
        p = t.split(":")
        p[1] = p[1][:-1] + str(int(p[1][-1]) + n)
        out.append(":".join(p))
    return " ".join(out)


# ------------------------------------------------------------------ tracks
tracks = {
    # ---------------- the kit
    "kick": {"inst": {"type": "kitkick", "tune": 56, "decay": 0.18, "beater": 0.65}, "humanize_ms": 4, "gain_db": 3.5,
             "fx": [{"type": "hpf", "hz": 40}, {"type": "eq", "hz": 56, "gain_db": -12, "q": 1.2}, {"type": "eq", "hz": 115, "gain_db": 6, "q": 1.0},
                    {"type": "eq", "hz": 400, "gain_db": -4, "q": 1.0}, {"type": "eq", "hz": 3000, "gain_db": 3, "q": 1.0},
                    {"type": "comp", "threshold_db": -12, "ratio": 2, "attack_ms": 12, "release_ms": 80}, ROOM(0.3, 0.15)]},
    "snare": {"inst": {"type": "kitsnare", "tune": 200, "wires": 0.45, "rim": 0.65, "body": 1.2}, "humanize_ms": 5, "push_ms": 3, "gain_db": 7,
              "fx": [{"type": "eq", "hz": 200, "gain_db": -3, "q": 2.0}, {"type": "eq", "hz": 150, "gain_db": 2, "q": 1.0},
                     {"type": "highshelf", "hz": 4500, "gain_db": -8}, {"type": "lpf", "hz": 9000}, {"type": "eq", "hz": 2500, "gain_db": 4, "q": 1.0},
                     {"type": "comp", "threshold_db": -12, "ratio": 2, "attack_ms": 12, "release_ms": 90}, ROOM(0.4, 0.3)], "send_reverb": 0.12},
    "hat": {"inst": {"type": "kithat", "open": 0.0}, "humanize_ms": 5, "dyn": [1.0, 0.5, 0.75, 0.5], "pan": 0.3, "gain_db": 2,
            "fx": [{"type": "highshelf", "hz": 7000, "gain_db": -5}, {"type": "lpf", "hz": 12000}, ROOM(0.3, 0.2)]},
    "ohat": {"inst": {"type": "kithat", "open": 0.45}, "humanize_ms": 5, "pan": 0.3, "choke_by": "hat", "gain_db": -2,
             "dyn": [1.0, 0.6, 0.85, 0.6], "fx": [{"type": "highshelf", "hz": 7000, "gain_db": -4}, {"type": "lpf", "hz": 12000}, ROOM(0.3, 0.2)]},
    "phat": {"inst": {"type": "kithat", "pedal": True}, "humanize_ms": 5, "pan": 0.3, "gain_db": 8, "fx": [{"type": "highshelf", "hz": 7000, "gain_db": -3}, ROOM(0.3, 0.2)]},
    "ride": {"inst": {"type": "kitride", "decay": 3.0, "bell": 0.4}, "humanize_ms": 5, "pan": -0.35, "gain_db": -3,
             "dyn": [1.0, 0.6, 0.85, 0.6], "fx": [{"type": "highshelf", "hz": 6500, "gain_db": -5}, {"type": "lpf", "hz": 13000}, ROOM(0.35, 0.2)]},
    "bell": {"inst": {"type": "kitride", "decay": 3.5, "bell": 0.9}, "humanize_ms": 5, "pan": -0.35, "gain_db": -4,
             "fx": [{"type": "highshelf", "hz": 6500, "gain_db": -5}, {"type": "lpf", "hz": 12000}, ROOM(0.4, 0.25)], "send_reverb": 0.15},
    "crash": {"inst": {"type": "kitcrash", "decay": 2.6}, "humanize_ms": 4, "pan": -0.45, "gain_db": 20,
              "fx": [{"type": "highshelf", "hz": 8000, "gain_db": -3}, ROOM(0.4, 0.2)]},
    "tom1": {"inst": {"type": "kittom", "tune": 165, "decay": 0.4}, "humanize_ms": 5, "pan": 0.25, "fx": [ROOM(0.4, 0.25)]},
    "tom2": {"inst": {"type": "kittom", "tune": 95, "decay": 0.55}, "humanize_ms": 5, "pan": -0.3, "fx": [ROOM(0.4, 0.25)]},
    "tamb": {"inst": {"type": "shaker"}, "humanize_ms": 6, "pan": 0.5, "gain_db": 0, "dyn": [1.0, 0.4, 0.75, 0.4],
             "fx": [{"type": "hpf", "hz": 2500}, {"type": "lpf", "hz": 9500}, ROOM(0.35, 0.25)]},
    # ---------------- bass
    "bass": {"inst": {"type": "ebass", "pick": 0.75, "drive": 0.25, "tone": 3200}, "humanize_ms": 4, "legato": 0.9, "gain_db": -0.5,
             "fx": [{"type": "hpf", "hz": 45}, {"type": "eq", "hz": 100, "gain_db": 3, "q": 1.0}, {"type": "eq", "hz": 135, "gain_db": 7, "q": 1.0}, {"type": "eq", "hz": 240, "gain_db": 5, "q": 0.9},
                    {"type": "eq", "hz": 800, "gain_db": 2, "q": 1.0}]},
    # ---------------- guitars
    "fig": {"inst": {"type": "cleanguitar", "chorus": 0.45, "bright": 0.6, "sustain": 1.2}, "humanize_ms": 5, "vel_jitter": 0.08,
            "send_reverb": 0.18, "send_delay": 0.22, "gain_db": 7,
            "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 300, "gain_db": 2, "q": 0.9}, {"type": "lpf", "hz": 7500}]},
    "figM": {"inst": {"type": "cleanguitar", "chorus": 0.35, "bright": 0.5, "mute": 0.55, "sustain": 0.6}, "humanize_ms": 5, "vel_jitter": 0.08,
             "send_reverb": 0.12, "send_delay": 0.18, "gain_db": 9,
             "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 300, "gain_db": 2, "q": 0.9}, {"type": "lpf", "hz": 6500}]},
    "chug": {"inst": {"type": "eguitar", "drive": 0.5, "mute": 0.8, "dark": 0.4}, "pan": 0.8, "humanize_ms": 5, "gain_db": -9,
             "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 150, "gain_db": 4, "q": 0.9}, {"type": "eq", "hz": 250, "gain_db": 5, "q": 0.9}, {"type": "lowshelf", "hz": 320, "gain_db": 4}]},
    "gtrL": {"inst": {"type": "eguitar", "drive": 0.55, "dark": 0.4}, "pan": -0.85, "humanize_ms": 6, "gain_db": -2,
             "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 150, "gain_db": 6, "q": 0.9}, {"type": "eq", "hz": 250, "gain_db": 6, "q": 0.8},
                    {"type": "lowshelf", "hz": 350, "gain_db": 8}, {"type": "eq", "hz": 2600, "gain_db": -3.5, "q": 0.8}]},
    "gtrR": {"inst": {"type": "eguitar", "drive": 0.4, "dark": 0.35, "pickup": 0.16}, "pan": 0.85, "humanize_ms": 7, "push_ms": 2, "gain_db": -4,
             "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 165, "gain_db": 6, "q": 0.8}, {"type": "eq", "hz": 270, "gain_db": 6, "q": 0.8},
                    {"type": "lowshelf", "hz": 350, "gain_db": 7}, {"type": "eq", "hz": 2600, "gain_db": -3.5, "q": 0.8}]},
    "figB": {"inst": {"type": "cleanguitar", "chorus": 0.8, "chorus_rate": 0.5, "bright": 0.35, "sustain": 1.6}, "humanize_ms": 12, "vel_jitter": 0.15,
             "send_reverb": 0.35, "send_delay": 0.35, "gain_db": 6,
             "fx": [{"type": "hpf", "hz": 180}, {"type": "tremolo", "rate": 5.5, "depth": 0.55}, {"type": "phaser"}, {"type": "lpf", "hz": 4200}]},
    "lead": {"inst": {"type": "eguitar", "drive": 0.5, "dark": 0.35, "pickup": 0.22, "sustain": 2.5}, "pan": 0.15, "humanize_ms": 8, "gain_db": -4,
             "send_reverb": 0.3, "send_delay": 0.22, "legato": 1.0,
             "fx": [{"type": "hpf", "hz": 250}, {"type": "eq", "hz": 1500, "gain_db": 2, "q": 0.8}, {"type": "lpf", "hz": 6000}]},
    # ---------------- keys
    "organ": {"inst": {"type": "organ"}, "gain_db": 0, "width": 0.6, "send_reverb": 0.2,
              "fx": [{"type": "hpf", "hz": 110}, {"type": "lpf", "hz": 3200}]},
    "piano": {"inst": {"type": "piano", "felt": 0.1}, "gain_db": 0, "send_reverb": 0.2, "humanize_ms": 8, "pan": -0.3,
              "fx": [{"type": "hpf", "hz": 300}]},
    "mbox": {"inst": {"type": "musicbox"}, "gain_db": 0, "humanize_ms": 10, "vel_jitter": 0.12, "send_reverb": 0.15, "width": 0.3,
             "fx": [{"type": "hpf", "hz": 300}, {"type": "lpf", "hz": 7000}]},
    # ---------------- the voice
    "voxV": {"inst": {"type": "vox", "voice": "alto", "vowel": "oo", "vowel2": "oh", "morph": 0.25, "vibrato": 0.15, "breath": 0.25, "ring": 0.65, "scoop": 0.3},
             "humanize_ms": 8, "send_reverb": 0.22, "send_delay": 0.1,
             "fx": [{"type": "hpf", "hz": 160}, {"type": "lpf", "hz": 10000}, {"type": "eq", "hz": 2800, "gain_db": 4, "q": 0.9}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
    "voxC": {"inst": {"type": "vox", "voice": "alto", "vowel": "oh", "vowel2": "ah", "morph": 0.35, "vibrato": 0.3, "breath": 0.22, "bright": 0.9, "ring": 1.0},
             "humanize_ms": 8, "gain_db": 5, "send_reverb": 0.3, "send_delay": 0.16,
             "fx": [{"type": "hpf", "hz": 180}, {"type": "lpf", "hz": 10000}, {"type": "eq", "hz": 2400, "gain_db": 6, "q": 0.7}, {"type": "comp", "threshold_db": -20, "ratio": 3}, {"type": "chorus", "rate": 0.5, "depth": 0.3, "mix": 0.3}, {"type": "width", "amount": 0.35}]},
    "voxB": {"inst": {"type": "vox", "voice": "alto", "vowel": "oo", "vowel2": "oh", "morph": 0.8, "vibrato": 0.35, "vib_rate": 4.2, "breath": 0.3, "ring": 0.6, "scoop": 1.2, "glide_ms": 220},
             "humanize_ms": 14, "send_reverb": 0.4, "send_delay": 0.3,
             "fx": [{"type": "hpf", "hz": 160}, {"type": "lpf", "hz": 8000}, {"type": "eq", "hz": 2800, "gain_db": 4, "q": 0.9}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
    "voxD": {"inst": {"type": "vox", "voice": "tenor", "vowel": "oh", "vowel2": "ah", "morph": 0.5, "vibrato": 0.22, "breath": 0.25, "bright": 0.55},
             "humanize_ms": 12, "push_ms": 6, "send_reverb": 0.35, "gain_db": -4, "pan": -0.25,
             "fx": [{"type": "hpf", "hz": 140}, {"type": "lpf", "hz": 9000}, {"type": "comp", "threshold_db": -20, "ratio": 3}]},
}

# ------------------------------------------------------------------ the song's material
V_FIG = ["A", "F#m", "D", ("Es", "E")]
V_CH = "Aadd9:16 F#m7:16 Dadd9:16 Esus4:8 E:8"
P_FIG = ["Bm", "A/C#", "D", ("Es", "E")]
P_CH = "Bm7:16 A/C#:16 D:16 Esus4:8 E:8"
C_FIG = ["D", "A", "E", "F#m", "D", "A", "E", "E"]
C_CH = "D:16 A:16 E:16 F#m:16 D:16 A:16 E:16 E:16"
T_FIG = ["F#m", "C#m", "G", ("Es", "E")]
T_CH = "F#m:16 C#m:16 G:16 Esus4:8 E:8"
B_CH = "D:16 Dm:16 A:16 A:16 D:16 Dm:16 Esus4:16 E:16"

# the hook: "here-you-are" on dotted eighths, the carousel's own rhythm
HOOK = ("0:F#5:3 3:E5:3 6:A5:8 18:A5:2 20:G#5:2 22:E5:6 "
        "32:E5:3 35:D5:3 38:G#5:8 50:G#5:2 52:F#5:2 54:C#5:6 "
        "64:F#5:3 67:E5:3 70:A5:8 82:A5:2 84:G#5:2 86:A5:6 "
        "96:B5:4 100:A5:4 104:G#5:4 108:E5:4 112:F#5:3 115:E5:9")
# the last chorus: the top note held (pride)
HOOKPEAK = ("0:F#5:3 3:E5:3 6:A5:8 18:A5:2 20:G#5:2 22:E5:6 "
            "32:E5:3 35:D5:3 38:G#5:8 50:G#5:2 52:F#5:2 54:C#5:6 "
            "64:F#5:3 67:E5:3 70:A5:8 82:A5:2 84:B5:2 86:C#6:10~ "
            "96:B5:4 100:A5:4 104:G#5:4 108:E5:4 112:F#5:3 115:A5:11")
# the hook come home: the same three-note cell over the verse chords (love)
HOOKHOME = ("0:C#5:3 3:B4:3 6:E5:8 18:E5:2 20:C#5:2 22:A4:6 "
            "32:F#5:3 35:E5:3 38:A5:8 50:G#5:2 52:F#5:2 54:E5:6 "
            "64:C#5:3 67:B4:3 70:E5:8 82:E5:2 84:F#5:2 86:A5:6 "
            "96:F#5:3 99:E5:3 102:A5:8 112:B5:4 116:G#5:4 120:E5:6")

# verse 1: nerves. short chattering phrases, narrow, low
VERSE1 = ("2:C#5:1 3:C#5:1 4:C#5:2 6:B4:2 8:A4:3 "
          "18:C#5:1 19:C#5:1 20:C#5:2 22:B4:2 24:A4:2 26:F#4:4 "
          "34:A4:2 36:B4:2 38:D5:4 42:C#5:2 44:B4:3 "
          "52:B4:2 54:C#5:2 56:B4:5 "
          "66:C#5:1 67:C#5:1 68:C#5:2 70:B4:2 72:A4:3 "
          "82:C#5:1 83:C#5:1 84:E5:2 86:C#5:2 88:B4:2 90:A4:4 "
          "98:A4:2 100:B4:2 102:D5:4 106:E5:2 108:D5:3 "
          "116:C#5:2 118:B4:2 120:E5:6")
VERSE1B = ("2:C#5:1 3:C#5:1 4:E5:2 6:C#5:2 8:B4:3 "
           "18:C#5:1 19:C#5:1 20:E5:2 22:C#5:2 24:B4:2 26:A4:4 "
           "34:A4:2 36:B4:2 38:D5:4 42:E5:2 44:F#5:3 "
           "52:E5:2 54:D5:2 56:B4:5 "
           "66:E5:1 67:E5:1 68:E5:2 70:C#5:2 72:B4:3 "
           "82:C#5:1 83:C#5:1 84:E5:2 86:F#5:2 88:E5:2 90:C#5:4 "
           "98:D5:2 100:E5:2 102:F#5:4 106:E5:2 108:D5:3 "
           "116:E5:2 118:D5:2 120:B4:6")
# verse 2a: the sleepless blur. the same tune, drawn out, sliding
VERSE2A = ("2:C#5:6 8:B4:4~ 12:A4:4~ "
           "18:C#5:6 24:B4:4~ 28:F#4:4~ "
           "34:A4:4 38:D5:6~ 44:C#5:4~ "
           "52:B4:10~ "
           "66:C#5:6 72:B4:4~ 76:A4:4~ "
           "82:E5:6 88:C#5:4~ 92:A4:4~ "
           "98:A4:4 102:D5:6~ 108:E5:4~ "
           "116:C#5:4~ 120:B4:8~")
# verse 2b: laughter. short sung phrases, the piano laughs in the gaps
VERSE2B = ("2:C#5:1 3:C#5:1 4:E5:2 6:C#5:2 8:B4:2 "
           "18:C#5:1 19:C#5:1 20:E5:2 22:F#5:2 24:E5:2 "
           "34:A4:2 36:B4:2 38:D5:2 40:E5:2 "
           "50:E5:2 52:D5:2 54:B4:3 "
           "66:E5:1 67:E5:1 68:E5:2 70:C#5:2 72:B4:2 "
           "82:C#5:1 83:C#5:1 84:E5:2 86:F#5:2 88:A5:2 "
           "98:D5:2 100:E5:2 102:F#5:2 104:E5:2 "
           "114:E5:2 116:F#5:2 118:G#5:2 120:B5:6")
LAUGH = ("11:A6:1:0.8 12:A6:1:0.7 13:F#6:1:0.65 14:E6:1:0.6 15:C#6:1:0.5 "
         "27:C#7:1:0.8 28:A6:1:0.7 29:A6:1:0.7 30:F#6:1:0.6 "
         "43:B6:1:0.8 44:B6:1:0.7 45:A6:1:0.65 46:F#6:1:0.6 47:D6:1:0.5 "
         "58:G#6:1:0.7 59:G#6:1:0.7 60:E6:1:0.6 62:B5:1:0.5 "
         "75:A6:1:0.8 76:A6:1:0.7 77:F#6:1:0.65 78:E6:1:0.6 79:C#6:1:0.5 "
         "91:C#7:1:0.85 92:C#7:1:0.75 93:A6:1:0.7 94:F#6:1:0.6 95:E6:1:0.5 "
         "107:B6:1:0.8 108:A6:1:0.7 109:F#6:1:0.65 110:D6:1:0.6")
# grief for the old life: one pass of a lone guitar, the G natural is the door you came through
GRIEF = "0:A5:6 6:G#5:2 8:F#5:8 16:G#5:6 22:F#5:2 24:E5:8 32:D5:6 38:E5:2 40:G5:8 48:E5:4 52:F#5:4 56:G#5:8"
# tenderness so big it's almost fear
TENDER = ("2:F#4:2 4:A4:4 8:D5:8 18:D5:2 20:F5:6~ 26:E5:2 28:D5:4 32:C#5:12 "
          "66:F#4:2 68:A4:4 72:D5:8 82:D5:2 84:F5:6~ 90:A5:6~ 96:A5:12 112:G#5:14")

fillA = {"bars": 1, "kick": "x.......x.......", "snare": "....x...xxxx....", "tom1": "............xx..", "tom2": "..............xX"}

patterns = {
    # ---------------- drums
    "v1beat": {"bars": 1, "kick": "x...x...x...x...", "phat": "..x...x...x...x.", "snare": "............g..."},
    "vbeat": {"bars": 1, "kick": "x.....x.x.......", "snare": "....x.......x...", "hat": "x.x.x.x.x.x.x.x."},
    "vfill": {"bars": 1, "kick": "x.....x.x.......", "snare": "....x.....o.x.xx", "hat": "x.x.x.x.x......."},
    "prebeat": {"bars": 4, "kick": "x..x............" * 3 + "x..x....x...x...", "bell": "x...x...x...x..." * 3 + "x...x...........",
                "snare": "." * 48 + "........o.x.xxXX"},
    "cbeat": {"bars": 1, "kick": "x..x..x...x.....", "snare": "....X.......X...", "ohat": "x.x.x.x.x.x.x.x.", "tamb": "xxxxxxxxxxxxxxxx"},
    "cbeat4": {"bars": 1, "kick": "x..x..x..x..x.x.", "snare": "....X.......X...", "ohat": "x.x.x.x.x.x.x.x.", "tamb": "xxxxxxxxxxxxxxxx", "bell": "x...x...x...x..."},
    "crash8": {"bars": 8, "crash": "X" + "." * 127},
    "crash4": {"bars": 4, "crash": "X" + "." * 63},
    "fillA": fillA,
    "tagbeat": {"bars": 1, "kick": "x..............."},
    "blurbeat": {"bars": 4, "kick": "x.........x.....x...............x.........x.....x.....x.........",
                 "snare": "........x...............x...............x................o......",
                 "ride": "x...x...x...x..." * 4},
    "lbeat": {"bars": 1, "kick": "x.....x.x..x....", "snare": "....x.......x...", "hat": "x.x.x.x.x.x.x...", "ohat": "..............x."},
    "heart": {"bars": 8, "kick": "x..x....x..x...." * 5 + "." * 16 + "x..x....x..x...." * 2},
    "liftbeat": {"bars": 4, "kick": "x..x....x..x...." * 2 + "x...x...x...x..." * 2,
                 "tom2": "." * 32 + "x.x.x.x.x.x.x.x." + "x.x.x.x.........",
                 "snare": "." * 48 + "........x.x.XXXX", "tom1": "." * 64},
    "obeat": {"bars": 1, "kick": "x.....x...x.....", "snare": "....x.......x...", "ride": "x.x.x.x.x.x.x.x.", "tamb": "xxxxxxxxxxxxxxxx"},
    # ---------------- music
    "introA": {"bars": 4, "figM": fig(V_FIG)},
    "introB": {"bars": 4, "figM": fig(V_FIG), "bass": bass(["A2"] * 4, vel=0.55, ln=1)},
    "verse1": {"bars": 8,
               "figM": fig(V_FIG * 2),
               "bass": bass(["A2"] * 8, vel=0.55, ln=1),
               "voxV": VERSE1},
    "verse1b": {"bars": 8,
                "figM": fig(V_FIG * 2),
                "bass": bass(["A2", "F#2", "D2", "E2"] * 2, vel=0.7),
                "chug": {"chords": V_CH + " " + V_CH, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.7, "strum": "down", "strum_ms": 5},
                "voxV": VERSE1B},
    "pre": {"bars": 4,
            "fig": fig(P_FIG, only_acc=True, acc=0.7),
            "gtrR": {"chords": P_CH, "style": "strum", "voicing": "guitar", "register": "B2", "vel": 0.6, "strum_ms": 25},
            "bass": bass(["B2", "C#3", "D3", "E3"], rhythm="x...............", ln=16, vel=0.8),
            "voxC": "0:D5:12 16:E5:12 32:F#5:14 48:A5:8~ 56:G#5:6"},
    "pre2v": {"bars": 4, "voxD": "0:B4:12 16:C#5:12 32:D5:14 48:E5:14"},
    "chorus": {"bars": 8,
               "fig": fig(C_FIG),
               "gtrL": {"chords": C_CH, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.85, "strum": "down", "strum_ms": 7},
               "gtrR": {"chords": C_CH, "style": "stabs", "rhythm": "x..x..x.x.x.x.x.", "voicing": "guitar", "register": "D3", "stab_len": 3, "vel": 0.8, "strum": "alt", "strum_ms": 14},
               "bass": bass(["D2", "A2", "E2", "F#2", "D2", "A2", "E2", "E2"], rhythm="X.xx.xX.x.X.x.x.", vel=0.85)},
    "chorusT": {"bars": 8,
                "fig": fig(["Dh", "Ah", "Eh", "F#mh", "Dh", "Ah", "Eh", "Eh"]),
                "gtrL": {"chords": C_CH, "style": "stabs", "rhythm": "x..x..x..x..x.x.", "voicing": "power", "register": "A2", "stab_len": 3, "vel": 0.9, "strum": "down", "strum_ms": 7},
                "gtrR": {"chords": C_CH, "style": "stabs", "rhythm": "x..x..x..x..x.x.", "voicing": "guitar", "register": "D3", "stab_len": 3, "vel": 0.85, "strum": "down", "strum_ms": 14},
                "bass": bass(["D2", "A2", "E2", "F#2", "D2", "A2", "E2", "E2"], rhythm="X..x..x..x..x.x.", ln=3, vel=0.9)},
    "hook": {"bars": 8, "voxC": HOOK},
    "hookpeak": {"bars": 8, "voxC": HOOKPEAK},
    "hookD": {"bars": 8, "voxD": octave(HOOK, -1)},
    "hookDhalf": {"bars": 8, "voxD": " ".join(t for t in octave(HOOK, -1).split() if int(t.split(":")[0]) >= 64)},
    "hookpeakD": {"bars": 8, "voxD": octave(HOOKPEAK, -1)},
    "leadhook": {"bars": 8, "lead": HOOK},
    "leadpeak": {"bars": 8, "lead": HOOKPEAK},
    "claugh": {"bars": 8, "piano": "27:C#7:1:0.8 28:A6:1:0.7 29:A6:1:0.7 30:E6:1:0.6 59:C#7:1:0.8 60:A6:1:0.7 61:F#6:1:0.65 62:F#6:1:0.6 63:C#6:1:0.5 91:E7:1:0.85 92:C#7:1:0.75 93:C#7:1:0.7 94:A6:1:0.65 95:E6:1:0.55"},
    "cpad": {"bars": 8, "organ": {"chords": C_CH, "style": "sustain", "register": "E3", "voicing": "close", "vel": 0.6}},
    "tag": {"bars": 4,
            "fig": fig(T_FIG, acc=0.7, soft=0.4),
            "bass": bass(["F#2", "C#3", "G2", "E2"], rhythm="x.........x.....", ln=6, vel=0.75),
            "gtrR": {"chords": T_CH, "style": "strum", "voicing": "guitar", "register": "D3", "vel": 0.55, "strum_ms": 25},
            "lead": GRIEF},
    "verse2a": {"bars": 8,
                "figB": fig(V_FIG * 2, acc=0.8, soft=0.5, ln=3),
                "bass": bass([("A2", "A2"), ("F#2", "F#2"), ("D2", "D2"), ("E2", "E2")] * 2, rhythm="x.......x.......", ln=7, vel=0.7),
                "voxB": VERSE2A},
    "verse2b": {"bars": 8,
                "fig": fig(V_FIG * 2),
                "bass": bass(["A2", "F#2", "D2", "E2"] * 2, rhythm="x..x..x.x..x..x.", vel=0.8),
                "gtrL": {"chords": V_CH + " " + V_CH, "style": "stabs", "rhythm": "..x...x...x...x.", "voicing": "guitar", "register": "A3", "stab_len": 1, "vel": 0.7, "strum": "up", "strum_ms": 8},
                "chug": {"chords": V_CH + " " + V_CH, "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.7, "strum": "down", "strum_ms": 5},
                "voxV": VERSE2B,
                "piano": LAUGH},
    "bridge": {"bars": 8,
               "mbox": " ".join(t for t in fig(["D", "Dm", "A", "A", "D", "Dm", "Es", "E"], only_acc=True, acc=0.7).split() if not (83 < int(t.split(":")[0]) < 96)),
               "figM": {"chords": "D:16 Dm:16 A:16 A:16 D:16 -:16 Esus4:16 E:16", "style": "strum", "voicing": "guitar", "register": "D3", "vel": 0.5, "strum_ms": 40},
               "bass": bass(["D2", "D2", "A2", "A2", "D2", None, "E2", "E2"], rhythm="x...............", ln=16, vel=0.7),
               },
    "bridgeV": {"bars": 8, "voxB": TENDER},
    "lift": {"bars": 4,
             "fig": fig(["F#m", "D", "Es", "E"]),
             "chug": {"chords": "-:32 Esus4:16 E:16", "style": "stabs", "rhythm": "x.x.x.x.x.x.x.x.", "voicing": "power", "register": "A2", "stab_len": 2, "vel": 0.75, "strum": "down", "strum_ms": 5},
             "bass": bass([None, None, "E2", "E2"], vel=0.8),
             "voxC": "0:C#5:12 16:D5:12 32:E5:14 48:G#5:12"},
    "outro": {"bars": 8,
              "fig": fig(["Ah", "F#mh", "Dh", "Eh"] * 2),
              "gtrL": {"chords": V_CH + " " + V_CH, "style": "stabs", "rhythm": "x.........x.....", "voicing": "power", "register": "A2", "stab_len": 9, "vel": 0.75, "strum": "down", "strum_ms": 10},
              "gtrR": {"chords": V_CH + " " + V_CH, "style": "stabs", "rhythm": "x.....x.........", "voicing": "guitar", "register": "D3", "stab_len": 10, "vel": 0.75, "strum": "down", "strum_ms": 22},
              "bass": bass(["A2", "F#2", "D2", "E2"] * 2, rhythm="X.xx.xX.x.X.x.x.", vel=0.85),
              "organ": {"chords": V_CH + " " + V_CH, "style": "sustain", "register": "A3", "voicing": "close", "vel": 0.6},
              "voxC": HOOKHOME,
              "voxD": octave(VERSE1, -1),
              "lead": shift("0:A5:6 6:G#5:2 8:F#5:8 16:G#5:6 22:F#5:2 24:E5:8", 32) + " " + shift("0:C#6:6 6:B5:2 8:A5:8 16:B5:6 22:A5:2 24:G#5:8", 96),
              "piano": " ".join(t for t in LAUGH.split() if int(t.split(":")[0]) < 32) + " " + shift(" ".join(t for t in LAUGH.split() if int(t.split(":")[0]) < 32), 64)},
    "outEnd": {"bars": 4,
               "bass": "0:A2:16",
               "gtrR": {"chords": "A:16", "style": "stabs", "rhythm": "x...............", "voicing": "guitar", "register": "D3", "stab_len": 16, "vel": 0.8, "strum": "down", "strum_ms": 30},
               "gtrL": {"chords": "A5:16", "style": "stabs", "rhythm": "x...............", "voicing": "power", "register": "A2", "stab_len": 16, "vel": 0.75, "strum": "down", "strum_ms": 12},
               "organ": {"chords": "A:16", "style": "sustain", "register": "A3", "voicing": "close", "vel": 0.5},
               "voxC": "0:A5:12",
               "kick": "x" + "." * 63, "crash": "X" + "." * 63},
    "coda": {"bars": 4, "figM": fig(["A", "F#m", "A"]) + " 48:E5:2:0.8 49:A4:2:0.45 50:C#5:2:0.45 51:E5:2:0.7 52:A4:2:0.4 53:C#5:2:0.4 54:E5:4:0.6"},
}

full_arr = [
    {"name": "intro", "bars": 4, "play": ["introA"]},
    {"name": "intro2", "bars": 4, "play": ["introB", "v1beat"], "auto": {"kick": {"gain_db": -6}, "bass": {"gain_db": -5}}},
    {"name": "verse1a", "bars": 8, "play": ["verse1", "v1beat"], "auto": {"kick": {"gain_db": -5}, "bass": {"gain_db": -5}}},
    {"name": "verse1b", "bars": 8, "play": ["verse1b", "vbeat"], "fill": {"pattern": "vfill"},
     "auto": {"kick": {"gain_db": -4}, "snare": {"gain_db": -8}, "chug": {"gain_db": -4}, "bass": {"gain_db": -5}}},
    {"name": "pre1", "bars": 4, "play": ["pre", "prebeat"], "auto": {"kick": {"gain_db": -3}, "bass": {"gain_db": -6}, "gtrR": {"gain_db": -4}, "voxC": {"gain_db": -3}}},
    {"name": "chorus1", "bars": 8, "play": ["chorus", "hook", "cbeat", "crash8", "cpad"], "auto": {"organ": {"gain_db": -4}}},
    {"name": "tag", "bars": 4, "play": ["tag", "tagbeat", "crash4"], "auto": {"kick": {"gain_db": -5}, "lead": {"gain_db": 2}, "bass": {"gain_db": -4}}},
    {"name": "verse2a", "bars": 8, "play": ["verse2a", "blurbeat"], "auto": {"kick": {"gain_db": -5}, "snare": {"gain_db": -6}, "ride": {"gain_db": -2}, "bass": {"gain_db": -4}}},
    {"name": "verse2b", "bars": 8, "play": ["verse2b", "lbeat"], "fill": {"pattern": "fillA"},
     "auto": {"kick": {"gain_db": -2}, "snare": {"gain_db": -2}, "gtrL": {"gain_db": -5}, "bass": {"gain_db": -3}}},
    {"name": "pre2", "bars": 4, "play": ["pre", "prebeat", "pre2v"], "auto": {"kick": {"gain_db": -3}, "bass": {"gain_db": -6}, "voxD": {"gain_db": -4}, "gtrR": {"gain_db": -4}, "voxC": {"gain_db": -3}}},
    {"name": "chorus2", "bars": 8, "play": ["chorus", "hook", "cbeat", "crash8", "cpad", "hookDhalf", "claugh"], "auto": {"piano": {"gain_db": 3}}},
    {"name": "bridge", "bars": 8, "play": ["bridgeV", "bridge", "heart"], "auto": {"kick": {"gain_db": -8}, "bass": {"gain_db": -5}, "voxB": {"gain_db": -2}}},
    {"name": "lift", "bars": 4, "play": ["lift", "liftbeat"],
     "auto": {"chug": {"gain_db": [-12, 0]}, "kick": {"gain_db": [-8, 0]}, "tom2": {"gain_db": [-12, 0]}, "fig": {"gain_db": [-3, 1]}, "bass": {"gain_db": [-8, 0]}},
     "exit": {"cut": {"tracks": "all", "beats": 1}}},
    {"name": "chorus3", "bars": 8, "play": ["chorus", "hook", "cbeat", "crash8", "cpad", "hookD", "leadhook"], "fill": {"pattern": "fillA"}},
    {"name": "chorus4", "bars": 8, "play": ["chorusT", "hookpeak", "cbeat4", "crash4", "cpad", "hookpeakD", "leadpeak"]},
    {"name": "outro", "bars": 8, "play": ["outro", "obeat", "crash8"], "auto": {"gtrL": {"gain_db": -3}, "gtrR": {"gain_db": -2}, "kick": {"gain_db": -2}, "snare": {"gain_db": -3}, "lead": {"gain_db": 4}, "piano": {"gain_db": 4}, "bass": {"gain_db": -2}}},
    {"name": "coda", "bars": 4, "play": ["coda", "outEnd"]},
]

loop_arr = [s for s in full_arr if s["name"] in ("verse1a", "pre1", "chorus1")]
arrangement = loop_arr if LOOP else full_arr

project = {
    "title": "Here You Are",
    "bpm": 136,
    "swing": 0.5,
    "seed": 9,
    "tracks": tracks,
    "patterns": patterns,
    "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -6, "lpf": 8000},
            "delay": {"beats": 0.75, "feedback": 0.3, "return_db": -9, "lpf": 4500}},
    "master": {"lufs": -10, "sat": 0.1, "glue": True},
}

json.dump(project, open(os.path.join(HERE, "project.json"), "w"), indent=1)
bars = sum(s["bars"] for s in arrangement)
print("project.json written:", bars, "bars, %d:%02d" % divmod(int(bars * 4 * 60 / project["bpm"]), 60))
