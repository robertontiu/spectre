"""Odell's builder: writes project.json. Edit here, run, render."""
import json, re

def trem(st, note, ln, vel=None):
    """tremolo 32nds on one note (cimbalom / cobza)."""
    out = []
    for i in range(int(ln * 2)):
        v = 0.95 if i == 0 else (0.6 if i % 2 else 0.75)
        if vel: v *= vel
        out.append(f"{st + i*0.5:g}:{note}:0.5:{v:.2f}")
    return " ".join(out)

def shift(spec, off):
    out = []
    for tok in spec.split():
        p = tok.split(":")
        p[0] = f"{float(p[0]) + off:g}"
        out.append(":".join(p))
    return " ".join(out)

def octave(spec, d=-1):
    return re.sub(r":([A-G][b#]?)(\d)", lambda m: f":{m.group(1)}{int(m.group(2))+d}", spec)

# ---------------------------------------------------------------- the motif (E Romanian minor)
FID = ("0:E4:4! 4:E4:2 6:G4:2 8:A#4:3~ 11:G4:1 12:F#4:4 "
       "16:E4:6! 22:B3:2 24:E4:4 "
       "32:E4:4! 36:E4:2 38:G4:2 40:F#4:2~ 42:E4:2 44:D4:4 "
       "48:E4:8! 56:B3:4 60:D4:2 62:E4:2")

