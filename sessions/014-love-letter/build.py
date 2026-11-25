#!/usr/bin/env python3
"""build.py [loop|full]: writes project.json for session 014 (Love letter).
Bolero-bachata, 84 bpm, D major. Every melodic part is written per section as "bar.step:note:len[:vel]" tokens
(bar counted from 1 inside the section, step in 16ths); the accompaniment is generated from each section's chords."""
import json, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "full"
BPM = 84

# ---------------------------------------------------------------- harmony
VERSE = "D D#dim7 Em7 A7 Em7 A7 Dmaj7 D7".split()
ROOT = {"D": ("D2", "A2"), "Dmaj7": ("D2", "A2"), "D7": ("D2", "A2"), "Dadd9": ("D2", "A2"), "D6": ("D2", "A2"),
        "D#dim7": ("D#2", "A2"), "Em7": ("E2", "B2"), "A7": ("A1", "E2"), "A7sus4": ("A1", "E2"),
        "G": ("G2", "D3"), "Gm6": ("G2", "D3"), "F#m7": ("F#2", "C#3"), "B7": ("B1", "F#2"), "Bm": ("B1", "F#2"),
        "Bm7": ("B1", "F#2"), "F#7": ("F#2", "C#3"), "D/F#": ("F#2", "A2"), "Em7/A": ("A1", "E2")}

SECTIONS = [  # name, chords (one per bar), groove
    ("opening", "Em7 A7 Dmaj7 A7".split(), "bolero"),
    ("verse1", VERSE, "bolero"),
    ("chorus1", "G Gm6 F#m7 B7 Em7 A7 D A7".split(), "majao"),
    ("verse2", VERSE, "derecho"),
    ("chorus2", "G Gm6 F#m7 B7 Em7 A7 D F#7".split(), "majao2"),
    ("mamboA", "Bm Bm7 G D Em7 F#7 Bm A7".split(), "mambo"),
    ("mamboB", "G Gm6 F#m7 B7 Em7 A7 D A7".split(), "mambo2"),
    ("verse3", VERSE, "readback"),
    ("chorus3", "G Gm6 F#m7 B7 Em7 A7 D D".split(), "small"),
    ("signature", "Em7 Gm6 D Dadd9".split(), "sign"),
    ("fold", "D D".split(), "ring"),
]
if MODE == "loop":
    SECTIONS = SECTIONS[:3]

