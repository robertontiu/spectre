#!/usr/bin/env python3
"""fastlisten.py [listen args]: runs `studio.py listen` with np.convolve swapped for an FFT convolution
for long inputs. ear.py's 400 ms loudness curve is a direct convolution (O(n x 17640)): a 4-minute track
took over 15 minutes on this machine. Same result to float precision."""
import sys, numpy as np, scipy.signal as ss
sys.path.insert(0, "/home/user/spectre/engine")
_conv = np.convolve
def conv(a, v, mode="full"):
    if len(a) > 100000 and len(v) > 1000:
        return ss.fftconvolve(a, v, mode=mode)
    return _conv(a, v, mode=mode)
np.convolve = conv
import studio
sys.argv = ["studio.py", "listen"] + sys.argv[1:]
studio.main()
