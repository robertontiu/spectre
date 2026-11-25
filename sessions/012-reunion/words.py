#!/usr/bin/env python3
"""words.py [--model small.en] FILE [FILE ...]: Whisper (medium.en by default) on the one sung line, "Peace on the earth, good will to men", in the
two places it is sung (the meeting, the a cappella reprise), at three window offsets per place. Words counted as the
longest common subsequence of the line's eight words ("man" for "men" is not counted). A threshold instrument: read one
word as noise. temperature 0 (no fallback sampling): deterministic, and 2.9 GB instead of 4 GB at the peak.
Heavy: wait for a free slot and 5000 MB available before running; never two at once."""
import sys, os, subprocess, re, numpy as np
open("/proc/self/oom_score_adj", "w").write("1000")
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
from faster_whisper import WhisperModel
LINE = "peace on the earth good will to men"
# first note of the quote: q_sop at 28.03 s (the meeting), q_sop2 at 113.78 s (the reprise); the line lasts about 8 s
PLACES = [("meeting", 28.03, 36.6), ("reprise", 113.78, 122.6)]
OFFS = [(-0.5, 0.5), (-0.8, 0.2), (-0.2, 0.9)]          # window start / end against the line, in seconds
MODEL = "medium.en"
if sys.argv[1] == "--model":
    MODEL = sys.argv[2]; del sys.argv[1:3]
m = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=2)
want = LINE.split()
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    tot = 0
    print(f, "(%s)" % MODEL)
    for name, t0, t1 in PLACES:
        for a, b in OFFS:
            seg = x[int((t0 + a) * 16000):int((t1 + b) * 16000)]
            segs, _ = m.transcribe(seg, language="en", beam_size=5, temperature=0.0, condition_on_previous_text=False, vad_filter=False)
            text = " ".join(s.text.strip() for s in segs)
            got = re.findall(r"[a-z']+", text.lower().replace("goodwill", "good will"))
            L = [[0] * (len(got) + 1) for _ in range(len(want) + 1)]
            for i, w in enumerate(want):
                for j, g in enumerate(got):
                    L[i + 1][j + 1] = L[i][j] + 1 if w == g else max(L[i][j + 1], L[i + 1][j])
            n = L[-1][-1]; tot += n
            print("  %-8s %+.1f/%+.1f  %d/8 | %s" % (name, a, b, n, text[:110]), flush=True)
    print("  total %d/48" % tot)