# ---------------------------------------------------------------- the hand (requinto), the cross-outs, the voice
REQ = {
    "opening": "1.0:D5:2 1.2:E5:2 1.4:G5:6 1.10:F#5:2 1.12:E5:2 1.14:D5:2 2.0:C#5:6 2.6:E5:2 2.8:A4:6 "
               "3.0:F#5:6 3.6:E5:2 3.8:C#5:2 3.10:D5:6 4.0:E5:6",
    "verse1": "1.10:A4:2 1.12:D5:2 1.14:F#5:2 2.0:A5:2 2.2:F#5:5 2.12:A4:2 2.14:C5:2 "
              "3.0:E5:2 3.2:G5:6 3.8:F#5:2 3.10:E5:2 3.12:D5:2 3.14:B4:2 4.0:C#5:6 4.6:E5:2 4.8:A4:8 "
              "5.2:E4:2 5.4:G4:2 5.6:B4:2 5.8:D5:2 5.10:E5:2 5.12:G5:4 6.0:F#5:2 6.2:E5:5 6.12:C#5:2 6.14:E5:2 "
              "7.0:F#5:6 7.6:E5:2 7.8:C#5:2 7.10:D5:6 8.0:C5:8",
    "chorus1": "2.12:D5:2 2.14:G5:2 3.0:A5:6 3.6:F#5:2 3.8:E5:2 3.10:C#5:2 3.12:E5:4 "
               "4.0:D#5:6 4.6:B4:2 4.8:C#5:2 4.10:D#5:2 4.12:F#5:4 5.0:G5:6 5.6:F#5:2 5.8:E5:4 5.12:D5:2 5.14:B4:2 "
               "6.0:C#5:6 6.6:E5:2 6.8:G5:4 6.12:F#5:2 6.14:E5:2 7.0:D5:2 7.2:E5:9",
    "verse2": "2.14:C5:2 3.0:E5:2 3.2:G5:6 3.8:F#5:2 3.10:E5:2 3.12:D5:2 3.14:B4:2 4.0:C#5:6 4.6:E5:2 4.8:A4:8 "
              "5.2:E4:2 5.4:G4:2 5.6:B4:2 5.8:D5:2 5.10:E5:2 5.12:G5:4 "
              "6.0:F#5:2 6.2:E5:2 6.4:C#5:2 6.6:A4:2 6.8:B4:2 6.10:C#5:2 6.12:E5:4 "
              "7.0:F#5:6 7.6:A5:2 7.8:F#5:2 7.10:D5:6 8.0:C5:5",
    "chorus2": "2.12:D5:2 2.14:G5:2 3.0:A5:6 3.6:F#5:2 3.8:E5:2 3.10:C#5:2 3.12:E5:4 "
               "4.0:D#5:6 4.6:B4:2 4.8:C#5:2 4.10:D#5:2 4.12:F#5:4 5.0:G5:6 5.6:F#5:2 5.8:E5:4 5.12:D5:2 5.14:B4:2 "
               "6.0:C#5:6 6.6:E5:2 6.8:G5:4 6.12:F#5:2 6.14:E5:2 7.0:D5:2 7.2:E5:2 7.4:F#5:10 "
               "8.8:A#4:2 8.10:C#5:2 8.12:E5:2 8.14:F#5:2",
    "mamboA": "1.0:F#5:2 1.2:D5:2 1.4:B4:2 1.6:D5:2 1.8:F#5:2 1.10:B5:4 1.14:A5:2 "
              "2.0:F#5:6 2.6:D5:2 2.8:E5:2 2.10:F#5:2 2.12:A5:4 "
              "3.0:G5:2 3.2:D5:2 3.4:B4:2 3.6:D5:2 3.8:G5:2 3.10:B5:4 3.14:A5:2 "
              "4.0:F#5:6 4.6:D5:2 4.8:A4:2 4.10:D5:2 4.12:F#5:4 "
              "5.0:E5:2 5.2:G5:2 5.4:B5:4 5.8:A5:2 5.10:G5:2 5.12:F#5:2 5.14:E5:2 "
              "6.0:C#5:2 6.2:E5:2 6.4:F#5:2 6.6:A#5:6 6.12:F#5:2 6.14:C#5:2 "
              "7.0:D5:2 7.2:F#5:2 7.4:B5:8 7.12:A5:2 7.14:F#5:2 8.0:E5:6 8.6:C#5:2 8.8:E5:2 8.10:G5:2 8.12:A5:4",
    "mamboB": "1.0:B5:T8 1.8:A5:4 1.12:G5:2 1.14:A5:2 2.0:Bb5:T10 2.10:G5:2 2.12:D5:2 2.14:G5:2 "
              "3.0:A5:6 3.6:F#5:2 3.8:E5:2 3.10:C#5:2 3.12:E5:4 4.0:D#5:6 4.6:B4:2 4.8:C#5:2 4.10:D#5:2 4.12:F#5:4 "
              "5.0:G5:6 5.6:F#5:2 5.8:E5:4 5.12:D5:2 5.14:B4:2 6.0:C#5:6 6.6:E5:2 6.8:G5:4 6.12:F#5:2 6.14:E5:2 "
              "7.0:E5:2 7.2:F#5:2 7.4:D5:12",
    "verse3": "1.10:A3:2 1.12:D4:2 1.14:F#4:2 2.0:A4:2 2.2:F#4:6 2.8:D#4:2 2.10:F#4:2 2.12:A4:2 2.14:C5:2 "
              "3.0:E4:2 3.2:G4:6 3.8:F#4:2 3.10:E4:2 3.12:D4:2 3.14:B3:2 4.0:C#4:6 4.6:E4:2 4.8:A3:8 "
              "5.2:E4:2 5.4:G4:2 5.6:B4:2 5.8:D5:2 5.10:E5:2 5.12:G5:4 6.0:F#5:2 6.2:E5:6 6.8:C#5:2 6.10:A4:2 "
              "6.12:C#5:2 6.14:E5:2 7.0:F#5:6 7.6:E5:2 7.8:C#5:2 7.10:D5:6 8.0:C5:8",
    "chorus3": "2.8:D4:2 2.10:E4:2 2.12:G4:4 3.0:A4:6 3.6:F#4:2 3.8:E4:2 3.10:C#4:2 3.12:E4:4 "
               "4.0:D#4:6 4.6:B3:2 4.8:C#4:2 4.10:D#4:2 4.12:F#4:4 5.0:G4:6 5.6:F#4:2 5.8:E4:4 5.12:D4:2 5.14:B3:2 "
               "6.0:C#4:6 6.6:E4:2 6.8:G4:4 6.12:F#4:2 6.14:E4:2 7.0:E4:2 7.2:F#4:2 7.4:D4:12",
    "signature": "1.0:G4:2 1.2:B4:2 1.4:D5:2 1.6:E5:10 3.10:F#5:2 3.12:E5:4 4.0:D5:16",
}
# second requinto voice (sixths and thirds under the lead), only where the sentence is said
REQ2 = {
    "chorus2": "3.0:C#5:6 3.6:A4:2 3.8:G#4:2 3.10:E4:2 3.12:G#4:4 4.0:F#4:6 4.6:D#4:2 4.8:E4:2 4.10:F#4:2 4.12:A4:4 "
               "5.0:B4:6 5.6:A4:2 5.8:G4:4 5.12:F#4:2 5.14:D4:2 6.0:E4:6 6.6:G4:2 6.8:B4:4 6.12:A4:2 6.14:G4:2",
    "mamboB": "1.0:D5:8 1.8:C5:4 1.12:B4:2 1.14:C5:2 2.0:D5:10 2.10:Bb4:2 2.12:G4:2 2.14:Bb4:2 "
              "3.0:C#5:6 3.6:A4:2 3.8:G#4:2 3.10:E4:2 3.12:G#4:4 4.0:F#4:6 4.6:D#4:2 4.8:E4:2 4.10:F#4:2 4.12:A4:4 "
              "5.0:B4:6 5.6:A4:2 5.8:G4:4 5.12:F#4:2 5.14:D4:2 6.0:E4:6 6.6:G4:2 6.8:B4:4 6.12:A4:2 6.14:G4:2 "
              "7.0:C#5:2 7.2:D5:2 7.4:F#4:12",
}
# the cross-outs: two dead strokes on the note the hand just reached
CROSS = {
    "opening": "4.8:E5:1 4.9.5:E5:1",
    "verse1": "2.8:F#5:1 2.9.5:F#5:1 6.8:E5:1 6.9.5:E5:1",
    "chorus1": "8.0:E5:1 8.1.5:E5:1",
    "verse2": "8.6:C5:1 8.7.5:C5:1",
}
VOZ = {  # notes, lyrics (one syllable per note)
    "opening": ("4.14:F#4:2", "tes"),
    "verse1": ("1.0:A4:6 1.6:F#4:5 8.12:G4:2 8.14:A4:2", "cri-bo lo que"),
    "chorus1": ("1.0:B4:8 1.8:A4:4 1.12:G4:2 1.14:A4:2 2.0:Bb4:9 8.14:F#4:2", "no su-pe de-cir tes"),
    "verse2": ("1.0:A4:4 1.4:F#4:4 1.14:A4:2 2.0:C5:8 2.8:A4:6 8.12:G4:2 8.14:A4:2", "cri-bo des-pa-cio lo que"),
    "chorus2": ("1.0:B4:8 1.8:A4:4 1.12:G4:2 1.14:A4:2 2.0:Bb4:9", "no su-pe de-cir"),
    "verse3": ("8.12:G4:2 8.14:A4:2", "lo que"),
    "chorus3": ("1.0:B4:8 1.8:A4:4 1.12:G4:2 1.14:A4:2 2.0:Bb4:16 3.0:A4:5", "no su-pe de-cir _"),
    "signature": ("2.0:Bb4:4 2.4:A4:4 2.8:G4:8 3.0:F#4:10", "siem-pre tu-ya"),
}


