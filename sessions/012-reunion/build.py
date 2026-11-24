#!/usr/bin/env python3
"""build.py [loop|full]: writes project.json for session 012 (Reunion).
All carol material is counted in tune steps (12 steps = one 6/8 carol bar), B-flat as verified; the street tracks
carry "transpose": -2 (A-flat)."""
import json, sys, re

# ---- the verified melody, copied from docs/CAROLING.md "Verified melodies" (CAROL, R. S. Willis 1850)
PICKUP = "14:F4:2"          # carol_pickup: one bar, the upbeat at step 14 (= tune step -2)
CAROL = ("0:D5:4 4:C5:2 6:C5:2 8:Bb4:2 10:G4:2 12:F4:4 16:G4:2 18:F4:4 22:F4:2 24:G4:2 26:A4:2 28:Bb4:2 30:Bb4:2 "
         "32:C5:2 34:D5:2 36:C5:10 46:F4:2 48:D5:4 52:A4:2 54:C5:2 56:Bb4:2 58:G4:2 60:F4:4 64:G4:2 66:F4:4 70:F4:2 "
         "72:G4:4 76:G4:2 78:A4:2 80:G4:2 82:F4:2 84:Bb4:10 94:D5:2 96:D5:4 100:D4:2 102:D4:2 104:E4:2 106:F#4:2 "
         "108:G4:4 112:A4:2 114:Bb4:4 118:D5:2 120:C5:2 122:Bb4:2 124:A4:2 126:G4:2 128:A4:2 130:G4:2 132:F4:10 "
         "142:F4:2 144:D5:4 148:A4:2 150:C5:2 152:Bb4:2 154:G4:2 156:F4:4 160:G4:2 162:F4:4 166:F4:2 168:G4:4 "
         "172:G4:2 174:A4:2 176:G4:2 178:F4:2 180:Bb4:12")


def parse(s):
    out = []
    for tok in s.split():
        a = tok.split(":")
        out.append([float(a[0]) if "." in a[0] else int(a[0]), a[1], float(a[2]) if "." in a[2] else int(a[2])] + a[3:])
    return out


QUOTE5 = [n for n in parse(CAROL) if 94 <= n[0] <= 117]   # line 5, "Peace on the earth, good will to men"
# ---- my own tune ("the door tune"), B-flat, 6/8, same 12-step grid; line 5's slot holds the quote
MINE = parse("-2:F4:2 0:Bb4:4 4:C5:2 6:D5:4 10:Bb4:2 12:G4:4 16:Bb4:2 18:F4:4 "
             "22:Bb4:2 24:D5:4 28:C5:2 30:Bb4:4 34:G4:2 36:A4:10 "
             "46:F4:2 48:Bb4:4 52:C5:2 54:D5:4 58:Bb4:2 60:G4:4 64:Bb4:2 66:F4:4 "
             "70:F4:2 72:G4:4 76:Eb4:2 78:F4:4 82:A4:2 84:Bb4:10 "
             "118:Bb4:2 120:A4:4 124:G4:2 126:A4:4 130:Bb4:2 132:C5:10 "
             "142:F4:2 144:Bb4:4 148:C5:2 150:D5:4 154:Bb4:2 156:G4:4 160:Bb4:2 162:F4:4 "
             "166:F4:2 168:G4:4 172:Eb4:2 174:F4:4 178:A4:2 180:Bb4:12")
TUNE = sorted(MINE + QUOTE5, key=lambda n: n[0])
LINES = {1: (-2, 21), 2: (22, 45), 3: (46, 69), 4: (70, 93), 5: (94, 117), 6: (118, 141), 7: (142, 165), 8: (166, 191)}
MEL = {5: [4]}
WORDS = {5: "Peace on the earth _ good will to men"}
ALTO = parse("-2:D4:2 0:D4:4 4:Eb4:2 6:F4:4 10:D4:2 12:Eb4:4 16:G4:2 18:D4:4 22:D4:2 24:Bb4:4 28:A4:2 30:G4:4 34:Eb4:2 "
             "36:F4:10 46:D4:2 48:D4:4 52:Eb4:2 54:F4:4 58:D4:2 60:Eb4:4 64:G4:2 66:D4:4 70:D4:2 72:Eb4:4 76:C4:2 "
             "78:C4:4 82:Eb4:2 84:D4:10 94:D4:2 96:D4:4 100:D4:2 102:D4:4 106:D4:2 108:D4:4 112:D4:2 114:D4:4 "
             "118:D4:2 120:F4:4 124:F4:2 126:F4:4 130:G4:2 132:A4:10 142:D4:2 144:D4:4 148:Eb4:2 150:F4:4 154:D4:2 "
             "156:Eb4:4 160:G4:2 162:D4:4 166:D4:2 168:Eb4:4 172:C4:2 174:C4:4 178:Eb4:2 180:D4:12")
