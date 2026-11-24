#!/usr/bin/env python3
"""Builds project.json for session 010 (joc țigănesc). python3 build.py [loop|full]"""
import json, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "loop"


def sh(notes, off):
    """shift a note string by off 16th steps"""
    out = []
    for tok in notes.split():
        st, rest = tok.split(":", 1)
        out.append(f"{float(st) + off:g}:{rest}")
    return " ".join(out)


# ---- the tune (one pattern bar = two bars of 2/4; a strain = 4 pattern bars = 64 steps) ----
# HIM: strain A, low strings, the climb G A Bb C# D
A = ("0:G4:1/dn 1:A4:1/s 2:Bb4:2 4:C#5:2/g-1 6:D5:2/acc "
     "8:Eb5:1 9:D5:1/s 10:C#5:2 12:D5:2/m 14:D4:2/sp "
     "16:F#4:2/g-1 18:A4:1 19:C5:1/s 20:Eb5:2/acc 22:D5:1 23:C5:1/s "
     "24:Bb4:2/g-1 26:G4:3 29:D4:1/up 30:G4:1/s 31:A4:1/s "
     "32:Bb4:1/dn 33:C5:1/s 34:Eb5:2/g-1 36:D5:1 37:C5:1/s 38:Bb4:2 "
     "40:A4:1 41:Bb4:1/s 42:A4:1/s 43:G4:1/s 44:G4:2/d=D4 46:D4:2 "
     "48:C5:2/m 50:Bb4:1 51:A4:1/s 52:Eb4:1 53:F#4:1/s 54:A4:2 "
     "56:G4:4/g-1 61:D5:1/up 62:Eb5:1/s 63:F#5:1/s")
A_CH = "Gm:8 Gm:8 D7:8 Gm:8 Cm:8 Gm:8 D7:8 Gm:8"
A_BASS = ("0:G2:2 4:D2:2 8:G2:2 12:Bb2:2 16:D2:2 20:A2:2 24:G2:2 28:D2:2 "
          "32:C3:2 36:G2:2 40:G2:2 44:D2:2 48:D2:2 52:A2:2 56:G2:2 60:F#2:2")

# HER: strain B, high strings, the fall A G F# Eb D
B = ("0:A5:1/dn 1:G5:1/s 2:F#5:2 4:Eb5:2/g-1 6:D5:2/acc "
     "8:G5:2/sl-3 10:Bb5:1 11:A5:1/s 12:G5:1 13:F#5:1/s 14:G5:2 "
     "16:G5:1 17:Eb5:1/s 18:C5:1/s 19:Eb5:1/s 20:G5:2/acc 22:F5:1 23:Eb5:1/s "
     "24:D5:4/fall-3 29:D5:1/up 30:Eb5:1/s 31:F#5:1/s "
     "32:G5:2/g-1 34:A5:1 35:Bb5:1/s 36:A5:2/m 38:G5:2 "
     "40:Bb5:1 41:G5:1/s 42:E5:1/s 43:C#5:1/s 44:Bb4:1 45:C#5:1/s 46:E5:1/s 47:G5:1/s "
     "48:F#5:3/tr+1 51:Eb5:1/s 52:D5:2 54:C5:1 55:A4:1/s "
     "56:G4:4/g-1 61:D4:1/up 62:Eb4:1/s 63:F#4:1/s")
B_CH = "D7:8 Gm:8 Cm:8 Gm:8 Gm:8 C#dim7:8 D7:8 Gm:8"
B_BASS = ("0:D2:2 4:A2:2 8:G2:2 12:D2:2 16:C3:2 20:G2:2 24:G2:2 28:D2:2 "
          "32:G2:2 36:D2:2 40:C#3:2 44:E2:2 48:D2:2 52:A2:2 56:G2:2 60:F#2:2")


