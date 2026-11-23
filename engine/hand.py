"""The hand: turns the producer's musical intentions into timed, humanized events.

It handles swing, pocket (push/drag), micro-timing, velocity phrasing, rolls,
chord voicing with voice leading, strums, arps and fills. The mind writes what
it wants; the hand decides exactly when and how hard.
"""
import re
import numpy as np

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_to_midi(s):
    m = re.fullmatch(r"([A-Ga-g])([#b]?)(-?\d)", s.strip())
    if not m:
        raise ValueError(f"bad note '{s}' (use like F1, Ab3, C#4)")
    pc = NOTE_PC[m.group(1).upper()] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)
    return 12 * (int(m.group(3)) + 1) + pc


def midi_to_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


QUALITIES = {
    "": [0, 4, 7], "maj": [0, 4, 7], "m": [0, 3, 7], "min": [0, 3, 7], "dim": [0, 3, 6], "aug": [0, 4, 8],
    "sus2": [0, 2, 7], "sus4": [0, 5, 7], "5": [0, 7], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9],
    "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "m7b5": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9], "mmaj7": [0, 3, 7, 11], "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14],
    "9": [0, 4, 10, 14], "maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14], "m11": [0, 3, 10, 14, 17],
    "11": [0, 7, 10, 14, 17], "13": [0, 4, 10, 14, 21], "maj13": [0, 4, 11, 14, 21], "7b9": [0, 4, 10, 13],
    "7#9": [0, 4, 10, 15], "7sus4": [0, 5, 7, 10], "m7b9": [0, 3, 10, 13], "6/9": [0, 4, 9, 14],
    "maj7#11": [0, 4, 11, 18], "7b13": [0, 4, 10, 20], "m(maj9)": [0, 3, 11, 14],
}


def parse_chord(sym):
    m = re.fullmatch(r"([A-G][#b]?)(.*?)(?:/([A-G][#b]?))?", sym.strip())
    if not m:
        raise ValueError(f"bad chord '{sym}'")
    root = NOTE_PC[m.group(1)[0]] + (1 if "#" in m.group(1) else -1 if "b" in m.group(1)[1:] else 0)
    q = m.group(2)
    if q not in QUALITIES:
        raise ValueError(f"unknown chord quality '{q}' in '{sym}'. Known: {sorted(QUALITIES)}")
    bass = None
    if m.group(3):
        b = m.group(3)
        bass = NOTE_PC[b[0]] + (1 if "#" in b else -1 if "b" in b[1:] else 0)
    return root % 12, QUALITIES[q], bass