def trem(tok_pos, note, ln, v0=0.55, v1=0.95):
    """a long note as a requinto tremolo: 32nds, swelling"""
    n = int(ln * 2)
    return " ".join(f"{tok_pos + i * 0.5:g}:{note}:{0.5 if i < n - 1 else 2}:{v0 + (v1 - v0) * i / (n - 1):.2f}" for i in range(n))


def conv(spec):
    """'bar.step[.frac]:note:len[:vel]' -> engine tokens with section-relative 16th steps"""
    out = []
    for tok in spec.split():
        pos, rest = tok.split(":", 1)
        p = pos.split(".")
        step = (int(p[0]) - 1) * 16 + int(p[1]) + (float("0." + p[2]) if len(p) > 2 else 0)
        r = rest.split(":")
        if r[1].startswith("T"):
            out.append(trem(step, r[0], float(r[1][1:])))
        else:
            out.append(f"{step:g}:{rest}")
    return " ".join(out)


N2M = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(n):
    return N2M[n[0]] + (1 if "#" in n else -1 if "b" in n[1:] else 0) + 12 * int(n[-1])


def speak(tokens, lo=0.66, hi=0.97):
    """phrase dynamics for the hand: inside each phrase (notes with no gap over 2 steps) the velocity leans toward the
    highest note and falls away after it; a phrase's last note is let go a little"""
    toks = [t.split(":") for t in tokens.split()]
    phrases, cur = [], []
    for t in toks:
        if cur and float(t[0]) - (float(cur[-1][0]) + float(cur[-1][2])) > 2:
            phrases.append(cur); cur = []
        cur.append(t)
    phrases.append(cur)
    out = []
    for ph in phrases:
        pk = max(range(len(ph)), key=lambda i: midi(ph[i][1]))
        for i, t in enumerate(ph):
            if len(t) > 3:
                out.append(":".join(t)); continue
            d = abs(i - pk) / max(1, max(pk, len(ph) - 1 - pk))
            v = hi - (hi - lo) * d ** 0.8
            if i == len(ph) - 1 and i != pk:
                v -= 0.06
            out.append(":".join(t + [f"{v:.2f}"]))
    return " ".join(out)