def bow(notes, shape=(0.95, 0.68, 0.78, 0.7, 0.88, 0.68, 0.78, 0.72)):
    """velocity by position in the 2/4 bar: the downbeat leans, beat 2 a little less, 16th offbeats lighter;
    accents (acc) and long notes keep weight"""
    out = []
    for tok in notes.split():
        st, nt, rest = tok.split(":", 2)
        if rest.count(":"):
            out.append(tok); continue
        p = float(st) % 8
        v = shape[int(p) % 8] if abs(p - round(p)) < 1e-6 else 0.66
        ln = float(rest.split("/")[0].rstrip("~!."))
        if "acc" in rest: v = max(v, 0.97)
        if ln >= 3: v = max(v, 0.86)
        out.append(f"{st}:{nt}:{rest}:{v:.2f}")
    return " ".join(out)


def gtr(chords, rhythm="..x...x...x...x.", vel=0.75):
    return {"chords": chords, "style": "stabs", "rhythm": rhythm, "stab_len": 1, "register": "G3",
            "voicing": "guitar", "strum": "down", "strum_ms": 9, "vel": vel}


TRACKS = {
    "vln": {"inst": {"type": "violin", "cold": 0.45, "vibrato": 0.3, "vib_rate": 5.2, "bow_speed": 1.0, "dark": 0.15, "bow_noise": 0.5,
                     "intonation": 0.7},
            "gain_db": 1, "humanize_ms": 7, "push_ms": -4, "vel_jitter": 0.04, "legato": 0.97, "send_reverb": 0.1, "pan": 0.05,
            "fx": [{"type": "hpf", "hz": 180}, {"type": "eq", "hz": 2800, "gain_db": -2.5, "q": 0.8},
                   {"type": "highshelf", "hz": 9000, "gain_db": 5}]},
    "gtr": {"inst": {"type": "acguitar", "chop": 0.8, "scrape": 0.35}, "humanize_ms": 4, "vel_jitter": 0.08,
            "gain_db": 9, "pan": -0.35, "send_reverb": 0.05,
            "fx": [{"type": "hpf", "hz": 110}, {"type": "eq", "hz": 175, "gain_db": 5, "q": 0.9}, {"type": "eq", "hz": 320, "gain_db": 2, "q": 1.0},
                   {"type": "highshelf", "hz": 3000, "gain_db": -2},
                   {"type": "eq", "hz": 150, "gain_db": 4, "q": 1.0}, {"type": "highshelf", "hz": 9000, "gain_db": 3}]},
    "bass": {"inst": {"type": "ebass", "pick": 0.2, "drive": 0.25, "tone": 2500},
             "humanize_ms": 3, "legato": 0.6, "gain_db": 5, "fx": [{"type": "eq", "hz": 160, "gain_db": 4, "q": 0.9}]},
    "toba": {"inst": {"type": "toba", "stroke": "boom", "tune": 54, "decay": 0.14}, "gain_db": -10, "humanize_ms": 4,
             "fx": [{"type": "eq", "hz": 54, "gain_db": -5, "q": 1.4}, {"type": "eq", "hz": 110, "gain_db": 3, "q": 1},
                    {"type": "room", "size": 0.35, "mix": 0.12}]},
    "cinel": {"inst": {"type": "toba", "stroke": "cinel", "cinel_decay": 0.16, "bright": 0.6},
              "gain_db": -11, "humanize_ms": 4, "pan": 0.25,
              "fx": [{"type": "hpf", "hz": 400}, {"type": "lpf", "hz": 14000}]},
    "rim": {"inst": {"type": "toba", "stroke": "rim"}, "gain_db": 2, "humanize_ms": 5, "pan": -0.15},
    "both": {"inst": {"type": "toba", "stroke": "both", "tune": 54, "decay": 0.16, "cinel_decay": 0.25, "bright": 0.4},
             "gain_db": -10, "humanize_ms": 3, "fx": [{"type": "eq", "hz": 54, "gain_db": -5, "q": 1.4},
                                                    {"type": "lpf", "hz": 10000}]},
    "snare": {"inst": {"type": "kitsnare", "tune": 230, "wires": 0.45, "decay": 0.11}, "gain_db": -11,
              "humanize_ms": 5, "pan": -0.1,
              "fx": [{"type": "room", "size": 0.3, "mix": 0.15}, {"type": "highshelf", "hz": 6000, "gain_db": 0}]},
    "snap": {"inst": {"type": "snap"}, "gain_db": -4, "humanize_ms": 7, "pan": 0.45},
    "clap": {"inst": {"type": "handclap", "clappers": 6, "spread_ms": 10, "room": 0.3, "bright": 0.5}, "gain_db": -8,
             "humanize_ms": 6, "width": 0.5, "send_reverb": 0.12, "fx": [{"type": "hpf", "hz": 250}]},
}


