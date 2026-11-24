#!/usr/bin/env python3
"""bands.py file.wav [t0 t1]: peak, rms and 1/3-octave levels 31-400 Hz of a wav (mono sum)"""
import sys, soundfile as sf, numpy as np
from scipy import signal
T=[31.5,40,50,63,80,100,125,160,200,250,315,400]
x,sr=sf.read(sys.argv[1]); m=x.mean(1) if x.ndim>1 else x
if len(sys.argv)>3: m=m[int(float(sys.argv[2])*sr):int(float(sys.argv[3])*sr)]
f,P=signal.welch(m,sr,nperseg=32768)
b=[10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()+1e-20) for c in T]
print(sys.argv[1].split('/')[-1],'pk',round(20*np.log10(np.abs(m).max()),1),'rms',round(20*np.log10(np.sqrt((m**2).mean())),1), ' '.join(f"{c}:{v:.0f}" for c,v in zip(T,b)))
