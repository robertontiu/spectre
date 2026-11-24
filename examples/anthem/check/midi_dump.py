"""Minimal SMF parser: dump notes per track with beat positions. Usage: python3 -I midi_dump.py file.mid"""
import sys, struct

NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def nn(p):
    return f"{NAMES[p % 12]}{p // 12 - 1}"


def vlq(d, i):
    v = 0
    while True:
        b = d[i]; i += 1
        v = (v << 7) | (b & 0x7f)
        if not b & 0x80:
            return v, i


def parse(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'MThd'
    fmt, ntr, div = struct.unpack('>HHH', d[8:14])
    i = 14
    tracks = []
    for _ in range(ntr):
        assert d[i:i + 4] == b'MTrk'
        ln = struct.unpack('>I', d[i + 4:i + 8])[0]
        t = d[i + 8:i + 8 + ln]; i += 8 + ln
        j = 0; tick = 0; rs = None; ev = []; on = {}
        while j < len(t):
            dt, j = vlq(t, j); tick += dt
            st = t[j]
            if st == 0xff:
                typ = t[j + 1]; ln2, j = vlq(t, j + 2); data = t[j:j + ln2]; j += ln2
                ev.append(('meta', tick, typ, data)); continue
            if st in (0xf0, 0xf7):
                ln2, j = vlq(t, j + 1); j += ln2; continue
            if st & 0x80:
                rs = st; j += 1
            st = rs
            hi = st & 0xf0
            if hi in (0xc0, 0xd0):
                ev.append(('ctl', tick, st, t[j])); j += 1; continue
            a, b = t[j], t[j + 1]; j += 2
            ch = st & 0x0f
            if hi == 0x90 and b > 0:
                on[(ch, a)] = (tick, b)
            elif hi in (0x80, 0x90):
                if (ch, a) in on:
                    s, v = on.pop((ch, a)); ev.append(('note', s, tick - s, a, ch, v))
        tracks.append(ev)
    return fmt, div, tracks


if __name__ == '__main__':
    fmt, div, tracks = parse(sys.argv[1])
    print('format', fmt, 'division', div)
    for k, ev in enumerate(tracks):
        notes = sorted([e for e in ev if e[0] == 'note'], key=lambda e: (e[1], -e[3]))
        print(f'--- track {k}: {len(notes)} notes')
        for e in ev:
            if e[0] == 'meta' and e[2] in (0x03, 0x51, 0x58, 0x59, 0x01, 0x02):
                if e[2] == 0x51:
                    us = int.from_bytes(e[3], 'big'); print('  tempo @', e[1] / div, round(60e6 / us, 1), 'bpm')
                elif e[2] == 0x58:
                    print('  timesig @', e[1] / div, e[3][0], '/', 2 ** e[3][1])
                elif e[2] == 0x59:
                    print('  keysig @', e[1] / div, int.from_bytes(e[3][:1], 'big', signed=True), 'minor' if e[3][1] else 'major')
                else:
                    print('  text', e[3].decode('latin1')[:120])
            if e[0] == 'ctl' and (e[2] & 0xf0) == 0xc0:
                print('  program ch', e[2] & 15, e[3])
        if len(sys.argv) > 2 and str(k) not in sys.argv[2].split(','):
            continue
        for e in notes:
            print(f'  beat {e[1] / div:8.3f} len {e[2] / div:6.3f} {nn(e[3]):4s} ch{e[4]} v{e[5]}')