# ---------------- variants ----------------
def toks(n):
    return n.split()


def parse(tok):
    st, nt, rest = tok.split(":", 2)
    ln, art = (rest.split("/", 1) + [""])[:2]
    return float(st), nt, ln, art


def build(lst):
    out = []
    for st, nt, ln, art in lst:
        out.append(f"{st:g}:{nt}:{ln}" + (f"/{art}" if art else ""))
    return " ".join(out)


def edit(notes, drop=(), add=""):
    """drop notes whose step is in drop (or in a (lo, hi) range), then add new tokens"""
    keep = []
    for t in toks(notes):
        st = parse(t)[0]
        gone = any((isinstance(d, tuple) and d[0] <= st < d[1]) or (not isinstance(d, tuple) and abs(st - d) < 1e-6)
                   for d in drop)
        if not gone:
            keep.append(t)
    return " ".join(keep + toks(add))


def pick(notes, kind):
    """replace the three-16th pickup at steps 61-63: 'lo' into a low strain, 'hi' into a high one, 'none'"""
    n = edit(notes, drop=[(60.5, 64)])
    return n + {"lo": " 61:D4:1/up 62:Eb4:1/s 63:F#4:1/s", "hi": " 61:D5:1/up 62:Eb5:1/s 63:F#5:1/s", "none": ""}[kind]


def addart(notes, test, art):
    out = []
    for t in toks(notes):
        st, nt, ln, a = parse(t)
        if test(st, nt, float(ln.rstrip("~!.")), a):
            a = (a + "," + art) if a else art
        out.append((st, nt, ln, a))
    return build(out)


def nv16(notes):
    """no vibrato on the 16ths (needed at slow tempos, where a 16th is long enough to wobble)"""
    return addart(notes, lambda st, nt, ln, a: ln <= 1 and "nv" not in a, "nv")


def vibl(notes, minlen=3):
    return addart(notes, lambda st, nt, ln, a: ln >= minlen and "ftr" not in a and "tr" not in a and "fall" not in a, "vib")


MIDI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(n):
    m = MIDI[n[0]] + (1 if "#" in n else -1 if "b" in n[1:] else 0)
    return m + 12 * (int(n[-1]) + 1)


def dbl(notes):
    """double stops against the open strings on the downbeats of each 2/4 bar (weight for a later round)"""
    out = []
    for t in toks(notes):
        st, nt, ln, a = parse(t)
        if abs(st % 4) < 1e-6 and "d=" not in a and "s" not in a.split(","):
            m = midi(nt)
            drone = "G3" if m < midi("A4") else "D4" if m <= midi("E5") else "A4"
            if m >= midi("Bb4") and (m - midi(drone)) % 12 in (0, 3, 4, 5, 7, 8, 9):
                a = (a + "," if a else "") + f"d={drone}"
        out.append((st, nt, ln, a))
    return build(out)


def octup(notes):
    out = []
    for t in toks(notes):
        st, nt, ln, a = parse(t)
        nt2 = nt[:-1] + str(int(nt[-1]) + 1)
        out.append((st, nt2, ln, a.replace("d=D4", "").replace(",,", ",").strip(",")))
    return build(out)