AMEL = {}
AWORDS = {5: "Peace on the earth good will to men"}
LOW = parse("-2:Bb3:2 0:Bb3:6 6:Bb3:6 12:Bb3:6 18:Bb3:4 22:Bb3:2 24:Bb3:6 30:Bb3:6 36:C4:10 46:Bb3:2 48:Bb3:6 54:Bb3:6 "
            "60:Bb3:6 66:Bb3:4 70:Bb3:2 72:C4:6 78:A3:6 84:Bb3:10 94:Bb3:2 96:Bb3:4 100:A3:8 108:Bb3:10 118:Bb3:2 "
            "120:C4:12 132:C4:10 142:Bb3:2 144:Bb3:12 156:Bb3:6 162:Bb3:4 166:Bb3:2 168:C4:6 174:A3:6 180:Bb3:12")
BASS = parse("0:Bb2:6 6:D3:6 12:Eb3:6 18:Bb2:6 24:G2:6 30:Eb3:6 36:C3:6 42:F3:6 48:Bb2:6 54:D3:6 60:Eb3:6 66:D3:6 "
             "72:C3:6 78:F2:6 84:Bb2:12 96:Bb2:4 100:A2:8 108:G2:12 120:A2:12 132:F3:6 138:Eb3:6 144:D3:6 150:Bb2:6 "
             "156:Eb3:6 162:F3:6 168:C3:6 174:F2:6 180:Bb2:12")
CH = [(0, "Bb", 6), (6, "Bb/D", 6), (12, "Eb", 6), (18, "Bb", 6), (24, "Gm", 6), (30, "Eb", 6), (36, "F/C", 6),
      (42, "F", 6), (48, "Bb", 6), (54, "Bb/D", 6), (60, "Eb", 6), (66, "Bb/D", 6), (72, "Cm", 6), (78, "F7", 6),
      (84, "Bb", 12), (96, "Bb", 4), (100, "D/A", 8), (108, "Gm", 12), (120, "F/A", 12), (132, "F", 6),
      (138, "F7/Eb", 6), (144, "Bb/D", 6), (150, "Bb", 6), (156, "Eb", 6), (162, "Bb/F", 6), (168, "Cm", 6),
      (174, "F7", 6), (180, "Bb", 12)]


def line_of(step):
    for k, (a, b) in LINES.items():
        if a <= step <= b:
            return k


def cut(notes, a, b, off=0, shorten_last=None, vel=None):
    """notes with a <= start <= b, shifted by off; as a token string"""
    out = []
    for n in notes:
        if a <= n[0] <= b:
            ln = n[2]
            out.append([n[0] + off, n[1], ln] + ([vel] if vel else n[3:]))
    if shorten_last and out:
        out[-1][2] = shorten_last
    return " ".join(":".join(str(x) for x in n) for n in out)


def sung(notes, mel, words, lines, off, syl="loo", wordlines=(), last_len=None):
    """a singer part for the given lines: notes + lyrics (one syllable per note, '_' on slurred notes)"""
    toks, lyr = [], []
    for L in lines:
        a, b = LINES[L]
        ns = [n for n in notes if a <= n[0] <= b]
        if L in wordlines:
            w = words[L].split()
            assert len(w) == len(ns), (L, len(w), len(ns))
            lyr += [x.strip("-") if x != "_" else "_" for x in w]
        else:
            for i, n in enumerate(ns):
                lyr.append("_" if (i in mel.get(L, []) or syl == "ooh" and i > 0) else syl)
        for n in ns:
            toks.append([n[0] + off, n[1], n[2]])
    if last_len:
        toks[-1][2] = last_len
    return {"notes": " ".join(":".join(str(x) for x in n) for n in toks), "lyrics": " ".join(lyr)}


def chords(a, b, off=0, lead=0, tail=0):
    """chord string covering tune steps a..b (exclusive end b), with `lead` steps of rest before"""
    out = ["-:%d" % lead] if lead else []
    for s, name, ln in CH:
        if s >= a and s < b:
            out.append("%s:%d" % (name, min(ln, b - s)))
    if tail:
        out.append("-:%d" % tail)
    return " ".join(out)


