#!/usr/bin/env python3
"""words.py master.mp3: Whisper (small.en) word accuracy per sung line on the mastered mix"""
import sys, os, subprocess, re, numpy as np
open("/proc/self/oom_score_adj", "w").write("1000")
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
from faster_whisper import WhisperModel
BAR = 240 / 140
LINES = [("intro 1 (bars 1-2)", 1, 3, "half of me is light"), ("intro 2 (bars 5-6)", 5, 7, "half of me is light"),
         ("drop 1 call (39-40)", 39, 41, "half of me is light"), ("breakdown line (51-52)", 51, 53, "half of me is light"),
         ("breakdown answer (57-60)", 57, 61, "half of what is left holds on"), ("main call (103-104)", 103, 105, "half of me is light"),
         ("last line (119-120)", 119, 121, "half of me is")]
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", sys.argv[1], "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
tot = hit = 0
for name, b0, b1, exp in LINES:
    a, b = max(0, int(((b0 - 1) * BAR - 0.5) * 16000)), int(((b1 - 1) * BAR + 0.6) * 16000)
    segs, _ = m.transcribe(x[a:b], language="en", beam_size=5, condition_on_previous_text=False, vad_filter=False)
    text = " ".join(s.text.strip() for s in segs)
    got = re.findall(r"[a-z']+", text.lower()); want = exp.split()
    # words found in order
    k = 0; n = 0
    for w in want:
        if w in got[k:]:
            k = got.index(w, k) + 1; n += 1
    tot += len(want); hit += n
    print("%-26s %d/%d  | %s" % (name, n, len(want), text))
print("total %d/%d = %.0f%%" % (hit, tot, 100 * hit / tot))