# ---------------- strains for later rounds ----------------
# C: call and answer, he climbs / she falls, bar by bar, then by half bars (round 3)
C = ("0:G4:1/dn 1:A4:1/s 2:Bb4:2 4:C#5:2/g-1 6:D5:2/acc "
     "8:A5:1/dn 9:G5:1/s 10:F#5:2 12:Eb5:2/g-1 14:D5:2/acc "
     "16:C5:1/dn 17:D5:1/s 18:Eb5:2 20:F#5:2/g-1 22:G5:2/acc "
     "24:A5:1/dn 25:G5:1/s 26:Eb5:2 28:C#5:2/g-1 30:D5:2/acc "
     "32:G4:1 33:Bb4:1/s 34:C5:1/s 35:Eb5:1/s 36:G5:1 37:Eb5:1/s 38:C5:1/s 39:Bb4:1/s "
     "40:C#5:1 41:E5:1/s 42:G5:1/s 43:Bb5:1/s 44:A5:1 45:G5:1/s 46:E5:1/s 47:C#5:1/s "
     "48:F#5:2/d=A4,acc 50:Eb5:1 51:D5:1/s 52:C5:1 53:A4:1/s 54:F#4:2/g-1 "
     "56:G4:4/d=D4 61:D4:1/up 62:Eb4:1/s 63:F#4:1/s")
C_CH = "Gm:8 D7:8 Cm:8 Gm:8 Cm:8 C#dim7:8 D7:8 Gm:8"
C_BASS = ("0:G2:2 4:D2:2 8:D2:2 12:A2:2 16:C3:2 20:G2:2 24:G2:2 28:D2:2 "
          "32:C3:2 36:Eb2:2 40:C#3:2 44:E2:2 48:D2:2 52:A2:2 56:G2:2 60:F#2:2")

# U: the union strain: the climb and the fall at once, double stops in contrary motion
# (octave G4/G5, sixth A4/F#5, fourth Bb4/Eb5, the two leading tones C#5/Eb5, then the unison D5)
UC = "{0}:G5:1/d=G4 {1}:F#5:1/s,d=A4 {2}:Eb5:2/d=Bb4 {4}:Eb5:2/d=C#5 {6}:D5:2/d=D5,acc"


def uc(off):
    return UC.format(*[off + i for i in range(7)])


U = (uc(0) + " 8:D5:1 9:Eb5:1/s 10:F#5:1/s 11:G5:1/s 12:A5:2/acc 14:F#5:2/g-1 " + uc(16) +
     " 24:D5:4/d=A4,vib 29:D4:1/up 30:G4:1/s 31:A4:1/s "
     "32:Bb4:1/dn 33:C5:1/s 34:Eb5:2/g-1 36:G5:2/acc 38:Eb5:2 "
     "40:Bb5:1 41:G5:1/s 42:E5:1/s 43:C#5:1/s 44:Bb4:2/d=G3 46:C#5:2/g-1 "
     "48:A5:2/d=D5 50:F#5:2/d=C5 52:Eb5:2/d=C#5 54:D5:2/d=D5,acc "
     "56:G5:4/d=G4,acc 61:D5:1/up 62:Eb5:1/s 63:F#5:1/s")
U_CH = "Gm:8 D7:8 Gm:8 D7:8 Cm:8 C#dim7:8 D7:8 Gm:8"
U_BASS = ("0:G2:2 4:D2:2 8:D2:2 12:F#2:2 16:G2:2 20:D2:2 24:D2:2 28:A2:2 "
          "32:C3:2 36:G2:2 40:C#3:2 44:E2:2 48:D2:2 52:A2:2 56:G2:2 60:D2:2")

# PEAK: the union twice, then the two leading tones pressed together and the held unison D5 over D7
PKA = (uc(0) + " 8:D5:1 9:Eb5:1/s 10:F#5:1/s 11:G5:1/s 12:A5:2/acc 14:F#5:2/g-1 " + uc(16) +
       " 24:G5:1 25:A5:1/s 26:Bb5:2/acc 28:A5:1 29:G5:1/s 30:F#5:1/s 31:G5:1/s")
PKA_CH = "Gm:8 D7:8 Gm:8 Cm:8"
PKA_BASS = "0:G2:2 4:D2:2 8:D2:2 12:F#2:2 16:G2:2 20:D2:2 24:C3:2 28:G2:2"
# the two leading tones pressed together (bowed tremolo), then the unison D5 held over D7 by the whole room
PKB = "0:Eb5:8/d=C#5,trem,acc 8:D5:16/d=D5,ftr+1,acc 24:G5:8/d=G4,acc"
PKB_CH = "C#dim7:8 D7:8 D7:8 Gm:2 -:6"
PKB_BASS = "0:C#3:2 4:E2:2 8:D2:2 12:A2:2 16:D2:2 20:C3:2 24:G2:3"

