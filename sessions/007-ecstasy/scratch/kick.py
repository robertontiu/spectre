import sys, json, numpy as np
sys.path.insert(0, '/home/claude/spectre/engine')
import studio as S
from hand import Hand
from scipy import signal
P = json.load(open('/home/claude/spectre/sessions/007-ecstasy/project.json'))
tr = P['tracks']['kick']; tr['fx'] = json.loads(sys.argv[1]); tr['inst'].update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
h = Hand(P['bpm'], 0.5, P.get('seed', 1)); ev, holds, secs, total = S.schedule(P, h)
n = int((total + 3) * S.SR); a, b = int(350 * S.SR), int(360 * S.SR)
st = S.render_track('kick', tr, [e for e in ev['kick'] if 349 < e['t'] < 360], [], n, P['bpm'])[:, a:b]
m=st.mean(0); f,Pw=signal.welch(m,S.SR,nperseg=32768)
print('pk', round(20*np.log10(np.abs(st).max()),1), 'rms', round(20*np.log10(np.sqrt((st**2).mean())),1),
 ' '.join(f"{c}:{10*np.log10(Pw[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):.1f}" for c in [50,63,80,100,125,160,200]))
