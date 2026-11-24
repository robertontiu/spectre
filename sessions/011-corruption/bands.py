#!/usr/bin/env python3
"""bands.py wav [wav...]: third-octave band levels (dB, whole file energy) at key bands"""
import sys, numpy as np, soundfile as sf
B=[31.5,50,63,80,100,125,200,315,500,1000,2000,3150,4000,5000,6300,8000,10000]
print("%-22s"%"", " ".join("%6s"%(str(b)[:6]) for b in B))
for f in sys.argv[1:]:
    x,sr=sf.read(f); x=x.mean(1) if x.ndim>1 else x
    X=np.abs(np.fft.rfft(x))**2; fr=np.fft.rfftfreq(len(x),1/sr)
    row=[]
    for b in B:
        m=(fr>=b/2**(1/6))&(fr<b*2**(1/6)); row.append(10*np.log10(X[m].sum()/len(x)+1e-12))
    print("%-22s"%f.split('/')[-1][:22], " ".join("%6.1f"%v for v in row))
