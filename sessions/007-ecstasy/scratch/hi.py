import sys, json, numpy as np
sys.path.insert(0, '/home/claude/spectre/engine')
import studio as S
from hand import Hand
from scipy import signal
P = json.load(open('/home/claude/spectre/sessions/007-ecstasy/project.json'))
h = Hand(P['bpm'], 0.5, P.get('seed', 1)); ev, holds, secs, total = S.schedule(P, h)
n = int((total + 3) * S.SR); a, b = int(350 * S.SR), int(370 * S.SR)
for name in sys.argv[1:]:
    tr = P['tracks'][name]
    st = S.render_track(name, tr, [e for e in ev[name] if 348 < e['t'] < 370], holds[name], n, P['bpm'])[:, a:b]
    m = st.mean(0); f, Pw = signal.welch(m, S.SR, nperseg=8192)
    print(f"{name:6s}", ' '.join(f"{c}:{10*np.log10(Pw[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()+1e-20):.0f}" for c in [1000, 4000, 6300, 8000, 12500, 16000]))