def svs(voice, pan, gain, rev, seed=1, lpf=None, extra=None, pre=40, shelf=2.0, **inst):
    fx = [{"type": "hpf", "hz": 110}, {"type": "eq", "hz": 850, "gain_db": -3.5, "q": 0.8},
          {"type": "eq", "hz": 2600, "gain_db": 4, "q": 0.55}, {"type": "eq", "hz": 2500, "gain_db": 6, "q": 2.5}, {"type": "eq", "hz": 3900, "gain_db": -5, "q": 2.6},
          {"type": "eq", "hz": 5300, "gain_db": 8.5, "q": 1.5},
          {"type": "highshelf", "hz": 4700, "gain_db": shelf + 9},
          {"type": "highshelf", "hz": 13000, "gain_db": 11}]
    if lpf:
        fx.append({"type": "lpf", "hz": lpf})
    fx += extra or []
    i = {"type": "singer", "source": "svs", "voice": voice, "seed": seed, "inhale": 0.3, "svs_fade_in_ms": 30,
         "svs_fade_out_ms": 140}
    i.update(inst)
    return {"inst": i, "gain_db": gain, "pan": pan, "send_reverb": rev, "reverb_predelay_ms": pre, "fx": fx,
            "humanize_ms": 0, "vel_jitter": 0.0}


STREET = [{"type": "room", "size": 0.25, "mix": 0.22, "damping": 0.7}]
ORG = {"type": "organ", "drawbars": [1, 0.55, 0.32, 0.24, 0.17, 0.14, 0.1, 0.1, 0.06, 0.06, 0.03, 0.03]}


def tracks():
    T = {}
    # the one outside (A-flat, dry street) and the same voice once inside (B-flat, the room)
    T["caller"] = svs("hanami", -0.05, 7, 0.04, seed=3, shelf=-3.0,
                      extra=[{"type": "highshelf", "hz": 9000, "gain_db": -6}] + STREET, transpose=-2)
    T["caller"]["push_ms"] = 35
    T["sop"] = svs("hanami", -0.38, 6, 0.3, seed=3)
    # the one who stayed: through the door (muffled), then in the room
    T["indoor"] = svs("hanami-dark", 0.2, 9, 0.5, seed=5, lpf=1100, transpose=-2)
    T["alto"] = svs("hanami-dark", 0.42, 3, 0.3, seed=5, shelf=4.0)
    # the others in the house
    T["low"] = svs("hanami-soft", 0.05, 1, 0.32, seed=9, shelf=3.0)
    T["sop_b"] = svs("hanami", -0.8, 2, 0.36, seed=11)
    T["alto_b"] = svs("hanami-soft", 0.8, 1, 0.36, seed=13)
    for k, ms in (("sop", 0), ("alto", 14), ("low", 22), ("sop_b", -9), ("alto_b", 27), ("indoor", 10)):
        T[k]["push_ms"] = ms      # a small group never lands together
    T["organ_door"] = {"inst": dict(ORG, transpose=-2), "gain_db": 9, "send_reverb": 0.45, "legato": 1.0,
                       "humanize_ms": 6, "width": 0.3,
                       "fx": [{"type": "lpf", "hz": 500}, {"type": "tremolo", "rate": 5.5, "depth": 0.06}]}
    T["organ"] = {"inst": dict(ORG), "gain_db": 6, "send_reverb": 0.3, "legato": 1.0, "humanize_ms": 8,
                  "vel_jitter": 0.04, "width": 0.55,
                  "fx": [{"type": "hpf", "hz": 120}, {"type": "lpf", "hz": 9000}, {"type": "eq", "hz": 2600, "gain_db": 4, "q": 0.8},
                         {"type": "tremolo", "rate": 5.5, "depth": 0.06}, {"type": "chorus", "rate": 0.4, "depth": 0.2, "mix": 0.2}]}
    T["pedal"] = {"inst": {"type": "organ", "drawbars": [1, 0.5, 0.15, 0.05]}, "gain_db": 11, "send_reverb": 0.2,
                  "legato": 1.0, "humanize_ms": 8, "fx": [{"type": "lpf", "hz": 900}, {"type": "eq", "hz": 140, "gain_db": 3, "q": 0.8}]}
    T["cello"] = {"inst": {"type": "strings", "attack": 0.25, "release": 0.5, "cutoff": 1400, "vibrato": 0.08,
                           "detune": 6}, "gain_db": 9, "send_reverb": 0.28, "legato": 1.0, "humanize_ms": 10,
                  "pan": 0.15, "fx": [{"type": "hpf", "hz": 60}, {"type": "lpf", "hz": 1100}]}
    # the parlour piano: the house's own voice for the tune (where a brass quartet on the corner would have stood)
    T["chorale"] = {"inst": {"type": "piano", "felt": 0.45, "release": 0.5}, "gain_db": 4, "send_reverb": 0.3,
                    "legato": 0.98, "humanize_ms": 12, "vel_jitter": 0.1, "pan": -0.15, "width": 0.2,
                    "fx": [{"type": "hpf", "hz": 110}, {"type": "highshelf", "hz": 4000, "gain_db": 4}]}
    bell = {"type": "bell", "ratio": 3.0, "decay": 1.3}
    bfx = [{"type": "hpf", "hz": 300}, {"type": "highshelf", "hz": 5500, "gain_db": -4}, {"type": "highshelf", "hz": 13000, "gain_db": 10}]
    T["bell_st"] = {"inst": dict(bell, transpose=-2), "gain_db": 12, "pan": 0.1, "send_reverb": 0.05,
                    "humanize_ms": 10, "vel_jitter": 0.1, "fx": bfx + [{"type": "lpf", "hz": 5000}] + STREET}
    T["bellL"] = {"inst": dict(bell), "gain_db": 12, "pan": -0.5, "send_reverb": 0.22, "humanize_ms": 14,
                  "vel_jitter": 0.12, "fx": bfx}
    T["bellR"] = {"inst": dict(bell, decay=1.2), "gain_db": 12, "pan": 0.5, "send_reverb": 0.22, "humanize_ms": 14,
                  "vel_jitter": 0.12, "fx": bfx}
    return T


