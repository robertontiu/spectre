"""For each expected melody note: is there a MIDI note of that exact pitch starting within 0.3 beats of where it
should (grid re-anchored on each matched note, so slow drift in the played MIDI doesn't accumulate)?
python3 -I check_midi.py file.mid track"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from midi_dump import parse, nn
from melody import stanza
fmt, div, tracks = parse(sys.argv[1])
notes = [(e[1] / div, e[3]) for e in tracks[int(sys.argv[2])] if e[0] == 'note']
seq = stanza(0)
anchor_exp, anchor_mid = 0.0, 0.966   # pickup position in the MIDI
pos, ok, bad = 0.0, 0, []
for p, d in seq:
    if p is not None:
        want = anchor_mid + (pos - anchor_exp)
        c = [s for s, q in notes if q == p and abs(s - want) < 0.3]
        if c:
            ok += 1; s = min(c, key=lambda s: abs(s - want)); anchor_exp, anchor_mid = pos, s
        else:
            bad.append((pos, nn(p), want))
    pos += d
print(f'{ok}/{ok + len(bad)} melody notes found in the MIDI at the expected pitch and time')
for b in bad: print('  missing', b)
