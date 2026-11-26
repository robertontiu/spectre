"""Builds project.json for 018-united ("united we stand, divided we fall"). Edit here, run `python3 gen.py`, render.
Beethoven's Ode to Joy (public domain) is quoted only as whole phrases from the verified blocks in
docs/CINEMATIC_HYBRID.md "The verified melody"; harmony, form, orchestration and every other line are Spectre's."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ the verified melody (D major, sung octave)
ODE_A = ("0:F#4:4 4:F#4:4 8:G4:4 12:A4:4 16:A4:4 20:G4:4 24:F#4:4 28:E4:4 32:D4:4 36:D4:4 40:E4:4 44:F#4:4 "
         "48:F#4:6 54:E4:2 56:E4:8 64:F#4:4 68:F#4:4 72:G4:4 76:A4:4 80:A4:4 84:G4:4 88:F#4:4 92:E4:4 96:D4:4 "
         "100:D4:4 104:E4:4 108:F#4:4 112:E4:6 118:D4:2 120:D4:8")
ODE_BA = ("0:E4:4 4:E4:4 8:F#4:4 12:D4:4 16:E4:4 20:F#4:2 22:G4:2 24:F#4:4 28:D4:4 32:E4:4 36:F#4:2 38:G4:2 "
          "40:F#4:4 44:E4:4 48:D4:4 52:E4:4 56:A3:4 60:F#4:8 68:F#4:4 72:G4:4 76:A4:4 80:A4:4 84:G4:4 88:F#4:4 "
          "92:E4:4 96:D4:4 100:D4:4 104:E4:4 108:F#4:4 112:E4:6 118:D4:2 120:D4:8")

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]


def midi(n):
    m = re.match(r"([A-G])(#|b)?(-?\d)", n)
    return NOTE[m.group(1)] + {"#": 1, "b": -1, None: 0}[m.group(2)] + 12 * (int(m.group(3)) + 1)


def nm(m):
    return NAMES[m % 12] + str(m // 12 - 1)


def tr(n, semi):
    return nm(midi(n) + semi)


def toks(s):
    return [[float(t.split(":")[0]), t.split(":")[1], t.split(":")[2]] for t in s.split()]


def phrase(block, a, b, shift=0, semi=0):
    """the notes of a block with a <= step < b, moved to start at `shift`, transposed by `semi`."""
    return [[st - a + shift, tr(n, semi), ln] for st, n, ln in toks(block) if a <= st < b]


def minor(ts):
    return [[s, n.replace("F#", "F"), l] for s, n, l in ts]


def at(ts, shift, semi=0):
    return [[s + shift, tr(n, semi), l] for s, n, l in ts]


def fmt(ts, art="", vel=None):
    out = []
    for st, n, ln in ts:
        s = f"{st:g}:{n}:{ln}"
        if art:
            s += "/" + art
        if vel is not None:
            s += f":{vel}"
        out.append(s)
    return " ".join(out)


def J(*parts):
    return " ".join(p for p in parts if p)


# phrases (steps relative to the phrase's own first downbeat)
A_ = phrase(ODE_A, 0, 64)            # a   (ends on the held E: open)
A2 = phrase(ODE_A, 64, 128)          # a'  (ends on the tonic)
B_ = phrase(ODE_BA, 0, 60)           # b   (ends on the low A, beat 3 of its 4th bar)
A3 = phrase(ODE_BA, 64, 128)         # a'' after its anticipation (its first note at step 4 is the tied F#'s repeat)
HEAD = phrase(ODE_A, 0, 28)          # the head of a, cut before its E (Act I)


def trem(ts, rate=0.5, vel=0.7):
    """cimbalom tremolo: notes of 4 steps or longer become repeated 32nds."""
    out = []
    for s, n, l in ts:
        L = float(str(l).rstrip("~!."))
        if L >= 4:
            k = 0.0
            while k < L - 1e-6:
                out.append(f"{s+k:g}:{n}:{rate}:{vel if k else 0.9}")
                k += rate
        else:
            out.append(f"{s:g}:{n}:{L:g}:0.9")
    return " ".join(out)


# ------------------------------------------------------------------ harmony (half bars: root, upper)
def H(seq, semi=0):
    return [(tr(c.split("/")[0], semi), tr(c.split("/")[1], semi)) for c in seq.split()]


H_a = H("D3/A3 D3/A3 G2/D3 A2/E3 B2/F#3 B2/F#3 A2/E3 A2/E3")
H_a2 = H("D3/A3 D3/A3 G2/D3 A2/E3 B2/F#3 G2/D3 A2/E3 D3/A3")
H_b = H("A2/E3 D3/A3 A2/E3 D3/A3 A2/E3 B2/F#3 G2/D3 A2/E3")
H_min = H("D3/A3 D3/A3 Bb2/F3 Bb2/F3 G2/D3 G2/D3 A2/E3 A2/E3")
H_D = H("D3/A3 D3/A3 G2/D3 G2/D3 A2/E3 A2/E3 D3/A3 D3/A3")
H_climb = H("B2/F#3 B2/F#3 G2/D3 G2/D3 E2/B2 E2/B2 A2/E3 A2/E3")
H_F = H("F2/C3 F2/C3 Bb2/F3 C3/G3 D3/A3 Bb2/F3 C3/G3 F2/C3")
MINORS_D = {"B", "E"}
MINORS_F = {"D", "G"}


def ost(harm, art="sp", acc="x..x..x.x..x..x.", octave=0, vel=(0.95, 0.55), gaps=None):
    """16th ostinato over half-bar (root, upper) pairs; accents take the upper note. gaps: half bars left silent."""
    r = []
    for h, (root, upper) in enumerate(harm):
        if gaps and h in gaps:
            continue
        for k in range(8):
            kk = (h % 2) * 8 + k
            n = upper if acc[kk] == "x" else root
            r.append(f"{h*8+k}:{tr(n, 12*octave)}:1/{art}:{vel[0] if acc[kk]=='x' else vel[1]}")
    return " ".join(r)


def eighths(harm, octave=1, art="sp", vel=(0.85, 0.55)):
    r = []
    for h, (root, upper) in enumerate(harm):
        for k in range(0, 8, 2):
            n = root if k % 4 == 0 else upper
            r.append(f"{h*8+k}:{tr(n, 12*octave)}:2/{art}:{vel[0] if k == 0 else vel[1]}")
    return " ".join(r)


def fold(m, lo, hi):
    while m < lo:
        m += 12
    while m > hi:
        m -= 12
    return m


def hits(harm, octave, ln=3, steps=(0, 6, 12), art="sp", vel=0.9, rng=None):
    r = []
    for b in range(len(harm) // 2):
        for k in steps:
            root = harm[b * 2 + (1 if k >= 8 else 0)][0]
            m = midi(root) + 12 * octave
            if rng:
                m = fold(m, *rng)
            r.append(f"{b*16+k}:{nm(m)}:{ln}" + (f"/{art}" if art else "") + f":{vel}")
    return " ".join(r)


def subhits(harm, vel=0.9):
    return hits(harm, -2, art="", vel=vel, rng=(midi("E1"), midi("D#2")))


def held(harm, octave, art="", vel=0.8, upper=False):
    """one held note per change of root (or of the upper note)."""
    r, prev, start = [], None, 0
    seq = [u if upper else ro for ro, u in harm] + [None]
    for h, n in enumerate(seq):
        if n != prev:
            if prev is not None:
                r.append(f"{start*8}:{tr(prev, 12*octave)}:{(h-start)*8}" + (f"/{art}" if art else "") + f":{vel}")
            prev, start = n, h
    return " ".join(r)


def chord(step, notes, ln, art="", vel=0.8):
    return " ".join(f"{step:g}:{n}:{ln}" + (f"/{art}" if art else "") + f":{vel}" for n in notes)


def pulse8(harm, octave=1, vel=(0.9, 0.6)):
    return " ".join(f"{h*8+k}:{tr(harm[h][0], 12*octave)}:1:{vel[0] if k % 4 == 0 else vel[1]}"
                    for h in range(len(harm)) for k in range(0, 8, 2))


def chordnames(harm, minors):
    out = []
    for r, _ in harm:
        root = re.match(r"[A-G][b#]?", r).group(0)
        out.append(root + ("m" if root in minors else "") + ":8")
    return " ".join(out)


# my own countermelody (half notes, contrary to the tune): one line through the hand-offs, the climax's descant
C_a = toks("0:A3:8 8:B3:8 16:D4:8 24:C#4:8 32:B3:8 40:A3:8 48:G3:8 56:A3:8")
C_a2 = toks("0:A3:8 8:B3:8 16:D4:8 24:C#4:8 32:D4:8 40:E4:8 48:C#4:8 56:D4:8")
C_b = toks("0:C#4:8 8:A3:8 16:C#4:8 24:D4:8 32:C#4:8 40:B3:8 48:B3:8 56:C#4:4")

# ------------------------------------------------------------------ tracks
T = {}


def trk(name, inst, role, gain=0.0, pan=0.0, hall=0.3, room=0.0, bus=None, **kw):
    t = {"inst": inst, "role": role, "gain_db": gain, "pan": pan, "sends": {}}
    if hall:
        t["sends"]["hall"] = hall
    if room:
        t["sends"]["room"] = room
    if bus:
        t["bus"] = bus
    t.update(kw)
    T[name] = t


# folk soloists: one hall, each its own seat
trk("trembita", {"type": "trembita", "bright": 0.5, "blare": 0.25, "attack": 0.3}, "lead", -4, 0.55, 0.5)
trk("nai", {"type": "nai", "breath": 0.3, "vibrato": 0.15}, "lead", -2, -0.2, 0.55)
trk("kokle", {"type": "kokle", "ring": 0.75, "bright": 0.6}, "lead", 2, -0.55, 0.35)
trk("accordion", {"type": "accordion", "ranks": 2, "musette": 12, "attack": 0.05}, "lead", -3, 0.5, 0.3)
trk("lira", {"type": "lira", "buzz": 0.25, "buzz_rate": 6.67, "attack": 0.06}, "lead", -2, -0.3, 0.3)
trk("violin", {"type": "violin", "vibrato": 0.3, "pressure": 0.75}, "lead", -2, 0.3, 0.3)
trk("cimbalom", {"type": "cimbalom", "hard": 0.55, "damp": 0.3}, "lead", -11, -0.45, 0.25)

# orchestra
trk("violins", {"type": "strings_section", "section": "violins", "players": 12, "air": 1.0}, "strings", 12, -0.15, 0.3, bus="strings")
trk("violas", {"type": "strings_section", "section": "violas"}, "strings", 18, -0.35, 0.18, bus="strings")
trk("celli", {"type": "strings_section", "section": "celli"}, "low-strings", 12, 0.3, 0.15, bus="strings")
trk("basses", {"type": "strings_section", "section": "basses"}, "low-strings", 9, 0.1, 0.12, bus="strings")
trk("bassoon", {"type": "woodwind", "instrument": "bassoon"}, "brass", -4, 0.15, 0.3)
trk("horns", {"type": "brass", "section": "horns", "players": 6}, "brass", 4, -0.2, 0.3, bus="brass")
trk("horns2", {"type": "brass", "section": "horns", "players": 4}, "brass", 0, 0.35, 0.3, bus="brass")
trk("trumpets", {"type": "brass", "section": "trumpets", "vibrato": 0.03}, "brass", 0, 0.15, 0.3, bus="brass")
trk("trombones", {"type": "brass", "section": "trombones"}, "brass", 1, 0.2, 0.25, bus="brass")
trk("tuba", {"type": "brass", "section": "tuba"}, "brass", 0, 0.0, 0.15, bus="brass")
trk("choir", {"type": "vox2choir", "voices": 8, "vowels": "ah oh", "onset": "h", "voice": "soprano"}, "choir", -6, 0.0, 0.4)
trk("choirpad", {"type": "choir", "vowel": "ah", "attack": 0.4, "release": 1.0}, "choir", -9, 0.0, 0.4, width=0.7)
trk("pulse", {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 10},
                                           {"shape": "square", "octave": -1, "level": 0.4}],
              "cutoff": 900, "env": 2500, "fdecay": 0.06, "sustain_level": 0, "decay": 0.12, "release": 0.05},
    "pad", 4, 0.0, 0.0, room=0.1, width=0.6)
trk("drone", {"type": "polysynth", "osc": [{"shape": "saw", "voices": 3, "detune": 8}, {"shape": "triangle", "octave": -1, "level": 0.5}],
              "cutoff": 380, "attack": 2.5, "release": 3.0, "drift": 0.5,
              "lfo": [{"dest": "cutoff", "rate": 0.11, "depth": 0.5, "shape": "smooth"}]},
    "pad", -10, 0.0, 0.45, width=0.8)
trk("sub", {"type": "sub", "harmonics": 0.1, "release": 0.15}, "sub", -5, hall=0)

# percussion and trailer sounds
trk("taiko", {"type": "taiko", "players": 4}, "kick", 0, 0.0, 0.1, room=0.3, bus="drums")
trk("toms", {"type": "taiko", "players": 3, "tune": 112, "decay": 0.35, "spread_ms": 9}, "perc", -8, 0.0, 0.08,
    room=0.35, bus="drums", humanize={"ms": 5})
trk("gran", {"type": "bassdrum"}, "kick", -2, 0.0, 0.2, bus="drums")
trk("timp", {"type": "timpani"}, "perc", -2, 0.1, 0.25, bus="drums")
trk("cym", {"type": "suscymbal"}, "cymbals", -4, 0.0, 0.25)
trk("crash", {"type": "suscymbal", "mode": "hit", "decay": 1.2}, "cymbals", 8, 0.0, 0.3, width=0.5)
trk("hit", {"type": "impact"}, "fx", -3, 0.0, 0.35, bus="drums")
trk("braam", {"type": "braam"}, "brass", -4, 0.0, 0.3)
trk("riser", {"type": "shepard"}, "fx", -10, 0.0, 0.2)

P = {}
ARR = []


def sec(name, bars, parts, **kw):
    P[name] = dict(bars=bars, **{k: v for k, v in parts.items() if v})
    ARR.append(dict(name=name, bars=bars, play=[name], **kw))


crowd = "x..x..x.x...x.x." + "x..x..x.x.x.x.x."
half = "x.......x......." + "x.......x.....x."
heart = ("6..3" + "." * 12)

# ================================================================== ACT I: divided (D minor), bars 1-24
sec("I1", 4, {  # the heartbeat; a call across the valley
    "drone": "0:D2:64:0.6 0:A2:64:0.5",
    "gran": heart * 4,
    "sub": " ".join(f"{b*16}:D1:3:0.7" for b in range(4)),
    "trembita": "0:D3:10 16:A3:6 24:D3:20 52:A2:12",
})
sec("I2", 4, {  # the broken ostinato: two beats, then nothing; one braam
    "drone": "0:D2:64:0.6 0:A2:64:0.5",
    "gran": heart * 4,
    "sub": " ".join(f"{b*16}:D1:3:0.7" for b in range(4)),
    "celli": ost(H_min, gaps={1, 3, 5, 7}, vel=(0.8, 0.45)),
    "basses": " ".join(f"{h*8}:{tr(H_min[h][0], -12)}:4/sp:0.8" for h in range(0, 8, 2)),
    "braam": "0:D2:24",
    "trembita": "40:A2:16",
})
sec("I3", 4, {  # the far voice: the head of a in minor, cut off before its E
    "drone": "0:D2:64:0.55 0:A2:64:0.45",
    "gran": heart * 4,
    "sub": "0:D1:3:0.7 16:D1:3:0.7 28:D1:6:1.0 48:D1:3:0.7",
    "nai": fmt(minor(HEAD)),
    "celli": "0:D3:24/swell:0.4",
    "hit": "." * 28 + "x" + "." * 35,
    "trombones": chord(28, ["Bb2", "D3", "F3"], 6, "sfz", 0.9),
    "tuba": chord(28, ["Bb1"], 6, "sfz", 0.9),
    "taiko": "." * 28 + "x" + "." * 35,
})
sec("I4", 4, {  # the ostinato resumes, darker, still breaking
    "drone": "0:D2:64:0.6 0:A2:32:0.5 32:Bb2:32:0.5",
    "gran": heart * 4,
    "sub": " ".join(f"{b*16}:D1:3:0.7" for b in range(4)),
    "celli": ost(H_min, gaps={3, 7}),
    "basses": hits(H_min, -1, vel=0.8),
    "trombones": J(chord(0, ["D3", "F3", "A3"], 16, "swell", 0.5), chord(32, ["G2", "D3", "Bb3"], 16, "swell", 0.5)),
})
H_strug = H_min + H_min
sec("I5", 8, {  # the struggle: the motor holds, low brass pushes, the drums gather
    "celli": ost(H_strug),
    "violas": ost(H_strug, acc="x.x.x.x.x.x.x.x.", octave=1, vel=(0.8, 0.5)),
    "basses": hits(H_strug, -1), "sub": subhits(H_strug),
    "taiko": ("x.......x....x.." + "x.......x.......") * 3 + "x.......x...x.xx" + "x...x...x.x.xxxx",
    "gran": ("x" + "." * 15) * 8,
    "trombones": J(chord(0, ["D3", "F3", "A3"], 16, "swell", 0.6), chord(16, ["Bb2", "D3", "F3"], 16, "swell", 0.6),
                   chord(32, ["G2", "Bb2", "D3"], 16, "swell", 0.7), chord(48, ["A2", "C#3", "E3"], 16, "sfz", 0.8),
                   chord(64, ["D3", "F3", "A3"], 16, "swell", 0.75), chord(80, ["Bb2", "D3", "F3"], 16, "swell", 0.8),
                   chord(96, ["G2", "Bb2", "D3"], 16, "swell", 0.85), chord(112, ["A2", "C#3", "E3"], 16, "swell", 0.95)),
    "tuba": "0:D2:16/swell:0.6 16:Bb1:16/swell:0.6 32:G1:16/swell:0.7 48:A1:16/sfz:0.8 64:D2:16/swell:0.75 "
            "80:Bb1:16/swell:0.8 96:G1:16/swell:0.85 112:A1:16/swell:0.95",
    "trembita": "64:A2:12 96:D3:8 104:A3:24",
    "cym": "96:C4:32",
}, exit={"cut": {"tracks": "all", "beats": 0.5}})

# ================================================================== ACT II: the relay (D major), bars 25-48
sec("II0", 4, {  # the motor turns major and light
    "violas": eighths(H_D, 1), "pulse": pulse8(H_D, 1, vel=(0.7, 0.45)),
    "celli": " ".join(f"{h*8}:{H_D[h][0]}:4/pz:0.8" for h in range(8)),
    "trembita": "0:D3:16 32:A2:24",
})
sec("II1", 4, {  # a: kokle (the Baltic)
    "kokle": fmt(A_, vel=0.85),
    "accordion": "56:E4:8/swell:0.6",     # the next voice enters on this one's last note
    "violas": eighths(H_a, 1), "pulse": pulse8(H_a, 1, vel=(0.7, 0.45)),
    "celli": " ".join(f"{h*8}:{H_a[h][0]}:4/pz:0.8" for h in range(8)),
})
sec("II2", 4, {  # a': accordion (the musette); the bassoon's countermelody begins; drums half time
    "accordion": fmt(A2, vel=0.8), "lira": "56:D4:8:0.6",
    "bassoon": fmt(at(C_a2, 0, -12), vel=0.75),
    "violas": eighths(H_a2, 1), "pulse": pulse8(H_a2, 1, vel=(0.75, 0.5)),
    "celli": ost(H_a2, vel=(0.75, 0.45)),
    "taiko": half * 2,
})
sec("II3", 4, {  # b: hurdy-gurdy (vielle, tekerőlant, zanfona) with its drone; basses and sub arrive
    "lira": J(fmt(B_, vel=0.8), "0:D3:56:0.45", "56:A3:8:0.7"),
    "violin": "60:F#4:8/sl-2:0.85",
    "bassoon": fmt(at(C_b, 0, -12), vel=0.75),
    "violas": eighths(H_b, 1), "pulse": pulse8(H_b, 1, vel=(0.75, 0.5)),
    "celli": ost(H_b, vel=(0.8, 0.5)), "basses": hits(H_b, -1, vel=0.75), "sub": subhits(H_b, 0.75),
    "taiko": half * 2,
})
sec("II4", 4, {  # a'': lăutar violin, taking the anticipation over the lira's low A; low brass under
    "violin": fmt(A3, vel=0.85), "cimbalom": "56:D4:8:0.7",
    "bassoon": fmt(at(C_a2, 0, -12), vel=0.75),
    "violas": eighths(H_a2, 1), "pulse": pulse8(H_a2, 1, vel=(0.8, 0.5)),
    "celli": ost(H_a2, vel=(0.85, 0.5)), "basses": hits(H_a2, -1, vel=0.8), "sub": subhits(H_a2, 0.8),
    "trombones": held(H_a2, 0, "swell", 0.45), "horns2": held(H_a2, 1, "", 0.4, upper=True),
    "taiko": half * 2,
})
sec("II5", 4, {  # b again: cimbalom (Hungary, Romania, Ukraine), tremolo; horns take the countermelody
    "cimbalom": trem(B_),
    "horns": fmt(C_b, vel=0.6),
    "violas": eighths(H_b, 1), "pulse": pulse8(H_b, 1, vel=(0.8, 0.5)),
    "celli": ost(H_b, vel=(0.85, 0.5)), "basses": hits(H_b, -1, vel=0.8), "sub": subhits(H_b, 0.8),
    "trombones": held(H_b, 0, "swell", 0.5),
    "taiko": "x.......x......." + "x.......x...x.x." + "x.......x......." + "x.......x...x.x.",
    # the anticipation taken by every soloist together: the heterophony begins
    "kokle": "60:F#4:8:0.85", "accordion": "60:F#4:8:0.8", "violin": "60:F#4:8/sl-2:0.85", "lira": "60:F#4:8:0.75",
})

A3_AUTO = {"drums": {"gain_db": [-3, -2]}, "strings": {"gain_db": -2}, "kokle": {"gain_db": -2}, "accordion": {"gain_db": -2},
           "lira": {"gain_db": -2}, "violin": {"gain_db": -2}, "cimbalom": {"gain_db": -2}}
# ================================================================== ACT III: together (D major), bars 49-64
sec("III1", 4, {  # a'' in heterophony: five traditions on one line; drums to full time
    "kokle": fmt(A3, vel=0.8), "accordion": fmt(A3, vel=0.75), "lira": fmt(A3, vel=0.7),
    "violin": fmt(A3, vel=0.8), "cimbalom": trem(A3, vel=0.6),
    "violas": ost(H_a2, acc="x.x.x.x.x.x.x.x.", octave=1, vel=(0.85, 0.5)), "pulse": pulse8(H_a2, 1),
    "celli": ost(H_a2), "basses": hits(H_a2, -1), "sub": subhits(H_a2, 0.85),
    "horns": fmt(C_a2, vel=0.65), "trombones": held(H_a2, 0, "swell", 0.55),
    "taiko": half * 2, "gran": "x..............." * 4,
}, auto=dict(A3_AUTO, drums={"gain_db": -4}, kokle={"gain_db": -5}, accordion={"gain_db": -5}, lira={"gain_db": -5},
             violin={"gain_db": -5}, cimbalom={"gain_db": -5}, strings={"gain_db": -3}))
sec("III2", 4, {  # the head in canon, one bar apart: kokle, accordion, lira, violin; the choir arrives
    "kokle": fmt(phrase(ODE_A, 0, 32), vel=0.8),
    "accordion": fmt(phrase(ODE_A, 0, 32, 16), vel=0.75),
    "lira": fmt(phrase(ODE_A, 0, 32, 32), vel=0.7),
    "violin": fmt(phrase(ODE_A, 0, 16, 48, 12), vel=0.85),
    "cimbalom": trem([[0, "D4", "16"], [16, "E4", "16"], [32, "F#4", "16"], [48, "E4", "16"]], vel=0.5),
    "violas": ost(H_D, acc="x.x.x.x.x.x.x.x.", octave=1), "pulse": pulse8(H_D, 1),
    "celli": ost(H_D), "basses": hits(H_D, -1), "sub": subhits(H_D, 0.85),
    "choir": "0:A4:16:0.5 16:B4:16:0.55 32:C#5:16:0.6 48:D5:16:0.65",
    "choirpad": {"chords": "D:16 G/D:16 A/D:16 D:16", "style": "sustain", "register": "D4", "voicing": "close", "vel": 0.6},
    "horns": "0:D4:16/swell:0.5 16:D4:16/swell:0.55 32:E4:16/swell:0.6 48:F#4:16/swell:0.65",
    "trombones": held(H_D, 0, "swell", 0.6),
    "taiko": crowd * 2, "gran": "x.......x......." * 4,
}, auto=A3_AUTO)
sec("III3", 4, {  # b fragments climbing; the violins join the motor two octaves up; the riser starts
    "kokle": fmt(phrase(ODE_BA, 0, 32), vel=0.8), "accordion": fmt(phrase(ODE_BA, 0, 32, 32), vel=0.8),
    "lira": fmt(phrase(ODE_BA, 0, 32, 16), vel=0.7), "violin": fmt(phrase(ODE_BA, 0, 32, 32, 12), vel=0.85),
    "cimbalom": trem([[0, "F#4", "16"], [16, "G4", "16"], [32, "E4", "16"], [48, "A4", "16"]], vel=0.55),
    "violins": ost(H_climb, acc="x.x.x.x.x.x.x.x.", octave=2, vel=(0.8, 0.5)),
    "violas": ost(H_climb, acc="x.x.x.x.x.x.x.x.", octave=1), "pulse": pulse8(H_climb, 1),
    "celli": ost(H_climb), "basses": hits(H_climb, -1), "sub": subhits(H_climb, 0.9),
    "choir": "0:B4:16:0.6 16:D5:16:0.65 32:E5:16:0.7 48:E5:16:0.75",
    "choirpad": {"chords": "Bm:16 G:16 Em:16 A:16", "style": "sustain", "register": "D4", "voicing": "close", "vel": 0.65},
    "horns": "0:F#4:16/swell:0.6 16:G4:16/swell:0.65 32:G4:16/swell:0.7 48:A4:16/swell:0.75",
    "trombones": held(H_climb, 0, "swell", 0.7), "tuba": held(H_climb, -1, "swell", 0.6),
    "taiko": crowd * 2, "gran": "x.......x......." * 4, "toms": "." * 32 + "....x.....x...xx" + "x.x.x.xxx.xxxxxx",
    "riser": "0:C4:64",
}, auto=dict(A3_AUTO, drums={"gain_db": [-2, 0]}, strings={"gain_db": [-2, 0]}, brass={"gain_db": [-1, 1]}))
sec("III4", 3, {  # the lead-in, nearly without bass: b high on violins and soloists, no drums
    "violins": fmt(phrase(ODE_BA, 0, 48, 0, 12), vel=0.8),
    "riser": "0:C4:48", "cym": "16:C4:32",
}, auto={"violins": {"gain_db": -9}})
# the edge bar (64): D, E on beats 1-2, beat 3 withheld (the low A), beat 4 the anticipation by everyone
sec("III5", 1, {
    "violins": "0:D5:3:0.8 4:E5:3:0.8 12:F#5:8:0.95", "violin": "12:F#5:8/sl-2:0.9",
    "accordion": "12:F#4:8:0.85", "kokle": "12:F#4:8:0.9",
    "lira": "12:F#4:8:0.8", "cimbalom": "12:F#4:0.5:0.9",
    "horns": "12:F#4:8:0.95", "trombones": "12:F#3:8:0.9", "trumpets": "12:F#5:8/rip:0.85",
    "choir": "12:F#5:8:0.85", "tuba": "12:D2:8:0.9", "basses": "12:D2:4/sp:1.0", "sub": "12:D1:6:1.0",
    "timp": "12:D3:2:1.0", "gran": "............x...", "crash": "12:C4:8:1.0", "taiko": "............x...", "hit": "............x...",
})


# ================================================================== ACT IV: united (D major, then F), bars 65-88
def tutti(name, mel, harm, minors, semi=0, extra=None):
    """the full theme: horns at pitch, trombones 8vb, trumpets 8va, violins 8va, choir 8va, ostinato, drums."""
    bars = len(harm) // 2
    mel = at(mel, 0, semi)
    tonic = midi(harm[0][0])
    parts = {
        "horns": fmt(mel, vel=0.9), "trombones": fmt(at(mel, 0, -12), vel=0.85), "trumpets": fmt(at(mel, 0, 12), vel=0.8),
        "violins": fmt(at(mel, 0, 12), vel=0.9), "choir": fmt(at(mel, 0, 12), vel=0.8),
        "choirpad": {"chords": chordnames(harm, minors), "style": "sustain", "register": tr("D4", semi),
                     "voicing": "close", "vel": 0.7},
        "violas": ost(harm, acc="x.x.x.x.x.x.x.x.", octave=1), "pulse": pulse8(harm, 1),
        "celli": ost(harm), "basses": hits(harm, -1), "sub": subhits(harm),
        "tuba": held(harm, -1, "", 0.8),
        "taiko": crowd * (bars // 2), "gran": "x.......x......." * bars,
        "timp": " ".join(f"{b*16}:{nm(fold(midi(harm[b*2][0]), midi('F#2'), midi('G3')))}:2:0.9" for b in range(bars)),
    }
    if extra:
        parts.update(extra)
    sec(name, bars, parts, auto={"brass": {"gain_db": 3}, "drums": {"gain_db": 3}, "violin": {"gain_db": -7},
                                 "violins": {"gain_db": -4}, "choir": {"gain_db": 2}, "tuba": {"gain_db": -3},
                                 "cimbalom": {"gain_db": -6}, "accordion": {"gain_db": -5}, "kokle": {"gain_db": -3},
                                 "lira": {"gain_db": -3}})


tutti("IV1", A3, H_a2, MINORS_D, extra={"crash": "0:C4:8:0.9 32:C4:8:0.8"})
tutti("IV2", A_ + at(A2, 64), H_a + H_a2, MINORS_D, extra={
    "crash": "0:C4:8:0.9 32:C4:8:0.8 64:C4:8:0.9 96:C4:8:0.8",
    "violin": fmt(at(C_a + at(C_a2, 64), 0, 24), vel=0.8),
    "accordion": fmt(at(C_a + at(C_a2, 64), 0, 12), vel=0.7),
    "cimbalom": trem(at(C_a + at(C_a2, 64), 0, 12), vel=0.55),
})
tutti("IV3", B_, H_b, MINORS_D, extra={"violin": fmt(at(C_b, 0, 24), vel=0.8), "accordion": fmt(at(C_b, 0, 12), vel=0.7),
                                       "kokle": fmt(at(C_b, 0, 12), vel=0.7), "lira": fmt(at(C_b, 0, 12), vel=0.6),
                                       # a breath inside the triumph: b with the drums in half time, no trumpets
                                       "taiko": half * 2, "gran": "x" + "." * 31 + "x" + "." * 31, "trumpets": "",
                                       "timp": "", "cym": "28:C4:32"})
ARR[-1]["auto"] = {"brass": {"gain_db": [-3, -3, -3, 0]}, "drums": {"gain_db": [-3, -3, -3, 0]}, "violin": {"gain_db": -4},
                   "accordion": {"gain_db": -2}, "kokle": {"gain_db": 0}, "lira": {"gain_db": -1}, "choir": {"gain_db": 2},
                   "violins": {"gain_db": -6}, "tuba": {"gain_db": -6}, "violas": {"gain_db": -3}, "celli": {"gain_db": -3},
                   "pulse": {"gain_db": -4}}
# the lift: the anticipation lands on A4 = the third of F major (A held as the common tone; A major -> F major).
# Everything under it moves to F on that beat too, so the turn is heard as harmony, not as a smear.
def cut_from(pat, step):
    return " ".join(t for t in pat.split() if float(t.split(":")[0]) < step)


HF1 = H("F2/C3 F2/C3")
def tail(pat, start=4, at_step=56):
    return " ".join(f"{float(t.split(':')[0]) + at_step:g}:" + ":".join(t.split(":")[1:])
                    for t in pat.split() if start <= float(t.split(":")[0]) < 8)


for k, new in {"celli": tail(ost(HF1)), "violas": tail(ost(HF1, acc="x.x.x.x.x.x.x.x.", octave=1)),
               "pulse": tail(pulse8(HF1, 1))}.items():
    P["IV3"][k] = J(cut_from(P["IV3"][k], 60), new)
for k in ("basses", "sub"):
    P["IV3"][k] = cut_from(P["IV3"][k], 60)
P["IV3"]["choirpad"]["chords"] = P["IV3"]["choirpad"]["chords"].rsplit(" ", 1)[0] + " A:4 F:4"
P["IV3"]["choir"] = ""

for k, v in {"horns": "60:A4:8:1.0", "trombones": "60:C4:8:0.95", "trumpets": "60:A5:8:0.95", "violins": "60:A5:8:1.0",
             "choir": "60:A5:8:0.9", "tuba": "60:F1:8:0.9", "trembita": "60:F3:40:0.8", "basses": "60:F2:4/sp:1.0",
             "sub": "60:F1:6:1.0"}.items():
    P["IV3"][k] = J(P["IV3"].get(k, ""), v)
tutti("IV4", A3, H_F, MINORS_F, semi=3, extra={
    "violin": fmt(at(C_a2, 0, 27), vel=0.85), "accordion": fmt(at(C_a2, 0, 15), vel=0.75),
    "kokle": fmt(at(C_a2, 0, 15), vel=0.75), "lira": fmt(at(C_a2, 0, 15), vel=0.6),
    "trembita": "0:F3:16:0.7 32:C3:16:0.7 48:F3:16:0.8", "crash": "0:C4:8:0.9 32:C4:8:0.8"})
sec("IV5", 4, {  # the held tonic (F major): brass and drums let go; strings and choir keep holding into the coda
    "horns": chord(0, ["F4", "A4", "C5"], 64, "dim", 0.85), "trombones": chord(0, ["F3", "C4"], 64, "dim", 0.8),
    "trumpets": chord(0, ["F5", "A5"], 32, "dim", 0.75), "tuba": "0:F1:64/dim:0.8",
    "violins": chord(0, ["F5", "C6"], 224, "", 0.8),
    "violas": chord(0, ["A4", "C5"], 224, "", 0.75),
    "celli": chord(0, ["F3", "C4"], 224, "", 0.75), "basses": "0:F2:256:0.8", "sub": "0:F1:32:0.8",
    "choir": "0:A5:48:0.8", "choirpad": {"chords": "F:64", "style": "sustain", "register": "F4", "voicing": "close", "vel": 0.7},
    "timp": "0:F3:48/roll:0.5", "gran": "x" + "." * 63, "trembita": "0:F3:64:0.6",
}, auto={"violins": {"gain_db": [0, -8]}, "violas": {"gain_db": [-6, -14]}, "celli": {"gain_db": [-6, -14]},
         "basses": {"gain_db": [0, -10]}, "timp": {"gain_db": -8}})
# ================================================================== CODA, bars 89-100: the nai finishes its phrase
sec("CODA", 11, {  # a + a' in F: the whole first half of the tune, ending on the tonic, inside the held F; the minor iv once
    "nai": fmt(at(A_ + at(A2, 64), 16, 3), vel=0.8).replace("136:F4:8", "136:F4:40"),
    "violins": "160:F5:16:0.6 160:Db6:16:0.55",
    "violas": "160:Bb4:16:0.55",
    "horns2": "160:Db4:16/swell:0.45 160:F4:16/swell:0.45",
    "choirpad": {"chords": "F:16 F:16 Bb/F:8 C/F:8 Dm/F:16 C/F:16 F:16 Bb/F:8 C/F:8 Dm/F:8 Bb/F:8 C/F:8 F:24 Bbm/F:16",
                 "style": "sustain", "register": "F4", "voicing": "close", "vel": 0.5},
    "trembita": "0:F2:32:0.4",
}, auto={"celli": {"gain_db": [-14, -22]}, "basses": {"gain_db": [-10, -20]}, "violins": {"gain_db": [-8, -14]},
         "violas": {"gain_db": [-14, -20]}})
sec("END", 3, {  # the last F: everyone who stayed, let go together into the hall
    "violins": "0:F5:44:0.6 0:A5:44:0.55 0:C6:44:0.5", "violas": "0:C5:44:0.5",
    "horns2": "0:C4:40/dim:0.45 0:F4:40/dim:0.45 0:A4:40/dim:0.45",
    "choirpad": {"chords": "F:44", "style": "sustain", "register": "F4", "voicing": "close", "vel": 0.5},
}, auto={"celli": {"gain_db": [-22, -30, -60]}, "basses": {"gain_db": [-20, -28, -60]}, "violins": {"gain_db": [-14, -22, -50]},
         "violas": {"gain_db": [-20, -28, -50]}, "choirpad": {"gain_db": [0, -8, -40]}, "horns2": {"gain_db": [0, -8, -40]}})

# ------------------------------------------------------------------ the arc in level: everything before the triumph a little further away
def offset(names, db):
    buses = ("strings", "brass", "drums")
    for sct in ARR:
        if sct["name"] not in names:
            continue
        au = sct.setdefault("auto", {})
        for t in list(T) + list(buses):
            if t in T and T[t].get("bus"):
                continue
            g = au.setdefault(t, {}).get("gain_db", 0)
            au[t]["gain_db"] = [x + db for x in g] if isinstance(g, list) else g + db


offset({"I5", "II0", "II1", "II2", "II3", "II4", "II5"}, -2.0)
offset({"III1", "III2", "III3", "III4", "III5"}, -1.5)
offset({"CODA", "END"}, -3.0)
ARR[[x["name"] for x in ARR].index("CODA")]["auto"]["nai"]["gain_db"] += 2.5   # the voice that was cut off, in front

project = {
    "title": "United", "bpm": 100, "swing": 0.5, "seed": 18, "seeds": "per-track", "voice_defaults": 2,
    "genre": "cinematic", "key": "D minor / D major / F major",
    "tracks": T, "patterns": P, "arrangement": ARR,
    "buses": {"strings": {"fx": [{"type": "comp", "threshold_db": -20, "ratio": 2}, {"type": "sat", "amount": 0.1},
                                  {"type": "highshelf", "hz": 7000, "gain_db": 3.5}]},
              "brass": {"fx": [{"type": "sat", "amount": 0.15}, {"type": "comp", "threshold_db": -18, "ratio": 2}]},
              "drums": {"fx": [{"type": "comp", "threshold_db": -16, "ratio": 2}, {"type": "clip", "ceiling_db": -3}]}},
    "mix": {"returns": {"hall": {"type": "hall", "predelay_ms": 22, "return_db": -1, "hpf": 220},
                        "room": {"type": "reverb", "size": 0.35, "damping": 0.6, "predelay_ms": 8, "return_db": -10}}},
    "master": {"lufs": -12.5},
}
json.dump(project, open(os.path.join(HERE, "project.json"), "w"), indent=1)
tot = sum(s["bars"] for s in ARR)
print("bars", tot, f"{int(tot*2.4//60)}:{tot*2.4%60:04.1f}", "tracks", len(T))
