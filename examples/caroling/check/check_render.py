"""Pitch-track the check render (pYIN) and compare every note of the melody blocks with what the engine played.
Usage: cd examples/caroling && python3 check/check_render.py [renders/v001.premaster.wav]"""
import os, sys
import numpy as np, librosa, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import melodies as M
from check_midi import midi_of

def notes(pickup, body, bpm, t0):
    out, sp = [], 60.0 / bpm / 4  # seconds per step
    for s, off in ((pickup, 0), (body, 16)):
        for tok in s.split():
            st, n, ln = tok.split(":")[:3]
            out.append((t0 + (float(st) + off) * sp, float(ln) * sp, midi_of(n), n))
    return out

wav = sys.argv[1] if len(sys.argv) > 1 else "renders/v001.premaster.wav"
y, sr = sf.read(wav, dtype="float32")
y = librosa.resample(y.mean(axis=1) if y.ndim > 1 else y, orig_sr=sr, target_sr=22050)
f0, vf, _ = librosa.pyin(y, fmin=130, fmax=1000, sr=22050, frame_length=2048, hop_length=256)
times = librosa.times_like(f0, sr=22050, hop_length=256)
t_nowell = 13 * 4 * 60 / 84
for name, ns in (("CAROL", notes(M.CAROL_PICKUP, M.CAROL, 84, 0.0)),
                 ("THE FIRST NOWELL", notes(M.NOWELL_PICKUP, M.NOWELL, 104, t_nowell))):
    ok, bad = 0, []
    for t, d, m, n in ns:
        sel = (times > t + 0.05) & (times < t + max(0.08, d * 0.7))
        p = f0[sel]; p = p[~np.isnan(p)]
        got = float(np.median(librosa.hz_to_midi(p))) if len(p) else None
        if got is not None and abs(got - m) < 0.5:
            ok += 1
        else:
            bad.append((round(t, 2), n, None if got is None else round(got, 2)))
    print(f"{name}: {ok}/{len(ns)} notes tracked at the written pitch; misses: {bad}")