# ---------------------------------------------------------------- grooves
def bass_line(chords, kind):
    out = []
    for i, c in enumerate(chords):
        r, f = ROOT[c]
        b = i * 16
        nxt = ROOT[chords[(i + 1) % len(chords)]][0]
        if kind == "bolero":      # half, quarter, quarter
            out += [f"{b}:{r}:8", f"{b+8}:{f}:4", f"{b+12}:{r}:4:0.7"]
        elif kind == "half":      # read-back: just the roots
            out += [f"{b}:{r}:12:0.7"]
        elif kind == "bachata":   # 1, (2)&, 3, 4: the pickup into 3
            out += [f"{b}:{r}:5", f"{b+6}:{r}:2:0.7", f"{b+8}:{f}:4", f"{b+12}:{r}:4:0.75"]
        elif kind == "mambo":
            out += [f"{b}:{r}:5", f"{b+6}:{r}:2:0.75", f"{b+8}:{f}:3", f"{b+11}:{f}:1:0.6", f"{b+12}:{r}:2:0.8",
                    f"{b+14}:{f}:2:0.7"]
    return " ".join(out)


# the room holds its breath at each cross-out: (from step, to step) inside the section, accompaniment silent
HOLES = {"opening": [(56, 64)], "verse1": [(24, 32), (88, 96)], "chorus1": [(114, 128)], "verse2": [(118, 128)], "verse3": [(120, 128)],
         "signature": [(32, 48), (48, 64)]}


