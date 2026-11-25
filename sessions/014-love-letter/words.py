#!/usr/bin/env python3
"""words.py <wav> <start_s> <end_s> [...]: Whisper (small, forced Spanish) on slices of a render; adapted from
examples/vocals/svs/spanish.py. Prints what it hears per slice."""
import os, sys
import numpy as np, soundfile as sf, librosa
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
from faster_whisper import WhisperModel
W = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
y, sr = sf.read(sys.argv[1])
if y.ndim > 1:
    y = y.mean(axis=1)
a = [float(x) for x in sys.argv[2:]]
for s, e in zip(a[::2], a[1::2]):
    seg = librosa.resample(y[int(s * sr):int(e * sr)].astype(np.float32), orig_sr=sr, target_sr=16000)
    seg = seg / (np.abs(seg).max() + 1e-9) * 0.7
    segs, info = W.transcribe(seg, language="es", beam_size=5, condition_on_previous_text=False)
    print(f"{s:6.1f}-{e:6.1f}: {' '.join(x.text.strip() for x in segs)!r}")
