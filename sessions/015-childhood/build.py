#!/usr/bin/env python3
"""build.py [loop|full] : writes project.json for 015-childhood ("Again, Again").
Grid: quarter = 4 steps; a fast waltz bar = 12 steps; a slow (watcher) bar = 24 steps."""
import json, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "full"
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT = {"Bb": "A#", "Eb": "D#", "Ab": "G#", "Db": "C#", "Gb": "F#"}


def tr(n, semis):
    """transpose a note name"""
    if not semis:
        return n
    name, octv = n[:-1], int(n[-1])
    name = FLAT.get(name, name)
    i = NOTES.index(name) + semis
    return NOTES[i % 12] + str(octv + i // 12)


# ---------------------------------------------------------------- the material
# the child's tune: five notes only (D E F# A B). per bar: (note, beats)
CHILD = [
    [("D5", 2), ("B4", 1)], [("A4", 2), ("F#4", 1)], [("A4", 1), ("B4", 1), ("D5", 1)], [("E5", 3)],
    [("F#5", 2), ("E5", 1)], [("D5", 2), ("B4", 1)], [("D5", 1), ("E5", 1), ("D5", 1)], [("A4", 3)],
    [("D5", 2), ("B4", 1)], [("A4", 2), ("F#4", 1)], [("A4", 1), ("B4", 1), ("D5", 1)], [("E5", 3)],
    [("B4", 1), ("D5", 1), ("F#5", 1)], [("A5", 2), ("F#5", 1)], [("E5", 2), ("B4", 1)], [("D5", 3)],
]
# the watcher's version: the same notes on the beats, the gaps filled with G and C#
ADULT = [
    [("D5", 2), ("C#5", .5), ("B4", .5)], [("A4", 2), ("G4", .5), ("F#4", .5)],
    [("A4", 1), ("B4", 1), ("C#5", .5), ("D5", .5)], [("E5", 3)],
    [("F#5", 2), ("E5", 1)], [("D5", 2), ("C#5", .5), ("B4", .5)], [("D5", 1), ("E5", 1), ("D5", 1)], [("A4", 3)],
    [("D5", 2), ("C#5", .5), ("B4", .5)], [("A4", 2), ("G4", .5), ("F#4", .5)],
    [("A4", 1), ("B4", 1), ("C#5", .5), ("D5", .5)], [("E5", 3)],
    [("B4", 1), ("D5", 1), ("F#5", 1)], [("A5", 2), ("G5", .5), ("F#5", .5)], [("E5", 2), ("C#5", 1)], [("D5", 3)],
]
# B, the run down the hill
BRUN = [
    [("B4", 1), ("D5", 1), ("G5", 1)], [("F#5", .5), ("E5", .5), ("D5", .5), ("E5", .5), ("D5", .5), ("B4", .5)],
    [("A4", 1), ("D5", 1), ("F#5", 1)], [("E5", .5), ("D5", .5), ("B4", .5), ("D5", .5), ("B4", .5), ("A4", .5)],
    [("B4", 1), ("D5", 1), ("G5", 1)], [("G#5", 2), ("B5", 1)], [("A5", 1), ("G5", 1), ("E5", 1)], [("E5", 3)],
    [("D5", 1), ("F#5", 1), ("B5", 1)], [("A5", .5), ("F#5", .5), ("E5", .5), ("F#5", .5), ("E5", .5), ("C#5", .5)],
    [("B4", 1), ("D5", 1), ("G5", 1)], [("F#5", .5), ("E5", .5), ("D5", .5), ("E5", .5), ("D5", .5), ("A4", .5)],
    [("G4", 1), ("B4", 1), ("E5", 1)], [("G#4", 1), ("B4", 1), ("D5", 1)], [("D5", 3)], [("C#5", 1)],
]
H_A = ["D", "F#m", "G", "A", "Bm", "G", "Em7", "A", "D", "F#m", "G", "A", "G", "D/F#", "A", "D"]
H_AD = ["D", "F#m", "G", "A", "Bm", "G", "Em7", "A", "D", "F#m", "G", "Gm6", "G", "D/F#", "A", "D"]  # the watcher's
H_B = ["G", "G", "D/F#", "D/F#", "G", "E", "Asus", "A", "Bm", "F#m", "G", "D/F#", "Em7", "E7", "Asus", "A"]
CH = {  # bass (piano), cello floor, waltz triad, slow arpeggio (low, mid, high)
    "D": ("D3", "D2", ["F#3", "A3", "D4"], ["D3", "A3", "F#4"]),
    "F#m": ("F#2", "F#2", ["F#3", "A3", "C#4"], ["F#2", "A3", "C#4"]),
    "G": ("G2", "G2", ["G3", "B3", "D4"], ["G2", "B3", "D4"]),
    "A": ("A2", "A2", ["A3", "C#4", "E4"], ["A2", "E3", "C#4"]),
    "Asus": ("A2", "A2", ["A3", "D4", "E4"], ["A2", "E3", "D4"]),
    "Bm": ("B2", "B2", ["F#3", "B3", "D4"], ["B2", "F#3", "D4"]),
    "Em7": ("E3", "E2", ["G3", "B3", "D4"], ["E3", "G3", "D4"]),
    "Gm6": ("G2", "G2", ["G3", "A#3", "E4"], ["G2", "A#3", "D4"]),
    "D/F#": ("F#2", "F#2", ["A3", "D4", "F#4"], ["F#2", "A3", "D4"]),
    "E": ("E3", "E2", ["G#3", "B3", "E4"], ["E3", "G#3", "B3"]),
    "E7": ("E3", "E2", ["G#3", "B3", "D4"], ["E3", "G#3", "D4"]),
}


ALT = {"D": "A2", "F#m": "C#3", "G": "D3", "A": "E3", "Bm": "F#2", "Em7": "B2", "Gm6": "D3", "D/F#": "A2",
       "Asus": "E3", "E": "B2", "E7": "B2"}


PZ = "pz"
REACH = (4, 12, 14)
CELLO_LINE = ["D4", "C#4", "B3", "A#3", "B3", "A3", "G3", "F#3"]  # the watcher's one changed note: B falls to B-flat


class Pat:
    """one section's pattern: track -> list of note tokens"""

    def __init__(self, steps):
        self.steps = steps
        self.t = {}

    def add(self, track, step, note, ln, vel=None, art=None):
        s = f"{step:g}:{note}:{ln:g}"
        if art:
            s += "/" + art
        if vel is not None:
            s += f":{max(0.05, min(1.0, vel)):.2f}"
        self.t.setdefault(track, []).append((step, s))

    def out(self):
        d = {"bars": -(-int(self.steps) // 16)}
        for k, v in self.t.items():
            d[k] = " ".join(s for _, s in sorted(v, key=lambda x: x[0]))
        return d


def melody(p, track, bars, q=4, start=0, octv=0, vel=0.7, first=1, last=None, len_k=1.0, art=None, accent=0.08,
           maxlen=None, velf=None, hes=0.0):
    """lay bars[first-1:last] of a tune; q = steps per quarter; start = step of bar `first`"""
    last = last or len(bars)
    for bi in range(first - 1, last):
        pos = 0.0
        for j, (n, beats) in enumerate(bars[bi]):
            st = start + ((bi - first + 1) * 3 + pos) * q
            ln = beats * q * len_k
            if hes and j == 0 and (bi + 1) in REACH:  # the reach: the finger arrives a little late on the high note
                st += hes; ln -= hes
            if maxlen:
                ln = min(ln, maxlen)
            v = vel + (accent if pos == 0 else 0) - (0.05 if beats < 1 else 0)
            if velf:
                v *= velf(bi + 1)
            a = art(bi, j, beats) if callable(art) else art
            p.add(track, st, tr(n, 12 * octv), ln, v, a)
            pos += beats


def waltz(p, harm, q=4, start=0, vel=0.55, piano="piano", bass="floor", guitar=None, bars=None, pah=True, gv=0.5,
          oom=True, per=1):
    """oom-pah-pah: bass on 1, staccato triads on 2 and 3. per = bars each chord lasts"""
    n = len(harm) * per
    for b in range(n):
        if bars and (b + 1) not in bars:
            continue
        c = CH[harm[b // per]]
        st = start + b * 3 * q
        fifth = per == 2 and b % 2 == 1
        if oom and piano:
            p.add(piano, st, ALT[harm[b // per]] if fifth else c[0], q * 1.6, vel + (0.0 if fifth else 0.08))
        if bass:
            p.add(bass, st, c[1], q * 2, vel + 0.15)
        if pah and piano:
            for k, bt in enumerate((1, 2)):
                for nn in c[2]:
                    p.add(piano, st + bt * q, nn, q * 0.45, vel - 0.10 - 0.05 * k)
        if guitar:
            for k, bt in enumerate((1, 2)):
                for nn in (c[2][1], c[2][2], tr(c[2][0], 12)):
                    p.add(guitar, st + bt * q, nn, q * 0.7, gv - 0.06 * k)


def arp(p, harm, q=8, start=0, vel=0.5, track="pianoM", bars=None, sparse=False):
    """the watcher's left hand: eighths (the old waltz pulse), low note held"""
    for b, h in enumerate(harm):
        if bars and (b + 1) not in bars:
            continue
        lo, mid, hi = CH[h][3]
        st = start + b * 3 * q
        p.add(track, st, lo, 3 * q, vel + 0.06)
        if sparse == "waltz":  # the game's own oom-pah-pah at half speed, held instead of tapped
            for k, bt in enumerate((1, 2)):
                for nn in CH[h][2]:
                    p.add(track, st + bt * q, nn, q * 0.9, vel - 0.12 - 0.04 * k)
            continue
        if sparse:
            p.add(track, st + 2 * q, mid, q, vel - 0.12)
            continue
        for k, nn in enumerate((mid, hi, mid, hi, mid)):
            p.add(track, st + (k + 1) * q / 2, nn, q * 1.2, vel - 0.08 - 0.02 * (k % 2))


def pickup(p, track, at, octv=1, vel=0.6, q=4):
    """'a-gain': A B on the two beats before `at`"""
    p.add(track, at - 2 * q, tr("A4", 12 * octv), q, vel)
    p.add(track, at - q, tr("B4", 12 * octv), q, vel + 0.08)


# ---------------------------------------------------------------- tracks
tracks = {
    "glock": {"inst": {"type": "glockenspiel", "hardness": 0.26, "ring": 5, "decay": 0.3}, "gain_db": 2.5, "pan": 0.18,
              "humanize_ms": 13, "vel_jitter": 0.14, "send_reverb": 0.15,
              "fx": [{"type": "highshelf", "hz": 6500, "gain_db": -1.5}]},
    "celesta": {"inst": {"type": "celesta", "hammer": 0.8, "pedal": True, "decay": 0.6}, "gain_db": -1, "pan": -0.22,
                "humanize_ms": 10, "vel_jitter": 0.1, "send_reverb": 0.3},
    "far": {"inst": {"type": "celesta", "hammer": 0.4, "pedal": True, "decay": 0.5}, "gain_db": -2, "pan": 0.3,
            "humanize_ms": 12, "vel_jitter": 0.12, "send_reverb": 0.75, "reverb_predelay_ms": 20,
            "fx": [{"type": "highshelf", "hz": 4500, "gain_db": 5}]},
    "piano": {"inst": {"type": "piano", "felt": 0.3, "release": 0.3}, "gain_db": -1, "humanize_ms": 9, "vel_jitter": 0.07,
              "send_reverb": 0.12, "width": 0.3,
              "fx": [{"type": "lowshelf", "hz": 170, "gain_db": 2}, {"type": "eq", "hz": 4200, "gain_db": 3, "q": 0.8},
                     {"type": "highshelf", "hz": 6000, "gain_db": 5}]},
    "pianoM": {"inst": {"type": "piano", "felt": 0.62, "release": 0.6}, "gain_db": -3.5, "humanize_ms": 11,
               "vel_jitter": 0.08, "send_reverb": 0.08, "width": 0.4,
               "fx": [{"type": "lowshelf", "hz": 170, "gain_db": 2}, {"type": "eq", "hz": 4200, "gain_db": 4, "q": 0.7},
                      {"type": "highshelf", "hz": 7000, "gain_db": 4}]},
    "floor": {"inst": {"type": "cello", "pizz": True}, "gain_db": 4.5, "pan": 0.1, "humanize_ms": 8, "vel_jitter": 0.06,
              "send_reverb": 0.15, "fx": [{"type": "lowshelf", "hz": 200, "gain_db": 2.5}]},
    "vpizz": {"inst": {"type": "violin", "dark": 0.15}, "gain_db": 3, "pan": -0.4, "humanize_ms": 9, "vel_jitter": 0.08,
              "send_reverb": 0.22, "fx": [{"type": "highshelf", "hz": 5000, "gain_db": 5}]},
    "violin": {"inst": {"type": "violin", "vibrato": 0.14, "vib_rate": 5.4, "intonation": 0.4, "bow_noise": 0.2, "dark": 0.45, "bow_pos": 0.17,
                                 "pressure": 0.58, "vib_delay": 0.2},
               "gain_db": -3, "pan": -0.3, "humanize_ms": 6, "send_reverb": 0.3, "legato": 1.0},
    "guitar": {"inst": {"type": "acguitar", "bright": 0.7, "scrape": 0.45}, "gain_db": 6, "pan": 0.42, "humanize_ms": 10, "vel_jitter": 0.1,
               "send_reverb": 0.14, "fx": [{"type": "hpf", "hz": 120}, {"type": "eq", "hz": 3800, "gain_db": 3, "q": 0.8},
                      {"type": "highshelf", "hz": 5000, "gain_db": 6}]},
    "cello": {"inst": {"type": "cello"}, "gain_db": -5, "pan": 0.25, "humanize_ms": 5, "send_reverb": 0.3,
              "legato": 1.0, "fx": [{"type": "highshelf", "hz": 4000, "gain_db": 3}]},
    "vlns": {"inst": {"type": "strings_section", "section": "violins", "air": 0.8}, "gain_db": 9, "send_reverb": 0.5, "legato": 1.0,
             "fx": [{"type": "highshelf", "hz": 4000, "gain_db": 3}]},
    "vlas": {"inst": {"type": "strings_section", "section": "violas", "air": 0.8}, "gain_db": 7, "send_reverb": 0.5, "legato": 1.0,
             "fx": [{"type": "highshelf", "hz": 4000, "gain_db": 3}]},
    "celli": {"inst": {"type": "strings_section", "section": "celli"}, "gain_db": 5, "send_reverb": 0.42,
              "legato": 1.0},
}

patterns, arrangement = {}, []


def section(name, p, bpm=None, **kw):
    patterns[name] = p.out()
    s = {"name": name, "bars": patterns[name]["bars"], "play": [name]}
    if bpm is not None:
        s["bpm"] = bpm
    s.update(kw)
    arrangement.append(s)


# ---------------------------------------------------------------- the form
# 0. "again": two notes and the game is already going
p = Pat(16)
pickup(p, "glock", 16, vel=0.62)
section("again", p, 172)

# 1. A: the glockenspiel, one finger; the waltz under it
p = Pat(192)
melody(p, "glock", CHILD, octv=1, vel=0.66, hes=0.55)
waltz(p, H_A, vel=0.52, bars=set(range(1, 9)))
waltz(p, H_A, vel=0.52, bars=set(range(9, 17)), guitar="guitar", gv=0.4)
for b in range(9, 17):  # halfway through, a second pair of feet: a plucked hop on the last beat of each bar
    top = CH[H_A[b - 1]][2][2]
    p.add("vpizz", (b - 1) * 12 + 8, tr(top, 12), 2, 0.5 + 0.03 * (b % 2), PZ)
pickup(p, "glock", 192, vel=0.6)
section("A1", p, 172)


slur = lambda bi, j, beats: "s" if j > 0 else None


def echo(p, bars_from, at_bar, track="glock", octv=1, vel=0.66, q=4):
    """the glockenspiel copies the bar before, a bar late"""
    pos = 0
    for n, beats in CHILD[bars_from - 1]:
        p.add(track, ((at_bar - 1) * 3 + pos) * q, tr(n, 12 * octv), beats * q, vel)
        pos += beats


def A2():
    p = Pat(192)
    melody(p, "celesta", CHILD, vel=0.68, hes=0.45)
    melody(p, "vpizz", CHILD, vel=0.6, art=PZ, maxlen=4)
    for b in (4, 8, 12):
        echo(p, b - 1, b)
    waltz(p, H_A, vel=0.52, guitar="guitar")
    section("A2", p, 172)


def B():
    p = Pat(192)
    melody(p, "celesta", BRUN, vel=0.66)
    melody(p, "piano", BRUN, octv=1, vel=0.5, len_k=0.8)
    for b in (1, 3, 5, 9, 11, 13, 14):
        melody(p, "vpizz", BRUN, first=b, last=b, start=(b - 1) * 12, vel=0.6, art=PZ, maxlen=4)
    for b, n, ln in ((1, "B5", 4), (3, "A5", 4), (5, "B5", 4), (6, "G#6", 8), (9, "D6", 4), (11, "B5", 4)):
        p.add("glock", (b - 1) * 12, n, ln, 0.72)
    waltz(p, H_B, vel=0.54, guitar="guitar", bars=set(range(1, 15)))
    waltz(p, H_B, vel=0.5, bars={15}, bass="floor")
    p.add("piano", 180, "A2", 10, 0.5); p.add("floor", 180, "A2", 8, 0.6)
    pickup(p, "glock", 192, vel=0.62)
    section("B", p, [172, 178])


def A3():
    p = Pat(144)
    melody(p, "violin", CHILD, last=12, vel=0.66, art=slur)
    for b in (4, 8):
        echo(p, b - 1, b)
    melody(p, "celesta", CHILD, first=9, last=12, start=96, octv=1, vel=0.5)
    waltz(p, H_A[:12], vel=0.54, guitar="guitar")
    section("A3", p, 175)
    # the last phrase slows: the dancers stop one by one, the violin finishes
    p = Pat(48)
    melody(p, "violin", CHILD, first=13, last=16, vel=0.62, art=slur)
    waltz(p, H_A[12:], vel=0.46, bars={1, 2}, bass=None)
    p.add("floor", 0, "G2", 8, 0.6)
    p.add("piano", 24, "A2", 10, 0.48)
    for n in ("D3", "A3", "D4", "F#4"):
        p.add("piano", 36, n, 14, 0.42)
    p.add("floor", 36, "D2", 10, 0.5)
    section("turn", p, [174, 88])


def M1():
    # the watcher: the piano alone at half speed, the gaps filled
    p = Pat(192)
    melody(p, "pianoM", ADULT, q=8, last=8, vel=0.62, len_k=1.15, hes=1.0)
    arp(p, H_AD[:8], vel=0.46, sparse="waltz")
    section("M1", p, [144, 160])


def M2():
    # the same, with a cello carrying the one changed note, and the game still running far off at its own speed
    p = Pat(192)
    melody(p, "pianoM", ADULT, q=8, first=9, last=16, vel=0.62, len_k=1.15, hes=1.0)
    h = H_AD[8:15] + ["Bm"]
    arp(p, h, vel=0.46)
    for i, n in enumerate(CELLO_LINE):
        p.add("cello", i * 24, n, 24, 0.5 + (0.12 if i == 3 else 0), "swell" if i in (0, 3) else "s")
    melody(p, "far", CHILD, octv=1, vel=0.5, hes=0.55)
    section("M2", p, 160)


def M3():
    # the hill again, slowly; the strings bloom behind
    p = Pat(192)
    melody(p, "pianoM", BRUN, q=8, last=8, vel=0.6, len_k=1.15)
    h = H_B[:8]
    arp(p, h, vel=0.45)
    inner = [("B3", "D4"), ("B3", "D4"), ("A3", "D4"), ("A3", "D4"), ("B3", "D4"), ("G#3", "B3"), ("A3", "D4"), ("A3", "C#4")]
    for i, (a, b) in enumerate(inner):
        v = 0.3 + 0.035 * i
        p.add("vlas", i * 24, a, 24, v); p.add("vlas", i * 24, b, 24, v)
        p.add("celli", i * 24, CH[h[i]][1], 24, v)
    p.add("glock", 5 * 24, "G#6", 12, 0.45)
    section("M3", p, [160, 166], auto={"vlas": {"gain_db": [-14, -7]}, "celli": {"gain_db": [-14, -8]}})


def M4():
    # the game alone, far, over a held dominant; then: again
    p = Pat(96)
    melody(p, "far", CHILD, last=8, octv=1, vel=0.55)
    p.add("vlas", 0, "A3", 92, 0.34, "dim"); p.add("vlas", 0, "E4", 92, 0.34, "dim")
    p.add("pianoM", 0, "A2", 24, 0.4)
    pickup(p, "glock", 96, vel=0.6); pickup(p, "celesta", 96, octv=0, vel=0.6)
    section("M4", p, [166, 172], auto={"vlas": {"gain_db": [-7, -12]}, "celli": {"gain_db": -8}})


def T():
    # the one swell: the dance at full speed, and the watcher's slow tune over it on the strings. two clocks.
    p = Pat(384)
    melody(p, "glock", CHILD, octv=1, vel=0.7, hes=0.5)
    melody(p, "glock", CHILD, octv=1, vel=0.7, last=4, start=192, hes=0.5)
    melody(p, "glock", CHILD, octv=1, vel=0.72, first=9, start=192 + 96, hes=0.5)
    melody(p, "celesta", CHILD, vel=0.66)
    melody(p, "celesta", CHILD, vel=0.66, start=192, velf=lambda b: 0.8 if 5 <= b <= 8 else 1)
    waltz(p, H_AD[:8], vel=0.48, guitar="guitar", per=2, gv=0.44)
    waltz(p, H_AD[8:], vel=0.56, guitar="guitar", per=2, start=192)
    longs = lambda bi, j, beats: "swell" if beats >= 3 else None
    melody(p, "vlas", ADULT, q=8, octv=-1, vel=0.5, art=longs, velf=lambda b: 0.85 + 0.02 * b)
    melody(p, "cello", ADULT, q=8, octv=-1, vel=0.55, art=slur, last=8)
    for i, n in enumerate(CELLO_LINE):  # second half: its own line from M2; the B-flat again, inside the swell
        p.add("cello", 192 + i * 24, n, 24, 0.62 + (0.14 if i == 3 else 0), "swell" if i in (0, 3) else "s")
    p.add("vlns", 168, "A4", 24, 0.4, "cresc")
    melody(p, "vlns", ADULT, q=8, first=9, start=192, vel=0.62, art=longs, velf=lambda b: 0.9 + 0.025 * (b - 8))
    # the last phrase: half the violins take the octave above; the top A of the tune is the top of the track
    melody(p, "vlns", ADULT, q=8, first=13, start=192 + 96, octv=1, vel=0.6, art=longs)
    for i, hh in enumerate(H_AD):
        v = 0.36 + 0.02 * i
        p.add("celli", i * 24, CH[hh][1], 24, v)
        if i >= 8:
            p.add("celli", i * 24, tr(ALT[hh], 0), 24, v - 0.05)
    section("T", p, [172, 176], auto={"vlas": {"gain_db": [-5, 0]}, "celli": {"gain_db": [-6, 0]},
                                      "vlns": {"gain_db": [-4, 0]}, "cello": {"gain_db": [-3, 0]}})


def G():
    # afterglow: the dancers leave; the piano picks up the run they drop
    p = Pat(48)
    melody(p, "piano", BRUN, first=9, last=12, vel=0.62)
    waltz(p, H_B[8:12], vel=0.5, guitar="guitar", gv=0.42)
    p.add("glock", 0, "D6", 4, 0.55); p.add("glock", 24, "B5", 4, 0.5)
    section("G1", p, [174, 156])
    p = Pat(48)
    melody(p, "piano", BRUN, first=13, last=16, vel=0.56)
    waltz(p, H_B[12:15], vel=0.44, bass=None)
    p.add("piano", 36, "A2", 12, 0.45)
    # from the next room, at the old speed: "again" (asked; the piano will answer, the child's way)
    p.add("far", 48 - 4.6, "A5", 2.3, 0.5); p.add("far", 48 - 2.3, "B5", 4, 0.58)
    section("G2", p, [156, 96])


def C():
    # the close: the piano plays it the child's way: one finger, high, slow
    p = Pat(192)
    melody(p, "pianoM", CHILD, q=8, last=8, octv=1, vel=0.66, len_k=1.1, hes=1.5)
    arp(p, H_AD[:8], vel=0.4, sparse=True)
    p.add("far", 192 - 6.8, "A5", 3.4, 0.5); p.add("far", 192 - 3.4, "B5", 4, 0.58)  # asked again; answered again
    section("C1", p, [140, 146])
    p = Pat(144)
    melody(p, "pianoM", CHILD, q=8, first=9, last=14, octv=1, vel=0.66, len_k=1.1, hes=1.5)
    arp(p, H_AD[8:14], vel=0.4, sparse=True)
    for i, (a, b) in enumerate([("F#3", "A3"), ("F#3", "A3"), ("G3", "B3"), ("G3", "A#3"), ("G3", "B3"), ("F#3", "A3")]):
        p.add("vlas", i * 24, a, 24, 0.3); p.add("vlas", i * 24, b, 24, 0.3)
    section("C2", p, [146, 138], auto={"vlas": {"gain_db": [-14, -10]}})
    p = Pat(80)
    p.add("pianoM", 0, "E6", 16, 0.64); p.add("pianoM", 16, "B5", 8, 0.56)
    p.add("pianoM", 0, "A2", 24, 0.42); p.add("pianoM", 16, "E3", 8, 0.3)
    p.add("pianoM", 24, "D6", 30, 0.62); p.add("pianoM", 24, "D2", 30, 0.34)
    for k, n in enumerate(("D3", "A3", "F#4")):
        p.add("pianoM", 24 + k * 1.5, n, 30 - k * 1.5, 0.4)
    p.add("vlas", 0, "E3", 24, 0.28); p.add("vlas", 0, "A3", 24, 0.28)
    p.add("vlas", 24, "F#3", 40, 0.28, "dim"); p.add("vlas", 24, "A3", 40, 0.28, "dim")
    # the last "again": the child's clock has not slowed (two quarters at the old 172, written against this tempo)
    p.add("far", 50, "A5", 2.5, 0.5); p.add("far", 52.5, "B5", 4, 0.58)
    section("C3", p, [138, 104], auto={"vlas": {"gain_db": [-10, -18]}})


A2(); B(); A3(); M1(); M2(); M3(); M4(); T(); G(); C()
if MODE.startswith("part:"):  # work on a few sections only (full renders at checkpoints)
    keep = MODE[5:].split(",")
    arrangement[:] = [s for s in arrangement if s["name"] in keep]

json.dump({
    "title": "Again, Again",
    "bpm": 172, "swing": 0.5, "seed": 15,
    "tracks": tracks, "patterns": patterns, "arrangement": arrangement,
    "mix": {"reverb": {"size": 0.72, "damping": 0.3, "return_db": -5, "lpf": 9000}},
    "master": {"lufs": -15, "sat": 0.0, "tape": 0.0, "glue": False},
}, open("project.json", "w"), indent=1)
print("sections:", [(s["name"], s["bars"]) for s in arrangement])
