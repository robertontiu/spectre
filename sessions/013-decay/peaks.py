#!/usr/bin/env python3
"""peaks.py t0 t1 track...: unclipped per-track peak and rms (dB) between t0 and t1 seconds"""
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/spectre/engine')
import studio as S
from hand import Hand
P = json.load(open('project.json'))
h = Hand(P['bpm'], P.get('swing', 0.5), P.get('seed', 1))
ev, holds, secs, total = S.schedule(P, h)
n = int((total + 3) * S.SR); a, b = int(float(sys.argv[1]) * S.SR), int(float(sys.argv[2]) * S.SR)
for name in sys.argv[3:]:
    st = S.render_track(name, P['tracks'][name], ev[name], holds[name], n, P['bpm'])
    st = st[..., a:b] if st.shape[-1] > 4 else st[a:b]
    print(name, 'pk', round(20*np.log10(np.abs(st).max()+1e-9),1), 'rms', round(20*np.log10(np.sqrt((st**2).mean())+1e-9),1))
