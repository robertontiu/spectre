#!/usr/bin/env python3
"""voxcheck.py vNNN [--nomute]: the two checks of docs/voice/MIXING.md section 6 for this session.
1) voice against band: renders a scratch copy with `voz` muted (scratch_mute/), voice = premaster - band, LU per sung line
2) words: Whisper small forced to Spanish on each sung line: voice alone, the mix, and the master if it exists."""
import os, sys, json, subprocess, unicodedata, shutil
import numpy as np, soundfile as sf, librosa, pyloudnorm as pyln
v = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
LINES = [("te escribo", 10.6, 15.0), ("lo que no supe decir", 33.1, 40.0), ("te escribo despacio", 56.3, 63.6),
         ("lo que no supe decir", 78.8, 86.0), ("lo que no supe decir", 170.2, 179.8), ("siempre tuya", 196.6, 204.5)]
sm = os.path.join(HERE, "scratch_mute")
if "--nomute" not in sys.argv:
    shutil.rmtree(sm, ignore_errors=True); os.makedirs(sm)
    P = json.load(open(f"{HERE}/renders/{v}.project.json")); P["tracks"]["voz"]["mute"] = True
    json.dump(P, open(f"{sm}/project.json", "w"))
    subprocess.run(["python3", "/home/claude/spectre/engine/studio.py", "render"], env=dict(os.environ, BEAT_DIR=sm),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
mix, sr = sf.read(f"{HERE}/renders/{v}.premaster.wav")
band, _ = sf.read(f"{sm}/renders/v001.premaster.wav")
n = min(len(mix), len(band)); vox = mix[:n] - band[:n]
meter = pyln.Meter(sr, block_size=0.4)
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
from faster_whisper import WhisperModel
W = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))
    return "".join(c if c.isalnum() or c.isspace() else " " for c in s).split()


def hear(y, a, b):
    seg = y[int(a * sr):int(b * sr)]; seg = seg.mean(axis=1) if seg.ndim > 1 else seg
    seg = librosa.resample(seg.astype(np.float32), orig_sr=sr, target_sr=16000); seg = seg / (np.abs(seg).max() + 1e-9) * 0.7
    segs, _ = W.transcribe(seg, language="es", beam_size=5, condition_on_previous_text=False)
    return " ".join(x.text.strip() for x in segs)


def found(ref, hyp):
    r, h = norm(ref), norm(hyp); k = 0; j = 0
    for w in r:
        if w in h[j:]:
            j = h.index(w, j) + 1; k += 1
    return k, len(r)


srcs = [("voice", vox), ("mix", sf.read(f"{HERE}/renders/{v}.wav")[0])]
mp = f"{HERE}/renders/{v}.master.wav"
if os.path.exists(mp):
    srcs.append(("master", sf.read(mp)[0]))
tot = {k: [0, 0] for k, _ in srcs}
for ref, a, b in LINES:
    lv = meter.integrated_loudness(vox[int(a * sr):int(b * sr)]); lb = meter.integrated_loudness(band[int(a * sr):int(b * sr)])
    row = f"{a:6.1f}s {ref!r:24} voice-band {lv - lb:+5.1f} LU |"
    for k, y in srcs:
        h = hear(y, a, b); f, t = found(ref, h); tot[k][0] += f; tot[k][1] += t
        row += f" {k}: {h!r} {f}/{t} |"
    print(row)
print("words found: " + ", ".join(f"{k} {a}/{b} = {100 * a / b:.0f}%" for k, (a, b) in tot.items()))
