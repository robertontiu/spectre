#!/bin/bash
# Diagnostic: render each named track solo and print its RMS and band levels over the first 6 s.
# Usage (from a session folder with BEAT_DIR set): bash ../../engine/solos.sh kick 808 snare
for s in "$@"; do python3 "$(dirname "$0")/studio.py" render --solo $s >/dev/null; python3 -c "
import soundfile as sf,numpy as np
from scipy.signal import welch
x,sr=sf.read('renders/solo_$s.wav'); x=x.mean(1) if x.ndim>1 else x
x=x[:int(6*sr)]; f,p=welch(x,sr,nperseg=4096)
print('%-6s rms %6.1f'%('$s',20*np.log10(np.sqrt((x**2).mean())+1e-9)), [round(10*np.log10(p[(f>=lo)&(f<hi)].sum()+1e-12),1) for lo,hi in [(20,60),(60,250),(250,2000),(2000,8000),(8000,20000)]])
"; done