# the stop-time ending: band hit on 1, the primaș runs alone, the band answers, the last hit together
END = ("2:D5:1/dn 3:Eb5:1/s 4:D5:1/s 5:C#5:1/s 6:D5:1/s 7:Bb4:1/s "
       "8:A4:1 9:Bb4:1/s 10:C#5:1/s 11:D5:1/s 12:Eb5:1 13:F#5:1/s 14:G5:1/s 15:A5:1/s "
       "16:Bb5:2/acc 18:A5:1 19:G5:1/s 20:F#5:2/g-1 22:Eb5:1 23:C#5:1/s "
       "24:D5:2/d=D5,acc 28:G5:3/d=G4,acc")
END_CH = "-:16 D7:2 -:2 D7:2 -:2 D7:2 -:2 Gm:2 -:2"
END_BASS = "16:D2:2 20:D2:2 24:D2:2 28:G2:3"

# primaș preludes and interludes
PRE = ("0:D5:6/sl-2,vib 6:Eb5:1/s 7:D5:1/s 8:C#5:2/g-1 10:Bb4:1 11:A4:1/s 12:G4:4/vib "
       "16:G5:3/sl-3 19:F#5:1/s 20:Eb5:2/g-1 22:D5:1 23:C#5:1/s 24:D5:5/fall-3 29:D4:1/up 30:Eb4:1/s 31:F#4:1/s")
RIS = ("0:D5:8/ftr+1 8:Eb5:1 9:D5:1/s 10:C#5:1/s 11:D5:1/s 12:F#5:2/g-1 14:G5:1 15:A5:1/s "
       "16:Bb5:4/acc 20:A5:1 21:G5:1/s 22:F#5:1/s 23:Eb5:1/s 24:D5:2/acc 26:A4:2 29:D4:1/up 30:Eb4:1/s 31:F#4:1/s")
INT1 = ("0:D5:4/ftr+1 4:Eb5:1 5:D5:1/s 6:C#5:1/s 7:D5:1/s 8:F#5:2/g-1 10:G5:1 11:A5:1/s 12:Bb5:2/acc 14:A5:1 15:G5:1/s "
        "16:F#5:4/tr+1 20:Eb5:1 21:D5:1/s 22:C5:1/s 23:Bb4:1/s 24:A4:2/turn 26:C5:2 29:D4:1/up 30:Eb4:1/s 31:F#4:1/s")
INT2 = ("0:A5:4/sl-3,acc 4:G5:1 5:F#5:1/s 6:G5:1/s 7:A5:1/s 8:Bb5:2/g-1 10:A5:1 11:G5:1/s 12:F#5:1 13:Eb5:1/s "
        "14:D5:1/s 15:C#5:1/s 16:D5:4/d=A4,ftr+1 20:D4:1 21:A4:1/s 22:D5:1/s 23:F#5:1/s 24:A5:2/acc 26:F#5:2/fall-3 "
        "29:D4:1/up 30:Eb4:1/s 31:F#4:1/s")

INT3 = ("0:D5:2/d=A4,acc 2:D5:1 3:Eb5:1/s 4:F#5:1/s 5:G5:1/s 6:A5:2/acc 8:Bb5:4/ftr+1 12:A5:1 13:G5:1/s "
        "14:F#5:1/s 15:Eb5:1/s 16:F#5:2/d=A4,acc 18:Eb5:1 19:D5:1/s 20:C#5:1 21:D5:1/s 22:Eb5:1/s 23:C#5:1/s "
        "24:D5:4/d=A4,ftr+1 29:D5:1/up 30:Eb5:1/s 31:F#5:1/s")

