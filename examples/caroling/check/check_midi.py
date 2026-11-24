"""Compare the melody blocks (melodies.py) with the soprano line of the Mutopia Project MIDI files (public domain):
  carol.mid      https://www.mutopiaproject.org/ftp/WillisRS/carol/carol.mid
  first_noel.mid https://www.mutopiaproject.org/ftp/Traditional/first_noel/first_noel.mid
kept outside the repo in ~/.cache/spectre/refs/carols/. No external MIDI library.
Usage: python3 examples/caroling/check/check_midi.py"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import melodies as M

NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def midi_of(n):
    p = NAMES[n[0]] + n[1:-1].count("#") - n[1:-1].count("b")
    return 12 * (int(n[-1]) + 1) + p

def read_midi(path):
    d = open(path, "rb").read()
    fmt, ntrk, div = struct.unpack(">HHH", d[8:14])
    pos, tracks = 14, []
    for _ in range(ntrk):
        ln = struct.unpack(">I", d[pos + 4:pos + 8])[0]
        tr, i, t, run, on, notes = d[pos + 8:pos + 8 + ln], 0, 0, None, {}, []
        while i < len(tr):
            v = 0
            while True:
                b = tr[i]; i += 1; v = (v << 7) | (b & 127)
                if b < 128: break
            t += v
            st = tr[i]
            if st == 0xFF:
                ln2 = 0; i += 2
                while True:
                    b = tr[i]; i += 1; ln2 = (ln2 << 7) | (b & 127)
                    if b < 128: break
                i += ln2; continue
            if st in (0xF0, 0xF7):
                i += 1; ln2 = tr[i]; i += 1 + ln2; continue
            if st >= 128: run = st; i += 1
            kind = run & 0xF0
            if kind in (0x80, 0x90):
                n, vel = tr[i], tr[i + 1]; i += 2
                if kind == 0x90 and vel > 0: on[n] = t
                elif n in on: notes.append((on.pop(n) / div, n, t / div))
            elif kind in (0xC0, 0xD0): i += 1
            else: i += 2
        tracks.append(sorted(notes))
        pos += 8 + ln
    return [t for t in tracks if t]

def block(pickup, body, pickup_steps=16):
    out = []
    for s, steps0 in ((pickup, 0), (body, pickup_steps)):
        for tok in s.split():
            st, n, ln = tok.split(":")[:3]
            out.append(((float(st) + steps0) / 4.0, midi_of(n), float(ln.rstrip("~!.")) / 4.0))
    return out

def compare(name, ours, midi_path, shift, merge_ties=False):
    tr = read_midi(midi_path)[0]  # soprano and alto share the first voice track (LilyPond partcombine)
    by_on = {}
    for on, n, off in tr:
        by_on.setdefault(round(on, 3), []).append((n, off))
    top = []  # the soprano: the highest note at each onset, unless a higher note is still sounding (alto moving)
    for on in sorted(by_on):
        n, off = max(by_on[on])
        if top and top[-1][2] > on + 1e-6 and top[-1][1] > n:
            continue
        top.append((on, n, off))
    if merge_ties:  # LilyPond's "c4. ( c4 )" is a slur on one pitch, which the MIDI re-strikes; the scores tie it
        t0 = top[0][0]
        ours_on = {round(o - ours[0][0], 3) for o, _, _ in ours}
        merged = []
        for on, n, off in top:
            if (merged and merged[-1][1] == n and abs(merged[-1][2] - on) < 1e-6
                    and round(on - t0, 3) not in ours_on):
                merged[-1] = (merged[-1][0], n, off)
                print(f"  tie merged: MIDI {n} at beat {on - t0:.2f} (re-struck slur, tied in the scores)")
                continue
            merged.append((on, n, off))
        top = merged
    t0 = top[0][0]
    ref = [(on - t0, n + shift) for on, n, off in top]
    o0 = ours[0][0]
    mine = [(on - o0, n) for on, n, _ in ours]
    ok = 0
    print(f"\n{name}: ours {len(mine)} notes, MIDI soprano {len(ref)} notes")
    for k, (a, b) in enumerate(zip(mine, ref)):
        same = abs(a[0] - b[0]) < 0.01 and a[1] == b[1]
        ok += same
        if not same:
            print(f"  note {k + 1}: ours beat {a[0]:.2f} midi {a[1]}  |  MIDI beat {b[0]:.2f} midi {b[1]}")
    print(f"  {ok}/{max(len(mine), len(ref))} notes at the same pitch and onset")

if __name__ == "__main__":
    ref = os.path.expanduser("~/.cache/spectre/refs/carols")
    compare("CAROL", block(M.CAROL_PICKUP, M.CAROL), os.path.join(ref, "carol.mid"), 0, merge_ties=True)
    compare("THE FIRST NOWELL", block(M.NOWELL_PICKUP, M.NOWELL), os.path.join(ref, "first_noel.mid"), 0)