def in_hole(name, step):
    return any(a <= step < b for a, b in HOLES.get(name, []))


def chordstr(chords, name=""):
    out = []
    for i, c in enumerate(chords):
        h = [(a, b) for a, b in HOLES.get(name, []) if i * 16 <= a < (i + 1) * 16]
        if h:
            a = h[0][0] - i * 16
            out += [f"{c}:{a}", f"-:{16 - a}"]
        else:
            out.append(f"{c}:16")
    return " ".join(out)


# bongó fills and turns: (section, bar) -> strings replacing that bar
FILLS = {
    ("chorus1", 1): dict(bonh="x...x...o.......", bonl="................"),
    ("chorus2", 1): dict(bonh="x...x...o.......", bonl="................"),
    ("chorus1", 4): dict(bonh="x...x...x.x.x.x.", bonl="............x.x."),
    ("chorus2", 4): dict(bonh="x...x...x.x.x.x.", bonl="............x.x."),
    ("chorus2", 8): dict(bonh="x...x.x.x.xxx.x.", bonk="..x......x......", bonl="..........x..xXR", mar="x.o.x.o.x.o....."),
    ("mamboA", 4): dict(bonh="X...X.x.x.xxX...", bonl="..............xx"),
    ("mamboA", 8): dict(bonh="X.x.X.xxx.xxX.x.", bonk="................", bonl=".............xXr"),
    ("mamboB", 2): dict(bonh="X...X...X..x..x.", bonl="............X..."),
    ("mamboB", 4): dict(bonh="X...X.x.x.xxX...", bonl="..............xx"),
    ("mamboB", 6): dict(bonh="X.x.X.x.X.xxx.xx", bonl="............X.x."),
    ("mamboB", 8): dict(bonh="X...x...o.......", bonk="..x...o.........", bonl="............o...", mar="x.....x.o......."),
}


def punch(name, steps, track=None):
    steps = list(steps)
    for (sec, bar), d in FILLS.items():
        if sec == name and track in d:
            steps[(bar - 1) * 16:bar * 16] = list(d[track])
    steps = "".join(steps)
    return "".join("." if in_hole(name, i) else ch for i, ch in enumerate(steps))


G = {  # groove -> parts
    "bolero":   dict(arp=0.62, bass="bolero", mar="x.o.x.o.x.o.x.o."),
    "majao":    dict(arp=0.5, chop="..x.x.x...x...x.", segb=1, bass="bachata", bonh="x...x...x.......", bonl="............x...",
                     mar="x...x...x...x..."),
    "derecho":  dict(arp=0.6, chop="......x.......x.", segb=0, bass="bolero", bonh="x...x...x.......", bonk="..x...x...x.x.x.", bonl="............x...",
                     mar="x.o.x.o.x.o.x.o."),
    "majao2":   dict(arp=0.5, chop="..x.x.x...x...x.", segb=1, bass="bachata", bonh="x...x...x.......", bonl="............x...",
                     mar="x.o.x.o.x.o.x.o."),
    "mambo":    dict(arp=0.6, strum=1, chop="..x.x.x...x...x.", segb=1, bass="mambo", bonh="X...X...X.......", bonk="..x...x...x.x.x.", bonl="............X...",
                     mar="x.o.o.x.x.o.o.x."),
    "mambo2":   dict(arp=0.65, strum=2, chop="..x.x.x...x...x.", segb=1, bass="mambo", bonh="X...X...X.......", bonk="..x...x...x.x.x.", bonl="............X...",
                     mar="x.o.o.x.x.o.o.x."),
    "readback": dict(arp=0.55, bass="half"),
    "small":    dict(arp=0.5),
    "sign":     dict(arp=0.45, strum=3),
    "ring":     dict(),
}