A_LO, A_HI = pick(A, "lo"), pick(A, "hi")
B_HI, B_LO = pick(B, "hi"), pick(B, "lo")
# second-time variants: more ornaments where a phrase lands, a different landing
A2_HI = edit(A_HI, drop=[24, 26, 56], add="24:Bb4:2/m 26:G4:3/fall-2 56:G4:4/tr+1")
B2_LO = edit(B_LO, drop=[8, 24, (40, 48)], add="8:G5:2/sl-4,acc 24:D5:4/ftr+1 40:C#5:2/g-1 42:E5:1 43:D5:1/s 44:C#5:2/m 46:Bb4:2")


NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def walk(bass):
    """the bassist's chromatic approach: a 16th a semitone under the next downbeat's root"""
    out = toks(bass)
    for t in toks(bass):
        st, nt, ln, a = parse(t)
        if st % 8 == 0 and st > 0:
            m = midi(nt) - 1
            out.append(f"{st - 1:g}:{NAMES[m % 12]}{m // 12 - 1}:1")
    return " ".join(sorted(out, key=lambda x: float(x.split(":")[0])))


def V(notes, bars=4):
    return {"bars": bars, "vln": bow(notes)}


def BAND(ch, bass, rhythm="..x...x...x...x.", vel=0.75, bars=4):
    return {"bars": bars, "gtr": gtr(ch, rhythm, vel), "bass": bass}


