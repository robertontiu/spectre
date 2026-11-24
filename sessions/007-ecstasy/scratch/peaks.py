import sys, json, numpy as np
sys.path.insert(0, '/home/claude/spectre/engine')
import studio as S
from hand import Hand
P = json.load(open('/home/claude/spectre/sessions/007-ecstasy/project.json'))
h = Hand(P['bpm'], P.get('swing', 0.5), P.get('seed', 1))
ev, holds, secs, total = S.schedule(P, h)
n = int((total + 3) * S.SR); a, b = int(350 * S.SR), int(400 * S.SR)
for name in sys.argv[1:]:
    st = S.render_track(name, P['tracks'][name], ev[name], holds[name], n, P['bpm'])[:, a:b]
    print(name, 'pk', round(20*np.log10(np.abs(st).max()+1e-9),1), 'rms', round(20*np.log10(np.sqrt((st**2).mean())+1e-9),1))
from scipy import signal
T=[50,63,80,100,125,160]
if '--bands' in sys.argv[-1:]: pass