def pattern(name, chords, groove):
    g = G[groove]
    n = len(chords)
    p = {"bars": n}
    cs = chordstr(chords, name)
    if "arp" in g:
        p["segarp"] = {"chords": cs, "style": "arp", "rate": 2, "pattern": "up", "register": "D3", "voicing": "guitar",
                       "vel": g["arp"]}
    if "chop" in g:
        # under "su-pe de-" (beats 3-4 of a sung chorus's first bar) the chop steps aside
        cseg = cs.replace(":16", ":8 -:8", 1) if name in ("chorus1", "chorus2") else cs
        p["seg"] = {"chords": cseg, "style": "stabs", "rhythm": g["chop"], "stab_len": 1, "voicing": "guitar",
                    "register": "A3", "strum": "down", "strum_ms": 9, "vel": 0.7}
    if g.get("segb"):
        p["segb"] = {"chords": cs, "style": "stabs", "rhythm": "x.......x...x...", "stab_len": 3, "voicing": "root",
                     "register": "A2", "vel": 0.7}
    if g.get("strum") == 3:   # the signature: one slow chord under "-ya", one last chord
        p["segst"] = {"chords": "-:32 D:16 Dadd9:16", "style": "stabs", "rhythm": "x...............", "stab_len": 16,
                      "voicing": "guitar", "register": "D3", "strum": "down", "strum_ms": 38, "vel": 0.6}
    elif g.get("strum"):
        p["segst"] = {"chords": cs, "style": "stabs", "rhythm": "x......x........" if g["strum"] > 1 else "x...............", "stab_len": 8, "voicing": "guitar",
                      "register": "D3", "strum": "down", "strum_ms": 22, "vel": 0.7}
    if "bass" in g:
        toks = [t for t in bass_line(chords, g["bass"]).split() if not in_hole(name, int(t.split(":")[0]))]
        for a, b in HOLES.get(name, []):   # the last bass note before a hole rings through it: a floor under the hesitation
            if name == "signature":
                continue
            prev = [i for i, t in enumerate(toks) if int(t.split(":")[0]) < a]
            if prev:
                f = toks[prev[-1]].split(":")
                f[2] = str(b - int(f[0]) - 1)
                toks[prev[-1]] = ":".join(f[:3]) + ":0.7"
        p["bass"] = " ".join(toks)
    for k in ("bonh", "bonk", "bonl", "mar"):
        if k in g or any(sec == name and k in d for (sec, _), d in FILLS.items()):
            p[k] = punch(name, g.get(k, '.' * 16) * n, k)
    if name in REQ:
        p[REQ_TRACK.get(name, "req")] = speak(conv(REQ[name]))
    if name in REQ2:
        p["req2"] = speak(conv(REQ2[name]), 0.6, 0.88)
    if name in CROSS:
        p["reqx"] = conv(CROSS[name])
    if name in VOZ:
        p["voz"] = {"notes": conv(VOZ[name][0]), "lyrics": VOZ[name][1]}
    return p


