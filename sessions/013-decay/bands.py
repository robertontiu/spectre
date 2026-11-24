#!/usr/bin/env python3
"""bands.py t0 t1 track...: 1/3-octave band levels (dB) of unclipped stems, plus the premaster of the latest render"""
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/spectre/engine')
import studio as S
from hand import Hand
import soundfile as sf
P = json.load(open('project.json'))
h = Hand(P['bpm'], P.get('swing', 0.5), P.get('seed', 1))
ev, holds, secs, total = S.schedule(P, h)
n = int((total + 3) * S.SR); t0, t1 = float(sys.argv[1]), float(sys.argv[2]); a, b = int(t0 * S.SR), int(t1 * S.SR)
F = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315]
if '--hi' in sys.argv: F = [1000, 2000, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]
def bl(x):
    x = x.mean(0) if x.ndim == 2 else x
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; fr = np.fft.rfftfreq(len(x), 1 / S.SR)
    return [10 * np.log10(sp[(fr >= f / 2 ** (1 / 6)) & (fr < f * 2 ** (1 / 6))].sum() / len(x) + 1e-12) for f in F]
print("%-8s" % "", " ".join("%6s" % f for f in F))
names = [x for x in sys.argv[3:] if not x.startswith('--')]
for name in names:
    if name == 'mix':
        v = json.load(open('renders/latest.json'))
        v = v.get('version', v) if isinstance(v, dict) else v
        x, sr = sf.read(f"renders/{v}.premaster.wav" if str(v).startswith('v') else v); x = x.T[:, a:b]
    else:
        x = S.render_track(name, P['tracks'][name], ev[name], holds[name], n, P['bpm'])
        x = x[..., a:b]
    print("%-8s" % name, " ".join("%6.1f" % v for v in bl(x)))
