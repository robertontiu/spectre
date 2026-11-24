"""Score-informed check of a recording against the transcribed melody, on a beat grid.
The recording's beats are tracked; the melody (pickup + a b b) is laid on them from a start beat (the one free
parameter, searched), and for every melody note the recording's CQT energy at the expected pitch is compared with its
semitone neighbours and with the other pitch classes in the melody register.
python3 -I verify_beats.py audio transpose_from_E [--stanzas 2] [--all] [--variant name]"""
import sys, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import librosa
from melody import stanza

NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
nn = lambda p: f"{NAMES[p % 12]}{p // 12 - 1}"
audio, tr = sys.argv[1], int(sys.argv[2])
nst = int(sys.argv[sys.argv.index('--stanzas') + 1]) if '--stanzas' in sys.argv else 1
sr, hop = 22050, 256
y, _ = librosa.load(audio, sr=sr, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, start_bpm=float(sys.argv[sys.argv.index('--bpm') + 1]) if '--bpm' in sys.argv else 100)
bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
# extrapolate the grid a little at both ends
per = np.median(np.diff(bt))
bt = np.concatenate([bt[0] - per * np.arange(8, 0, -1), bt, bt[-1] + per * np.arange(1, 9)])
lo_m = librosa.note_to_midi('C2')
C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz('C2'), n_bins=12 * 6, bins_per_octave=12))
fr = sr / hop
seq = []
for s in range(nst):
    if seq:
        seq = seq[:-1]  # the last rest beat of a stanza is the next stanza's pickup
    seq += stanza(tr)
if '--shuffle' in sys.argv:  # control: same rhythm, pitches shuffled
    rng = np.random.default_rng(int(sys.argv[sys.argv.index('--shuffle') + 1]))
    ps = [p for p, d in seq if p is not None]; rng.shuffle(ps); it = iter(ps)
    seq = [(None if p is None else next(it), d) for p, d in seq]
# beat positions (pickup at 0)
pos, rows = 0.0, []
for p, d in seq:
    if p is not None:
        rows.append((p, d, pos))
    pos += d
if '--seq' in sys.argv:  # notes tracked from the engine render: [midi, onset beat] (pickup at render beat 3), G minor
    import json
    tracked = json.load(open(sys.argv[sys.argv.index('--seq') + 1]))
    shift = int(sys.argv[sys.argv.index('--seq-transpose') + 1])
    on = [b - tracked[0][1] for _, b in tracked]
    one = [(q + shift, (on[k + 1] if k + 1 < len(on) else on[k] + 3) - on[k], on[k]) for k, (q, _) in enumerate(tracked)]
    rows = []
    for st in range(nst):  # the render holds pickup + a + b; lay it on each stanza's pickup, a and first b
        rows += [(p, round(d * 2) / 2, round(b * 2) / 2 + st * 120) for p, d, b in one]


def bt_at(b):
    return np.interp(b, np.arange(len(bt)), bt)


def score(off):
    res = []
    for p, d, b in rows:
        t0, t1 = bt_at(off + b), bt_at(off + b + d)
        i0 = int((t0 + 0.15 * (t1 - t0)) * fr); i1 = max(i0 + 1, int((t1 - 0.1 * (t1 - t0)) * fr))
        if i1 > C.shape[1]:
            break
        seg = C[:, i0:i1].mean(axis=1)
        e = lambda q: seg[q - lo_m] if 0 <= q - lo_m < len(seg) else 0.0
        pc = np.zeros(12)
        for q in range(p - 6, p + 13):
            pc[q % 12] += e(q)
        rank = int((pc > pc[p % 12]).sum()) + 1
        ratio = e(p) / (max(e(p - 1), e(p + 1)) + 1e-9)
        res.append((p, d, b, t0, rank, ratio))
    return res


scores = {o: sum(r[5] > 1 for r in score(o)) for o in range(0, 12)}
print('notes passing per start-beat offset (control: a wrong offset should score far lower):', scores)
best = max(scores, key=scores.get)
res = score(best)
nb = sum(r[5] > 1 for r in res); rk = sum(r[4] <= 3 for r in res)
print(f'start beat {best} ({bt[best]:.2f}s), tempo {60 / per:.1f} bpm; {len(res)} melody notes; expected pitch stronger '
      f'than both semitone neighbours: {nb}/{len(res)} ({100 * nb / len(res):.0f}%); its pitch class among the 3 strongest: {rk}/{len(res)}')
for k, (p, d, b, t0, rank, ratio) in enumerate(res):
    flag = '' if ratio > 1 else '   <-- neighbour stronger'
    if '--all' in sys.argv or flag:
        bar = int((b - 1) // 4) + 1 if b >= 1 else 0
        print(f'  #{k:3d} bar {bar:2d} {nn(p):4s} {d:4g} beats @ {t0:6.2f}s  pc rank {rank:2d}  vs neighbours {ratio:5.2f}{flag}')
