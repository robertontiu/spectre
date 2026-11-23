import json
from trem import expand, octave

RIFF = ("0:D4:2 2:D4:2 4:Eb4:2 6:D4:2 8:Eb4:4:t 12:D4:2 14:C4:2 "
        "32:G4:2 34:G4:2 36:A4:2 38:G4:2 40:F#4:2 42:Eb4:2 44:F#4:2 46:G4:2")
DRONE = "16:D4:16:t 48:D4:16:t"

ANS = ("16:D4:2 18:D4:2 20:Eb4:2 22:Eb4:2 24:D4:6 "
       "48:Eb4:2 50:Eb4:2 52:D4:2 54:C4:2 56:D4:6")

tracks = {
 "kick": {"inst": {"type": "kick", "tune": 62, "decay": 0.14, "punch": 1.8, "click": 0.7, "drive": 0.7},
          "gain_db": -2, "humanize_ms": 2,
          "fx": [{"type": "drive", "db": 4}, {"type": "eq", "hz": 62, "gain_db": -4, "q": 1.1}, {"type": "eq", "hz": 2500, "gain_db": 3, "q": 0.9}, {"type": "gain", "db": -4}]},
 "snare": {"inst": {"type": "snare", "tone": 200, "decay": 0.07, "snap": 0.8, "body": 1.0, "drive": 0.8},
           "gain_db": 3, "humanize_ms": 2, "send_reverb": 0.05,
           "fx": [{"type": "hpf", "hz": 120}, {"type": "drive", "db": 4}, {"type": "eq", "hz": 180, "gain_db": -2, "q": 1.0}, {"type": "highshelf", "hz": 3500, "gain_db": -7}]},
 "clap": {"inst": {"type": "clap", "tone": 1200, "decay": 0.12, "spread": 1.0},
          "gain_db": 9, "push_ms": -6, "width": 0.8, "send_reverb": 0.08,
          "fx": [{"type": "hpf", "hz": 200}, {"type": "drive", "db": 4}, {"type": "highshelf", "hz": 4000, "gain_db": -4}]},
 "hat": {"inst": {"type": "hat", "decay": 0.035, "tone": 8500}, "gain_db": 8, "pan": 0.2, "humanize_ms": 3,
         "dyn": [1.0, 0.55, 0.8, 0.6], "roll_pitch": 0,
         "fx": [{"type": "hpf", "hz": 400}, {"type": "highshelf", "hz": 5000, "gain_db": -4}]},
 "stomp": {"inst": {"type": "tom", "tune": 147, "decay": 0.12}, "gain_db": 1, "width": 0.3,
           "fx": [{"type": "hpf", "hz": 130}, {"type": "drive", "db": 8}, {"type": "eq", "hz": 170, "gain_db": -5, "q": 1.2}, {"type": "eq", "hz": 700, "gain_db": 4, "q": 0.9},
                  {"type": "highshelf", "hz": 4000, "gain_db": -4}]},
 "doum": {"inst": {"type": "darbuka", "stroke": "doum", "tune": 1.048, "decay": 0.16}, "gain_db": -4, "pan": -0.1,
          "fx": [{"type": "hpf", "hz": 90}]},
 "tek": {"inst": {"type": "darbuka", "stroke": "tek"}, "gain_db": 5, "pan": -0.45, "humanize_ms": 4,
         "fx": [{"type": "hpf", "hz": 300}]},
 "ka": {"inst": {"type": "darbuka", "stroke": "ka"}, "gain_db": 2, "pan": 0.5, "humanize_ms": 5, "vel_jitter": 0.1,
        "fx": [{"type": "hpf", "hz": 300}]},
 "808": {"inst": {"type": "808", "decay": 0.9, "drive": 0.8, "punch": 0.8, "tone": 0.5, "glide_ms": 70},
         "gain_db": -7, "legato": 0.95, "sidechain": {"source": "kick", "depth": 0.55, "release_ms": 90},
         "fx": [{"type": "drive", "db": 10}, {"type": "sat", "amount": 0.5}, {"type": "eq", "hz": 39, "gain_db": -6, "q": 1.2}, {"type": "eq", "hz": 52, "gain_db": 3, "q": 1.2}, {"type": "eq", "hz": 85, "gain_db": 5, "q": 0.7},
                {"type": "lpf", "hz": 3000}, {"type": "eq", "hz": 700, "gain_db": 3, "q": 0.9}, {"type": "gain", "db": -7}]},
 "oud": {"inst": {"type": "oud", "damp": 0.994, "bright": 0.7}, "gain_db": 4, "pan": -0.1, "send_reverb": 0.15,
         "fx": [{"type": "hpf", "hz": 150}, {"type": "drive", "db": 6}, {"type": "eq", "hz": 1200, "gain_db": 2, "q": 0.8},
                {"type": "highshelf", "hz": 5000, "gain_db": -3}]},
 "oudLo": {"inst": {"type": "oud", "damp": 0.993, "bright": 0.5, "transpose": -12}, "gain_db": 1, "pan": 0.25, "push_ms": 4,
         "send_reverb": 0.1, "fx": [{"type": "hpf", "hz": 120}, {"type": "drive", "db": 8}, {"type": "highshelf", "hz": 4000, "gain_db": -4}]},
 "crowd2": {"inst": {"type": "choir", "vowel": "oh", "attack": 0.05, "release": 0.25}, "gain_db": 12, "pan": 0.55, "width": 0.9,
           "humanize_ms": 14, "push_ms": 8, "send_reverb": 0.35,
           "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 640, "gain_db": -3, "q": 1.2}, {"type": "chorus", "rate": 0.7, "depth": 0.6, "mix": 0.5}, {"type": "drive", "db": 6}]},
 "ney": {"inst": {"type": "ney", "breath": 0.75, "vibrato": 0.25, "attack": 0.015, "glide_ms": 60}, "gain_db": -3, "legato": 0.8, "pan": 0.05,
         "send_reverb": 0.2, "send_delay": 0.12,
         "fx": [{"type": "hpf", "hz": 350}, {"type": "eq", "hz": 600, "gain_db": -3, "q": 1.0}, {"type": "drive", "db": 12}, {"type": "eq", "hz": 1800, "gain_db": 4, "q": 0.8}, {"type": "highshelf", "hz": 6000, "gain_db": -5}]},
 "crowd3": {"inst": {"type": "choir", "vowel": "ee", "attack": 0.04, "release": 0.2}, "gain_db": 6, "pan": 0.0, "width": 1.0,
           "humanize_ms": 12, "push_ms": 4, "send_reverb": 0.3,
           "fx": [{"type": "hpf", "hz": 300}, {"type": "chorus", "rate": 0.5, "depth": 0.5, "mix": 0.5}, {"type": "drive", "db": 5}, {"type": "highshelf", "hz": 5000, "gain_db": -4}]},
 "crowd": {"inst": {"type": "choir", "vowel": "ah", "attack": 0.03, "release": 0.2}, "gain_db": 10, "pan": -0.45, "width": 0.9, "humanize_ms": 10,
           "send_reverb": 0.3, "fx": [{"type": "hpf", "hz": 150}, {"type": "eq", "hz": 640, "gain_db": -3, "q": 1.2}, {"type": "drive", "db": 6}]},
}

CROWD = lambda spec: {"crowd": expand(spec) + " " + expand(octave(spec)), "crowd2": expand(spec) + " " + expand(octave(spec))}

patterns = {
 # the crowd's body: stomp, stomp, CLAP
 "body":  {"bars": 1, "stomp": "X...X.......o...", "clap": "........X......."},
 "drums": {"bars": 1, "kick": "X.....x...X..x..", "snare": "........X.......", "hat": "x.x.x.x.x.xrx.x."},
 "drumsV": {"bars": 1, "kick": "X.........X.....", "snare": "........X.......", "hat": "x.x.x.x.x.x.x.x."},
 "drumsV4": {"bars": 4, "kick": "X.........X.....X.........X.....X.........X.....X.........X..x..",
             "snare": "........X...............X...............X...............X......o",
             "hat": "x.x.x.x.x.x.x.x.x.x.x.x.x.xtx.x.x.x.x.x.x.x.x.x.x.x.x.x.x.x.xrxt"},
 "darb":  {"bars": 1, "doum": "X.......X.......", "tek": "..x...x.....x...", "ka": "...o.o....o..o.o"},
 "darbHot": {"bars": 1, "doum": "X.....x.X.......", "tek": "..X...x...X.x.X.", "ka": "o.o.oo.oo.o.o.oo"},
 "darbLite": {"bars": 1, "tek": "..x...x.....x...", "ka": "...o.o....o..o.o"},
 "bassA": {"bars": 4,
   "808": "0:D1:6! 6:D1:4 10:D1:3 13:Eb1:3~ 16:D1:6! 22:D1:4 26:C1:2 28:D1:4~ "
          "32:D1:6! 38:D1:4 42:D1:3 45:Eb1:3~ 48:D1:6! 54:D1:2 56:A1:4~ 60:G1:4~"},
 "bassV": {"bars": 4,
   "808": "0:D1:10! 10:D1:6 16:D1:10! 26:C1:6~ 32:D1:10! 42:D1:6 48:D1:8! 56:A1:4~ 60:G1:4~"},
 "oudA": {"bars": 4, "oud": expand(RIFF), "oudLo": expand(RIFF + " " + DRONE)},
 "oudCall": {"bars": 4, "oud": expand(RIFF)},
 "oudV": {"bars": 4, "oudLo": expand("0:D4:2 2:D4:2 4:Eb4:2 6:D4:2 8:Eb4:4:t 12:D4:2 14:C4:2 48:D4:16:t")},
 "crowdA": {"bars": 4, **CROWD(ANS)},
 "neyCall": {"bars": 4, "ney": "0:D5:3! 3:Eb5:1 4:D5:2 6:C5:1 7:D5:1~ 8:Eb5:4~ 12:D5:2 14:C5:2~ "
                               "32:G5:2! 34:A5:1 35:G5:1 36:A5:2~ 38:G5:2 40:F#5:2~ 42:Eb5:2 44:F#5:2~ 46:G5:2"},
 "crowdA1": {"bars": 4, "crowd": expand(ANS) + " " + expand(octave(ANS))},
 "crowdA3": {"bars": 4, **CROWD(ANS), "crowd3": expand(octave(ANS, 1)) + " " + expand(ANS)},
 "crowdV": {"bars": 4, **CROWD("48:Eb4:2 50:Eb4:2 52:D4:2 54:C4:2 56:D4:6")},
 "marchHits": {"bars": 1, "stomp": "X...X...X...X...", "clap": "........X......."},
 "chantHold": {"bars": 4, **CROWD("0:D4:14 16:Eb4:14 32:D4:14 48:Eb4:8 56:D4:8")},
 "snareRoll": {"bars": 1, "stomp": "X...X...X.X.X.X.", "clap": "........X...X.X.", "doum": "X.......X...X...",
               "tek": "x.x.x.x.xxxxTTTT", "ka": "o.o.o.o.........", "snare": "............x.xX"},
}

P = {"title": "untitled", "bpm": 140, "swing": 0.5, "seed": 3,
     "tracks": tracks, "patterns": patterns,
     "arrangement": [
        {"name": "intro", "bars": 8, "play": ["oudCall", "darbLite"],
         "auto": {"oud": {"lpf": [900, 6000]}, "tek": {"gain_db": [-8, 0]}, "ka": {"gain_db": [-8, 0]}}},
        {"name": "gather", "bars": 4, "play": ["oudA", "darb", "body", "crowdA"], "exit": {"cut": {"tracks": "all", "beats": 1}}},
        {"name": "hook1", "bars": 8, "play": ["drums", "body", "darb", "bassA", "oudA", "crowdA1"], "enter": {"crash": 0.7},
         "exit": {"cut": {"tracks": ["kick", "808", "hat", "oudLo"], "beats": 1}}},
        {"name": "verse1", "bars": 16, "play": ["drumsV4", "body", "darbLite", "bassV", "oudV", "crowdV"]},
        {"name": "hook2", "bars": 8, "play": ["drums", "body", "darb", "bassA", "oudA", "crowdA"], "enter": {"crash": 0.7},
         "exit": {"cut": {"tracks": ["kick", "808", "hat", "snare"], "beats": 2}}},
        {"name": "march", "bars": 8, "play": ["marchHits", "darb", "chantHold"], "fill": {"pattern": "snareRoll"},
         "auto": {"crowd": {"gain_db": [-8, 2]}, "crowd2": {"gain_db": [-8, 2]}}, "exit": {"cut": {"tracks": "all", "beats": 0.5}}},
        {"name": "verse2", "bars": 16, "play": ["drumsV4", "marchHits", "darb", "bassV", "oudV", "crowdV"], "enter": {"impact": 0.8}},
        {"name": "standoff", "bars": 4, "play": ["body", "neyCall", "crowdA3"],
         "auto": {"stomp": {"gain_db": [-4, 2]}, "clap": {"gain_db": [-2, 3]}}, "exit": {"cut": {"tracks": "all", "beats": 0.5}}},
        {"name": "hook3", "bars": 16, "play": ["drums", "body", "darbHot", "bassA", "oudA", "crowdA3", "neyCall"], "enter": {"crash": 0.8, "impact": 0.9},
         "auto": {"ka": {"gain_db": [5, 7]}, "tek": {"gain_db": [2, 3]}}},
        {"name": "outro", "bars": 8, "play": ["body", "darb", "oudCall", "crowdA"],
         "auto": {"crowd": {"lpf": [8000, 1500], "gain_db": [0, -6]}, "crowd2": {"lpf": [8000, 1500], "gain_db": [0, -6]}, "oud": {"lpf": [6000, 700], "gain_db": [0, -10]}, "stomp": {"gain_db": [0, -12]}, "clap": {"gain_db": [0, -12]},
                  "doum": {"gain_db": [0, -12]}, "tek": {"gain_db": [0, -12]}, "ka": {"gain_db": [0, -12]}}}],
     "mix": {"reverb": {"size": 0.7, "damping": 0.5, "return_db": -5, "lpf": 6500},
             "delay": {"beats": 0.75, "feedback": 0.3, "return_db": -8, "lpf": 3500}},
     "master": {"lufs": -10.5, "sat": 0.15, "tape": 0.0, "glue": True}}

json.dump(P, open("project.json", "w"), indent=1)
