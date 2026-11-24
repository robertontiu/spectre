#!/usr/bin/env python3
"""spec.py file.wav [t0 t1]: 1/3-octave long-term levels (dB, absolute) 31.5 Hz-16 kHz"""
import sys, numpy as np, soundfile as sf
x, sr = sf.read(sys.argv[1]); x = x.mean(1) if x.ndim > 1 else x
if len(sys.argv) > 3: x = x[int(float(sys.argv[2])*sr):int(float(sys.argv[3])*sr)]
F = np.fft.rfft(x * np.hanning(len(x))); f = np.fft.rfftfreq(len(x), 1/sr); P = np.abs(F)**2
bands = [31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000]
out=[]
for b in bands:
    m = (f >= b/2**(1/6)) & (f < b*2**(1/6)); out.append(10*np.log10(P[m].sum()+1e-20))
ref = out[bands.index(1000)]
print(" ".join(f"{b:g}:{v-ref:+.1f}" for b, v in zip(bands, out)))