GUITAR_BODY = [{"type": "hpf", "hz": 95}, {"type": "lowshelf", "hz": 330, "gain_db": 4.5}, {"type": "eq", "hz": 265, "gain_db": 8, "q": 1.0}, {"type": "eq", "hz": 410, "gain_db": -3.5, "q": 1.2}, {"type": "eq", "hz": 850, "gain_db": -2, "q": 0.8}, {"type": "eq", "hz": 3400, "gain_db": 2.5, "q": 0.7}]
REQ_INST = {"type": "acguitar", "bright": 0.78, "sustain": 1.7, "mic": 0.65, "pluck_pos": 0.12, "scrape": 0.25}
tracks = {
    "req": {"inst": dict(REQ_INST), "gain_db": 19, "pan": -0.24, "send_reverb": 0.14, "humanize_ms": 7, "vel_jitter": 0.08,
            "legato": 1.0, "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 265, "gain_db": 5.5, "q": 0.9}, {"type": "eq", "hz": 410, "gain_db": -2, "q": 1.2}, {"type": "eq", "hz": 1700, "gain_db": -2, "q": 0.8}, {"type": "eq", "hz": 3300, "gain_db": 4, "q": 0.7},
                                              {"type": "highshelf", "hz": 3800, "gain_db": 6.5}]},
    "req2": {"inst": dict(REQ_INST, seed=7, bright=0.5), "gain_db": 15, "pan": 0.1, "send_reverb": 0.14, "humanize_ms": 8,
             "vel_jitter": 0.08, "legato": 1.0, "fx": [{"type": "hpf", "hz": 180}, {"type": "highshelf", "hz": 5000, "gain_db": 3}]},
    "reqx": {"inst": dict(REQ_INST, chop=0.95, scrape=0.7, sustain=0.5), "gain_db": 26, "pan": -0.24, "send_reverb": 0.05,
             "humanize_ms": 3, "fx": [{"type": "hpf", "hz": 180}]},
    "segarp": {"inst": {"type": "acguitar", "bright": 0.5, "mic": 0.5, "scrape": 0.25}, "gain_db": 9.5, "pan": 0.34,
               "send_reverb": 0.1, "humanize_ms": 8, "vel_jitter": 0.1, "fx": list(GUITAR_BODY) + [{"type": "highshelf", "hz": 4000, "gain_db": 5.5}]},
    "seg": {"inst": {"type": "acguitar", "chop": 0.85, "scrape": 0.35, "seed": 5}, "gain_db": -2, "pan": 0.5,
            "send_reverb": 0.08, "humanize_ms": 7, "vel_jitter": 0.1,
            "fx": [{"type": "hpf", "hz": 130}, {"type": "eq", "hz": 280, "gain_db": 5, "q": 0.8}, {"type": "eq", "hz": 2500, "gain_db": -2.5, "q": 0.7}]},
    "segb": {"inst": {"type": "acguitar", "chop": 0.3, "seed": 5}, "gain_db": -1, "pan": 0.3, "humanize_ms": 6,
             "fx": [{"type": "hpf", "hz": 90}, {"type": "eq", "hz": 180, "gain_db": 4, "q": 0.8}, {"type": "eq", "hz": 290, "gain_db": 4, "q": 0.9}]},
    "segst": {"inst": {"type": "acguitar", "bright": 0.4, "seed": 9}, "gain_db": -1, "pan": -0.45, "send_reverb": 0.1,
              "humanize_ms": 6, "fx": list(GUITAR_BODY)},
    "bass": {"inst": {"type": "ebass", "pick": 0.2, "tone": 2200, "drive": 0.3}, "gain_db": -6, "humanize_ms": 5,
             "legato": 0.9, "fx": [{"type": "eq", "hz": 115, "gain_db": 4, "q": 0.8}, {"type": "eq", "hz": 165, "gain_db": 5, "q": 0.9}, {"type": "eq", "hz": 280, "gain_db": 5.5, "q": 0.9}]},
    "bonh": {"inst": {"type": "darbuka", "stroke": "tek", "tune": 0.62}, "gain_db": -2, "pan": -0.22, "humanize_ms": 8,
             "vel_jitter": 0.12, "send_reverb": 0.12, "fx": [{"type": "lpf", "hz": 4500}]},
    "bonk": {"inst": {"type": "darbuka", "stroke": "ka", "tune": 0.62}, "gain_db": -6, "pan": -0.22, "humanize_ms": 9,
             "vel_jitter": 0.15, "send_reverb": 0.12, "fx": [{"type": "lpf", "hz": 4500}]},
    "bonl": {"inst": {"type": "darbuka", "stroke": "tek", "tune": 0.44}, "gain_db": -1, "pan": -0.16, "humanize_ms": 8,
             "vel_jitter": 0.1, "send_reverb": 0.12, "fx": [{"type": "lpf", "hz": 4000}]},
    "mar": {"inst": {"type": "shaker", "decay": 0.022}, "gain_db": 8, "pan": 0.35, "humanize_ms": 9, "vel_jitter": 0.18,
            "fx": [{"type": "lpf", "hz": 7000}]},
    # the voice: docs/LATIN_POP.md "Mixing the voice" starting chain (soft voice over a bolero band: 4.5 kHz bell at +3)
    "voz": {"inst": {"type": "singer", "source": "svs", "voice": "hanami-es-soft", "inhale": 0.08, "svs_fade_in_ms": 30,
                     "svs_fade_out_ms": 120},
            "gain_db": 4, "send_reverb": 0.14, "reverb_predelay_ms": 55, "send_delay": 0.0, "vel_jitter": 0.0,
            "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 250, "gain_db": -2, "q": 0.8},
                   {"type": "eq", "hz": 800, "gain_db": -2, "q": 0.9}, {"type": "eq", "hz": 4500, "gain_db": 3, "q": 0.8},
                   {"type": "eq", "hz": 7500, "gain_db": -4, "q": 1.0}, {"type": "lpf", "hz": 11000},
                   {"type": "comp", "threshold_db": -22, "ratio": 3},
                   {"type": "gain", "db": 6}]},
}