def voice_chord(root, ivs, center, prev, style, bass_pc=None):
    """Return midi notes. Voice-leads from prev; keeps the upper structure near center."""
    upper_ivs = ivs[1:] if style in ("spread", "keys") and len(ivs) >= 3 else ivs
    pcs = [(root + i) % 12 for i in upper_ivs]
    cands = []
    for inv in range(len(pcs)):
        order = pcs[inv:] + pcs[:inv]
        for base_oct in range(2, 7):
            notes, cur = [], None
            for pc in order:
                n = 12 * base_oct + pc if cur is None else cur + ((pc - cur) % 12 or 12)
                notes.append(n)
                cur = n
            cands.append(notes)

    def cost(v):
        c = abs(np.mean(v) - center) * 0.6
        if prev:
            pu = sorted(prev)[-len(v):] if len(prev) >= len(v) else sorted(prev)
            c += sum(abs(a - b) for a, b in zip(sorted(v), pu)) / max(len(v), 1)
        if max(v) - min(v) > 16:
            c += 6
        return c
    best = min(cands, key=cost)
    if style in ("spread", "keys"):
        lb = (bass_pc if bass_pc is not None else root)
        low = 12 * ((center - 14) // 12) + lb
        while low > min(best) - 7:
            low -= 12
        while low < center - 30:
            low += 12
        best = [low] + best
    elif bass_pc is not None:
        low = min(best) - ((min(best) - bass_pc) % 12 or 12)
        best = [low] + best
    return sorted(best)


VEL_CHARS = {"X": 1.0, "x": 0.82, "o": 0.45, "g": 0.3}
ROLL_CHARS = {"r": 2, "t": 3, "q": 4, "s": 6, "z": 8}


class Hand:
    def __init__(self, bpm, swing, seed):
        self.bpm = bpm
        self.swing = swing
        self.beat = 60.0 / bpm
        self.six = self.beat / 4
        self.rng = np.random.default_rng(seed)

    def bar_sec(self):
        return self.beat * 4

    def step_time(self, step16, swing=None):
        """step16: position in 16ths (float). Applies swing to odd 16ths."""
        s = self.swing if swing is None else swing
        base = step16 * self.six
        whole = int(np.floor(step16 + 1e-6))
        frac = step16 - whole
        if whole % 2 == 1 and frac < 1e-6:
            base += (2 * s - 1) * self.six
        return base

    def humanize(self, t, tr):
        t += tr.get("push_ms", 0) / 1000.0
        h = tr.get("humanize_ms", 4) / 1000.0
        if h > 0:
            t += float(np.clip(self.rng.normal(0, h), -2.5 * h, 2.5 * h))
        return t

    def vel(self, v, tr, pos16=None):
        j = tr.get("vel_jitter", 0.06)
        v = v * (1 + self.rng.normal(0, j))
        dyn = tr.get("dyn")
        if dyn and pos16 is not None:
            v *= dyn[int(pos16) % len(dyn)]
        return float(np.clip(v, 0.03, 1.0))

    # ---------------- drums
    def drum_events(self, steps, bars, t0, tr):
        s = re.sub(r"[\s|]", "", steps)
        if len(s) % bars != 0:
            raise ValueError(f"step string length {len(s)} not divisible by bars={bars}: '{steps}'")
        grid = len(s) // bars
        unit16 = 16.0 / grid  # how many 16ths one step spans
        swing = tr.get("swing", self.swing) if grid in (8, 16, 32) else 0.5
        rp = tr.get("roll_pitch", 0)
        ev = []
        for i, ch in enumerate(s):
            if ch in ".-_":
                continue
            pos16 = i * unit16
            if ch in VEL_CHARS or ch.isdigit():
                v = VEL_CHARS.get(ch, (int(ch) / 9.0) if ch.isdigit() else 0.8)
                t = self.step_time(pos16, swing) if grid in (8, 16) else pos16 * self.six
                ev.append(dict(t=t0 + self.humanize(t, tr), vel=self.vel(v, tr, pos16 if grid == 16 else None), ps=0.0))
            elif ch.lower() in ROLL_CHARS:
                k = ROLL_CHARS[ch.lower()]
                ramp = ch.isupper()  # uppercase = crescendo roll
                base = self.step_time(pos16, swing) if grid in (8, 16) else pos16 * self.six
                for j in range(k):
                    tt = base + j * unit16 * self.six / k
                    vv = (0.45 + 0.5 * (j + 1) / k) if ramp else 0.72 - 0.08 * (j % 2)
                    ps = rp * j / max(k - 1, 1)
                    ev.append(dict(t=t0 + self.humanize(tt, {**tr, "humanize_ms": tr.get("humanize_ms", 4) * 0.4}),
                                   vel=self.vel(vv, tr), ps=ps))
            else:
                raise ValueError(f"unknown step char '{ch}' in '{steps}'")
        return ev

    # ---------------- notes (808, bass, lead, melody)
    def note_events(self, spec, t0, tr):
        ev = []
        for tok in spec.split():
            parts = tok.split(":")
            if len(parts) < 3:
                raise ValueError(f"note token '{tok}' must be step:note:len[~][!|.]")
            step = float(parts[0])
            lenstr = parts[2]
            glide = "~" in lenstr
            accent = 1.15 if "!" in lenstr else (0.6 if lenstr.endswith(".") else 1.0)
            ln = float(re.sub(r"[~!.]+$", "", lenstr.replace("~", "")))
            v = 0.85 * accent
            if len(parts) > 3:
                v = float(parts[3])
            t = self.humanize(self.step_time(step, tr.get("swing", self.swing)), tr)
            ev.append(dict(t=t0 + t, midi=note_to_midi(parts[1]), dur=ln * self.six * tr.get("legato", 0.95),
                           vel=self.vel(v, tr), glide=glide))
        return ev

    # ---------------- chords
    def chord_events(self, spec, bars, t0, tr, state):
        style = spec.get("style", "sustain")
        voicing = spec.get("voicing", "keys")
        center = note_to_midi(spec.get("register", "C4"))
        toks = spec["chords"].split()
        pos = 0.0
        ev = []
        rhythm = spec.get("rhythm")
        for tok in toks:
            if ":" in tok:
                sym, ln = tok.rsplit(":", 1)
                ln = float(ln)
            else:
                sym, ln = tok, 16.0
            if sym in ("-", "N.C."):
                pos += ln
                continue
            root, ivs, bass = parse_chord(sym)
            notes = voice_chord(root, ivs, center, state.get("prev"), voicing, bass)
            state["prev"] = notes
            vel0 = spec.get("vel", 0.7)
            if style in ("sustain", "strum"):
                hits = [(pos, ln)]
            elif style == "stabs":
                r = re.sub(r"[\s|]", "", rhythm or "x...x...x...x...")
                hits = []
                for b in range(int(np.ceil(ln / len(r)))):
                    for i, ch in enumerate(r):
                        p = pos + b * len(r) + i
                        if ch != "." and p < pos + ln:
                            hits.append((p, spec.get("stab_len", 2)))
            elif style == "arp":
                rate = spec.get("rate", 2)  # in 16ths
                pat = spec.get("pattern", "up")
                seq = list(notes[1:] if voicing in ("keys", "spread") else notes)
                seq = seq + [n + 12 for n in seq] if spec.get("octaves", 1) > 1 else seq
                if pat == "down":
                    seq = seq[::-1]
                elif pat == "updown":
                    seq = seq + seq[-2:0:-1]
                k = 0
                p = pos
                if voicing in ("keys", "spread"):
                    t = self.humanize(self.step_time(pos), tr)
                    ev.append(dict(t=t0 + t, midi=notes[0], dur=ln * self.six, vel=self.vel(vel0 * 0.9, tr)))
                while p < pos + ln - 1e-6:
                    n = seq[k % len(seq)] if pat != "random" else seq[self.rng.integers(len(seq))]
                    t = self.humanize(self.step_time(p), tr)
                    ev.append(dict(t=t0 + t, midi=n, dur=rate * self.six * 1.6, vel=self.vel(vel0 * (1.0 if k % 4 == 0 else 0.82), tr)))
                    p += rate
                    k += 1
                pos += ln
                continue
            else:
                raise ValueError(f"unknown chord style '{style}'")
            for (hp_, hl) in hits:
                base = self.humanize(self.step_time(hp_), tr)
                for j, n in enumerate(notes):
                    off = 0.0
                    if style == "strum":
                        off = j * spec.get("strum_ms", 28) / 1000.0
                    else:
                        off = abs(self.rng.normal(0, 0.006))
                    v = vel0 * (1.08 if j == len(notes) - 1 else 0.95 if j == 0 else 0.86)
                    ev.append(dict(t=t0 + base + off, midi=n, dur=hl * self.six * 0.97 - off, vel=self.vel(v, tr)))
            pos += ln
        return ev