tracks = {
 "kick": {"inst": {"type": "kick", "tune": 60, "decay": 0.1, "punch": 1.6, "click": 0.6, "drive": 0.6},
          "gain_db": -2, "humanize_ms": 2, "push_ms": -5,
          "fx": [{"type": "drive", "db": 3}, {"type": "eq", "hz": 2500, "gain_db": 2, "q": 0.9}, {"type": "gain", "db": -3}]},
 "snare": {"inst": {"type": "snare", "tone": 200, "decay": 0.05, "snap": 0.9, "body": 1.0, "drive": 0.9},
           "gain_db": 7, "humanize_ms": 2, "send_reverb": 0.0,
           "fx": [{"type": "hpf", "hz": 150}, {"type": "drive", "db": 6}, {"type": "eq", "hz": 1800, "gain_db": 3, "q": 1.0}, {"type": "highshelf", "hz": 4500, "gain_db": -8}]},
 "clap": {"inst": {"type": "clap", "tone": 1100, "decay": 0.06, "spread": 0.5},
          "gain_db": 10, "push_ms": -5, "width": 0.4, "send_reverb": 0.0,
          "fx": [{"type": "hpf", "hz": 250}, {"type": "drive", "db": 3}]},
 "hat": {"inst": {"type": "hat", "decay": 0.03, "tone": 8000}, "gain_db": 9, "pan": 0.2, "humanize_ms": 2,
         "fx": [{"type": "hpf", "hz": 500}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
 "toba": {"inst": {"type": "darbuka", "stroke": "doum", "tune": 1.0, "decay": 0.08}, "gain_db": -3, "pan": -0.15,
          "fx": [{"type": "hpf", "hz": 160}, {"type": "drive", "db": 8}, {"type": "eq", "hz": 900, "gain_db": 4, "q": 0.9}]},
 "808": {"inst": {"type": "808", "decay": 0.5, "drive": 0.7, "punch": 0.7, "tone": 0.45, "glide_ms": 60},
         "gain_db": -7, "legato": 0.85, "sidechain": {"source": "kick", "depth": 0.6, "release_ms": 90},
         "fx": [{"type": "drive", "db": 9}, {"type": "sat", "amount": 0.5}, {"type": "eq", "hz": 41, "gain_db": -4, "q": 1.2},
                {"type": "eq", "hz": 82, "gain_db": 4, "q": 0.8}, {"type": "lpf", "hz": 3000}, {"type": "eq", "hz": 700, "gain_db": 3, "q": 0.9},
                {"type": "gain", "db": -6}]},
 "fiddle": {"inst": {"type": "fiddle", "vibrato": 0.15, "grit": 0.75, "bow_noise": 0.25, "attack": 0.02, "glide_ms": 50},
            "gain_db": 4, "pan": 0.1, "legato": 0.85, "send_reverb": 0.12, "push_ms": 3,
            "fx": [{"type": "hpf", "hz": 200}, {"type": "drive", "db": 5}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
 "fidLo": {"inst": {"type": "fiddle", "vibrato": 0.1, "grit": 0.85, "bow_noise": 0.2, "attack": 0.03, "glide_ms": 60, "transpose": -12},
            "gain_db": 1, "pan": -0.2, "legato": 0.85, "send_reverb": 0.08, "push_ms": 9,
            "fx": [{"type": "hpf", "hz": 140}, {"type": "drive", "db": 7}, {"type": "eq", "hz": 250, "gain_db": -3, "q": 1.0}, {"type": "highshelf", "hz": 4000, "gain_db": -5}]},
 "cimb": {"inst": {"type": "cimbalom", "hard": 0.7, "damp": 0.3}, "gain_db": -5, "pan": 0.35, "width": 0.4, "humanize_ms": 3,
          "send_reverb": 0.18,
          "fx": [{"type": "hpf", "hz": 250}, {"type": "drive", "db": 4}, {"type": "eq", "hz": 600, "gain_db": -3, "q": 1.0}, {"type": "highshelf", "hz": 6000, "gain_db": -3}]},
 "nai": {"inst": {"type": "nai", "breath": 0.65, "vibrato": 0.12, "glide_ms": 70}, "gain_db": 6, "pan": -0.05, "legato": 0.95,
         "send_reverb": 0.25, "send_delay": 0.12,
         "fx": [{"type": "hpf", "hz": 300}, {"type": "drive", "db": 9}, {"type": "eq", "hz": 1500, "gain_db": 3, "q": 0.8}, {"type": "highshelf", "hz": 7000, "gain_db": -4}]},
 "cobza": {"inst": {"type": "oud", "damp": 0.975, "bright": 1.0}, "gain_db": 4, "pan": -0.3, "humanize_ms": 3,
           "send_reverb": 0.08,
           "fx": [{"type": "hpf", "hz": 300}, {"type": "drive", "db": 9}, {"type": "eq", "hz": 450, "gain_db": -3, "q": 1.0}, {"type": "eq", "hz": 2200, "gain_db": 3, "q": 1.0}, {"type": "highshelf", "hz": 6000, "gain_db": -4}]},
}

ACC = "XgoXgoXgoXgoXgXg"   # geamparale-style 3-3-3-3-2-2 accents on the clock

patterns = {
 "drums": {"bars": 1, "kick": "X.....x...X.....", "snare": "........X.......", "clap": "........X.......", "hat": ACC,
           "toba": "...x.........x.."},
 "bass": {"bars": 4, "808": "0:E1:5! 6:E1:3 10:E1:5 16:E1:5! 22:E1:3 26:G1:2 28:F#1:2~ 30:E1:2~ "
                            "32:E1:5! 38:E1:3 42:E1:5 48:E1:5! 54:E1:2 56:D2:3~ 60:C#2:2 62:B1:2~"},
 "fid": {"bars": 4, "fiddle": FID, "fidLo": FID},
 "cob": {"bars": 4, "cobza": {"chords": "Em:16 Em:16 Em:16 F#7:8 Em:8", "style": "stabs", "rhythm": "...x..x....x..x.",
                              "stab_len": 0.5, "register": "E3", "voicing": "close", "vel": 0.8}},
}

# ---------------------------------------------------------------- more patterns
FIDV = "0:E4:12! 12:F#4:2 14:G4:2 16:E4:14 32:E4:4! 36:E4:2 38:G4:2 40:F#4:2~ 42:E4:2 44:D4:4 48:E4:14"
CIMB = " ".join([trem(0, "E4", 8), trem(0, "B4", 8, 0.8), trem(8, "G4", 8), trem(8, "B4", 8, 0.8),
                 trem(16, "E4", 16), trem(16, "B4", 16, 0.8), trem(32, "E4", 8), trem(32, "B4", 8, 0.8),
                 trem(40, "G4", 8), trem(40, "B4", 8, 0.8), trem(48, "F#4", 8), trem(48, "A#4", 8, 0.8),
                 trem(56, "E4", 8), trem(56, "B4", 8, 0.8)])
DRONE = " ".join([trem(0, "E3", 64, 0.3), trem(0, "B3", 64, 0.22)])
# doina: a long held note, a cascade of ornaments, a fall to E -- but it keeps walking (8 bars)
DOINA = ("0:B4:10! 10:C#5:1 11:B4:1 12:A#4:2~ 14:B4:2 16:G4:6 22:A#4:1 23:G4:1 24:F#4:4~ 28:E4:4 "
         "32:B4:6! 38:C#5:1 39:B4:1 40:A#4:1 41:B4:1 42:A#4:2~ 44:G4:4 48:F#4:2 50:G4:1 51:F#4:1 52:E4:12 "
         "64:E5:8! 72:D5:1 73:E5:1 74:D5:2~ 76:C#5:2 78:B4:2 80:A#4:4~ 84:G4:4 88:F#4:2 90:G4:1 91:F#4:1 92:E4:4 "
         "96:B4:8 104:A#4:2~ 106:G4:2 108:F#4:2 110:E4:2 112:E4:16")

SAW = " ".join(f"{b*16+o}:{n}:{l}:{v}" for b in range(4) for o,n,l,v in [(0,"E4",2,0.95),(3,"E4",2,0.7),(6,"E4",2,0.8),(9,"E4",2,0.7),(12,"E4",1.5,0.85),(14,"B3" if b%2 else "E4",1.5,0.7)])
patterns.update({
 "saw": {"bars": 4, "fidLo": SAW},
 "clock": {"bars": 1, "hat": ACC},
 "knock": {"bars": 1, "toba": "...x.........x.."},
 "drumsV": {"bars": 4, "kick": "X.........X.....X.....x...X.....X.........X.....X.....x...X..x..",
            "snare": "........X...............X...............X...............X.......",
            "clap": "........X...............X...............X...............X.......",
            "hat": ACC + ACC + ACC + "XgoXgoXgoXgoXrXq",
            "toba": "...x.........x.....x.........x.....x.........x.....x......x..x.."},
 "drumsD": {"bars": 4, "kick": "X.....x.......x." "X.......x......." "X.....x.......x." "X.......x..x....",
            "snare": "........X.....o.........X..o............X.....o.........X...o.X.",
            "clap": "........X...............X...............X...............X.......",
            "hat": "X.x.X.x.XxxxX.x." "X.x.X.x.X.x.XtX." "X.x.X.x.XxxxX.x." "X.x.X.xtX.x.XqXz",
            "toba": "...x.........x.....x.........x.....x.........x.....x.........x.."},
 "bassV": {"bars": 4, "808": "0:E1:8! 10:E1:6 16:E1:8! 26:G1:2 28:F#1:3~ 32:E1:8! 42:E1:6 48:E1:8! 58:D2:3~ 61:B1:3~"},
 "bassD": {"bars": 4, "808": "0:E1:6! 6:E1:4 14:G1:2~ 16:E1:6! 24:B1:4~ 28:A#1:4~ 32:E1:6! 38:E1:4 46:G1:2~ 48:F#1:4! 52:E1:4~ 56:D2:4~ 60:E2:2~ 62:E1:2~"},
 "fidV": {"bars": 4, "fidLo": FIDV},
 "fidHi": {"bars": 4, "fiddle": FID},
 "cimb": {"bars": 4, "cimb": CIMB},
 "drone": {"bars": 4, "cimb": DRONE},
 "doina": {"bars": 8, "nai": DOINA},
})

arrangement = [
 {"name": "intro", "bars": 8, "play": ["fid", "cob", "clock", "knock"],
  "auto": {"fiddle": {"lpf": [700, 5000]}, "fidLo": {"lpf": [500, 4000]}, "hat": {"gain_db": [-12, 0]}, "cobza": {"lpf": [900, 8000]}},
  "exit": {"cut": {"tracks": "all", "beats": 1}}},
 {"name": "clockin", "bars": 4, "play": ["drumsV", "bassV", "cob"], "enter": {"impact": 0.6},
  "exit": {"cut": {"tracks": ["kick", "808"], "beats": 1}}},
 {"name": "hook1", "bars": 8, "play": ["drums", "bass", "fid", "cob"]},
 {"name": "verse1", "bars": 16, "play": ["drumsV", "bassV", "fidV", "cob"]},
 {"name": "hook2", "bars": 8, "play": ["drums", "bass", "fid", "cob", "cimb"],
  "exit": {"cut": {"tracks": ["kick", "808", "snare", "clap"], "beats": 2}}},
 {"name": "wall", "bars": 8, "play": ["clock", "knock", "drone", "doina", "saw"],
  "auto": {"hat": {"gain_db": [-6, -2]}, "cimb": {"lpf": [1500, 2500]}}},
 {"name": "push", "bars": 4, "play": ["clock", "knock", "cob", "fidV"], "auto": {"cobza": {"gain_db": [-8, 0]}},
  "exit": {"cut": {"tracks": "all", "beats": 0.5}}},
 {"name": "verse2", "bars": 16, "play": ["drumsD", "bassD", "fidV", "cob"], "enter": {"impact": 0.8}},
 {"name": "hook3", "bars": 16, "play": ["drums", "bass", "fid", "cob", "cimb"]},
 {"name": "outro", "bars": 8, "play": ["clock", "knock", "cob", "fidHi"],
  "auto": {"fiddle": {"lpf": [5000, 600], "gain_db": [0, -10]}, "cobza": {"gain_db": [0, -8]}, "hat": {"gain_db": [0, -10]}, "toba": {"gain_db": [0, -10]}}},
]

proj = {"title": "untitled", "bpm": 144, "swing": 0.5, "seed": 4, "tracks": tracks, "patterns": patterns,
        "arrangement": arrangement,
        "mix": {"reverb": {"size": 0.55, "damping": 0.6, "return_db": -6, "lpf": 6000},
                "delay": {"beats": 0.75, "feedback": 0.3, "return_db": -9, "lpf": 3000}},
        "master": {"lufs": -10.5, "sat": 0.15, "tape": 0.0, "glue": true if False else True}}
json.dump(proj, open("project.json", "w"), indent=1)
print("ok")