# per-section level offsets (dB) per track: the arc (the middle is the loudest, the end the smallest)
AUTO = {
    "opening": {"req": -1, "voz": -1.5},
    "verse1": {"voz": -1.5}, "verse2": {"voz": -1.5}, "chorus1": {"voz": 1}, "chorus2": {"voz": 1.5},
    "mamboA": {"req": 3, "mar": 2, "seg": 2, "segb": 2, "segst": 4, "bass": 1.5, "bonh": 2, "bonk": 2, "bonl": 2, "segarp": 1},
    "mamboB": {"req": 4.5, "req2": 3, "seg": 3, "segb": 3, "segst": 6, "bass": 2.5, "bonh": 3, "bonk": 3, "bonl": 3,
               "segarp": 2, "mar": 3},
    "verse3": {"req": -5, "segarp": -2, "bass": 0},
    "chorus3": {"req": -7, "segarp": -5, "voz": -4.5},
    "signature": {"req": -4, "segarp": -3, "voz": -6, "segst": 2},
}
# the hand's time feel: late while it hesitates (verses), with the band in the choruses, leaning in in the mambo
REQ_TRACK = {"chorus1": "reqc", "chorus2": "reqc", "chorus3": "reqc", "signature": "reqc", "mamboA": "reqm", "mamboB": "reqm"}
tracks["req"]["push_ms"] = 22
tracks["reqx"]["push_ms"] = 10
tracks["reqc"] = dict(tracks["req"], push_ms=8)
tracks["reqm"] = dict(tracks["req"], push_ms=-6, humanize_ms=5)
tracks = {k: tracks[k] for k in ["req", "reqc", "reqm"] + [k for k in tracks if k not in ("req", "reqc", "reqm")]}
patterns, arrangement = {}, []
for name, chords, groove in SECTIONS:
    patterns[name] = pattern(name, chords, groove)
    sec = {"name": name, "bars": len(chords), "play": [name]}
    if name in ("signature", "fold"):
        sec["bpm"] = [84, 74] if name == "signature" else 300
    if name in AUTO:
        sec["auto"] = {(REQ_TRACK.get(name, "req") if t == "req" else t): {"gain_db": [v, v]} for t, v in AUTO[name].items()}
    arrangement.append(sec)

project = {
    "title": "Love letter (session 014)", "bpm": BPM, "swing": 0.5, "seed": 14,
    "tracks": tracks, "patterns": patterns, "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.5, "damping": 0.6, "return_db": -7, "lpf": 6000}},
    "master": {"lufs": -11},
}
exec(open("tweaks.py").read()) if __import__("os").path.exists("tweaks.py") else None
json.dump(project, open("project.json", "w"), indent=1, ensure_ascii=False)
bars = sum(len(c) for _, c, _ in SECTIONS)
print(f"{bars} bars, {bars * 240 / BPM:.1f} s")