PUSH = "..x..xx...x..xx."
PAT = {
    # violin
    "v_pre": V(nv16(PRE), 2),
    "v_rA": V(vibl(nv16(A_LO), 2)), "v_rB": V(vibl(nv16(B_LO), 2)),
    "v_ris": V(nv16(RIS), 2),
    "v_1A": V(A_LO), "v_1A2": V(A2_HI), "v_1B": V(B_HI), "v_1B2": V(B2_LO),
    "v_i1": V(INT1, 2),
    "v_2A": V(dbl(A_LO)), "v_2A2": V(dbl(A2_HI)), "v_2B": V(dbl(B_HI)), "v_2B2": V(B2_LO),
    "v_i2": V(INT2, 2),
    "v_3C": V(C), "v_3C2": V(pick(dbl(C), "hi")), "v_3A": V(pick(octup(A_HI), "hi")), "v_3B": V(pick(dbl(B), "hi")),
    "v_i3": V(INT3, 2),
    "v_4U": V(pick(U, "hi")), "v_4U2": V(pick(edit(U, drop=[24, 56], add="24:D5:4/d=A4,ftr+1 56:G5:4/d=G4,acc"), "hi")),
    "v_pkA": V(PKA, 2), "v_pkB": V(PKB, 2), "v_end": V(END, 2),
    # band
    "b_pre": {"bars": 2, "gtr": {"chords": "D7:16 D7:16", "style": "strum", "strum_dir": "down", "strum_ms": 40,
                                 "register": "G3", "voicing": "guitar", "vel": 0.5},
              "bass": "0:D2:12 16:D2:12"},
    "b_rA": BAND(A_CH, A_BASS, vel=0.6), "b_rB": BAND(B_CH, B_BASS, vel=0.6),
    "b_ris": BAND("D7:8 D7:8 D7:8 D7:8", "0:D2:2 4:A2:2 8:D2:2 12:A2:2 16:D2:2 20:A2:2 24:D2:2 28:C3:2", vel=0.68, bars=2),
    "b_A": BAND(A_CH, A_BASS), "b_B": BAND(B_CH, B_BASS), "b_Bw": BAND(B_CH, walk(B_BASS)),
    "b_Apw": BAND(A_CH, walk(A_BASS), PUSH, 0.8), "b_Cw": BAND(C_CH, walk(C_BASS), PUSH, 0.8),
    "b_Ap": BAND(A_CH, A_BASS, PUSH, 0.8), "b_Bp": BAND(B_CH, B_BASS, PUSH, 0.8),
    "b_int": BAND("D7:8 D7:8 D7:8 D7:8", "0:D2:2 4:A2:2 8:D2:2 12:A2:2 16:D2:2 20:A2:2 24:D2:2 28:C3:2", bars=2),
    "b_C": BAND(C_CH, C_BASS, PUSH, 0.8),
    "b_U": BAND(U_CH, U_BASS, vel=0.82), "b_Uw": BAND(U_CH, walk(U_BASS), PUSH, 0.86), "b_Bpk": BAND(B_CH, B_BASS, PUSH, 0.85),
    "b_pkA": BAND(PKA_CH, PKA_BASS, PUSH, 0.88, bars=2), "b_pkB": BAND(PKB_CH, PKB_BASS, PUSH, 0.9, bars=2),
    "b_end": {"bars": 2, "gtr": {"chords": END_CH, "style": "strum", "strum_dir": "down", "strum_ms": 12,
                                 "register": "G3", "voicing": "guitar", "vel": 0.9},
              "bass": END_BASS},
    # percussion: the room joins in steps
    "k_rar": {"bars": 1, "toba": "x.......x.......", "rim": "..o...x...o...x."},
    "k_ris": {"bars": 2, "toba": "x.......x.......x...x...x.x.x.x.", "snare": "................o.o.o.o.o.o.o.rr"},
    "k_1": {"bars": 1, "toba": "x...g...x...g...", "snare": "..o...o...o...o."},
    "k_1b": {"bars": 1, "toba": "x...g...x...g...", "snare": "..x...x.g.x.o.x."},
    "k_2": {"bars": 1, "toba": "x...g...x...g...", "snare": "..x...x.g.x.o.x.", "cinel": "x.......x......."},
    "k_int": {"bars": 2, "toba": "x...g...x...g...x...g...x.x.x.x.", "snare": "..o...o...o...o.o.o.o.o.o.o.o.rr"},
    "snaps": {"bars": 1, "snap": "..x...x...x...x."},
    "claps": {"bars": 1, "clap": "......x.......x."},
    "k_int3": {"bars": 2, "toba": "x.......x.......x.......x.x.x.x.", "snare": "............................o.rr"},
    "claps2": {"bars": 1, "clap": "..x...x...x...x."},
    "k_4h": {"bars": 1, "toba": "x...g...x...g..."},
    "k_4": {"bars": 1, "toba": "....g...x...g...", "both": "x...............", "snare": "..x..ox.g.x..ox.",
            "cinel": "........x......."},
    "k_pk": {"bars": 1, "toba": "....g.......g...", "both": "x.......x.......", "snare": "..x..ox.g.x..ox.",
             "cinel": "..o...x...o...x."},
    "k_pkB": {"bars": 2, "toba": "....g.......g.......g...........", "both": "x.......X.......x.......X.......",
              "snare": "..x..ox.g.x..ox...x..ox.........", "cinel": "..o...x...x...x...o...x.........",
              "clap": "..x..xx...x..xx...x..xx.X.......", "snap": "..x...x...x...x...x...x........."},
    "k_end": {"bars": 2, "both": "................x...x...x...X...",
              "clap": "............................X..."},
    "fill_snare": {"bars": 1, "snare": "..x...x.o.o.o.rr", "toba": "x...g...x.x.x.x."},
}

if MODE == "loop":
    ARR = [{"name": "rA", "bars": 4, "bpm": 112, "play": ["v_1A", "b_A", "k_2"]},
           {"name": "rB", "bars": 4, "bpm": 112, "play": ["v_1B", "b_B", "k_2", "snaps", "claps"]}]