def up(tokens, semis_oct=1):
    return re.sub(r":([A-G][b#]?)(\d)", lambda m: ":%s%d" % (m.group(1), int(m.group(2)) + semis_oct), tokens)


def project(mode):
    P = {"title": "Reunion", "bpm": 84, "swing": 0.5, "seed": 12, "tracks": tracks(), "patterns": {},
         "arrangement": [],
         "mix": {"reverb": {"size": 0.5, "damping": 0.6, "return_db": -7, "lpf": 6000}},
         "master": {"lufs": -14, "sat": 0.0, "tape": 0.0, "glue": False}}
    pat, arr = P["patterns"], P["arrangement"]
    if mode == "loop":
        # the core verse: three upper voices, organ, pedal; pickup bar + 12 bars
        pat["pk"] = {"bars": 1,
                     "sop": sung(TUNE, MEL, WORDS, [1], 16), "alto": sung(ALTO, AMEL, AWORDS, [1], 16),
                     "low": sung(LOW, {}, {}, [1], 16, syl="ooh")}
        for tr in ("sop", "alto", "low"):   # only the upbeat lives in the pickup bar
            n = pat["pk"][tr]["notes"].split()[0]; pat["pk"][tr] = {"notes": n, "lyrics": pat["pk"][tr]["lyrics"].split()[0]}
        body = {"bars": 12}
        for tr, src, mel, w in (("sop", TUNE, MEL, WORDS), ("alto", ALTO, AMEL, AWORDS)):
            d = sung(src, mel, w, range(1, 9), 0, wordlines=(5,))
            ns, ls = d["notes"].split(), d["lyrics"].split()
            body[tr] = {"notes": " ".join(ns[1:]), "lyrics": " ".join(ls[1:])}
        d = sung(LOW, {}, {}, range(1, 9), 0, syl="ooh")
        body["low"] = {"notes": " ".join(d["notes"].split()[1:]), "lyrics": " ".join(d["lyrics"].split()[1:])}
        body["organ"] = {"chords": chords(0, 192), "style": "sustain", "voicing": "close", "register": "D4", "vel": 0.6}
        body["pedal"] = cut(BASS, 0, 191)
        body["bellL"] = "36:C6:8:0.5 132:F5:8:0.5"
        body["bellR"] = "84:Bb5:8:0.5 180:Bb5:10:0.6 186:F5:6:0.4"
        pat["verse"] = body
        arr += [{"name": "pk", "bars": 1, "play": ["pk"]}, {"name": "verse", "bars": 12, "play": ["verse"]}]
    return P


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "full":
        from full import project as full_project
        P = full_project()
    else:
        P = project(mode)
    json.dump(P, open("project.json", "w"), indent=1)
    print("wrote project.json:", mode, sum(s["bars"] for s in P["arrangement"]), "bars")