else:
    F = {"pattern": "fill_snare"}
    ARR = [
        {"name": "prelude", "bars": 2, "bpm": 50, "play": ["v_pre", "b_pre"]},
        {"name": "rarA", "bars": 4, "bpm": 50, "play": ["v_rA", "b_rA", "k_rar"]},
        {"name": "rarB", "bars": 4, "bpm": [50, 72], "play": ["v_rB", "b_rB", "k_rar"]},
        {"name": "ridicare", "bars": 2, "bpm": [72, 100], "play": ["v_ris", "b_ris", "k_ris"]},
        {"name": "r1A", "bars": 4, "bpm": 100, "play": ["v_1A", "b_A", "k_1"]},
        {"name": "r1A2", "bars": 4, "bpm": 100, "play": ["v_1A2", "b_A", "k_1b"]},
        {"name": "r1B", "bars": 4, "bpm": 100, "play": ["v_1B", "b_B", "k_2"]},
        {"name": "r1B2", "bars": 4, "bpm": 100, "play": ["v_1B2", "b_Bw", "k_2", "snaps"]},
        {"name": "int1", "bars": 2, "bpm": 106, "play": ["v_i1", "b_int", "k_int"]},
        {"name": "r2A", "bars": 4, "bpm": 112, "play": ["v_2A", "b_A", "k_2", "snaps"]},
        {"name": "r2A2", "bars": 4, "bpm": 112, "play": ["v_2A2", "b_Apw", "k_2", "snaps"]},
        {"name": "r2B", "bars": 4, "bpm": 112, "play": ["v_2B", "b_Bp", "k_2", "snaps", "claps"]},
        {"name": "r2B2", "bars": 4, "bpm": 112, "play": ["v_2B2", "b_Bp", "k_2", "snaps", "claps"], "fill": F},
        {"name": "int2", "bars": 2, "bpm": 118, "play": ["v_i2", "b_int", "k_int", "claps"]},
        {"name": "r3C", "bars": 4, "bpm": 124, "play": ["v_3C", "b_C", "k_2", "snaps", "claps"]},
        {"name": "r3C2", "bars": 4, "bpm": 124, "play": ["v_3C2", "b_Cw", "k_2", "snaps", "claps2"]},
        {"name": "r3A", "bars": 4, "bpm": 124, "play": ["v_3A", "b_Ap", "k_2", "snaps", "claps2"]},
        {"name": "r3B", "bars": 4, "bpm": 124, "play": ["v_3B", "b_Bp", "k_2", "snaps", "claps2"]},
        {"name": "int3", "bars": 2, "bpm": 126, "play": ["v_i3", "b_int", "k_int3", "claps2"]},
        {"name": "r4U", "bars": 4, "bpm": [126, 132], "play": ["v_4U", "b_U", "k_4h", "claps2"]},
        {"name": "r4U2", "bars": 4, "bpm": [132, 136], "play": ["v_4U2", "b_Uw", "k_4", "snaps", "claps2"], "fill": F},
        {"name": "peakA", "bars": 2, "bpm": [136, 138], "play": ["v_pkA", "b_pkA", "k_pk", "snaps", "claps2"]},
        {"name": "peakB", "bars": 2, "bpm": [138, 140], "play": ["v_pkB", "b_pkB", "k_pkB"]},
        {"name": "end", "bars": 2, "bpm": 140, "play": ["v_end", "b_end", "k_end"]},
        {"name": "tail", "bars": 1, "bpm": 140, "play": []},
    ]

# the arc in level: the door is quieter, every round a little louder, the peak loudest
LEVEL = {"prelude": (-8, -8), "rarA": (-7, -7), "rarB": (-7, -6), "ridicare": (-6, -4), "r1": (-4, -4), "int1": (-3.5, -3.5),
         "r2": (-2.5, -2.5), "int2": (-2, -2), "r3": (-1.5, -1.5), "int3": (-1.5, -1.5), "r4U": (-2, -1.5), "r4U2": (-1.2, -0.6), "peakA": (0, 0), "peakB": (0.5, 0.5), "end": (0, 0)}
if MODE != "loop":
    for sec in ARR:
        key = sec["name"] if sec["name"] in LEVEL else sec["name"][:2] if sec["name"][:2] in LEVEL else None
        if key:
            g = list(LEVEL[key])
            sec["auto"] = {t: {"gain_db": g} for t in TRACKS}

P = {"title": "Spectre - joc", "bpm": 50, "swing": 0.5, "seed": 10, "tracks": TRACKS, "patterns": PAT,
     "arrangement": ARR,
     "mix": {"reverb": {"size": 0.35, "damping": 0.6, "return_db": -9, "lpf": 6500}},
     "master": {"lufs": -11, "sat": 0.05, "glue": True}}
json.dump(P, open("project.json", "w"), indent=1)
print("wrote project.json", MODE, sum(s["bars"] for s in ARR), "pattern bars")
