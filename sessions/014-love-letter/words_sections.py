#!/usr/bin/env python3
"""words_sections.py FILE.mp3 vNNN LANG MODEL 'section=expected words' ...: Whisper word accuracy per section
(each cut with 0.5 s either side), words counted as the longest common subsequence. Sections' times from renders/vNNN.meta.json."""
import sys, os, subprocess, re, json, numpy as np
open("/proc/self/oom_score_adj", "w").write("1000")
os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
from faster_whisper import WhisperModel
f, v, lang, model = sys.argv[1:5]
S = {s["name"]: s for s in json.load(open(f"renders/{v}.meta.json"))["sections"]}
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=2)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
norm = lambda t: re.findall(r"[a-záéíóúñü']+", t.lower())
tot = hit = 0
for spec in sys.argv[5:]:
    name, _, exp = spec.partition("=")
    rng = None
    if "@" in name:                       # name@t0-t1 in seconds
        name, r = name.split("@"); rng = [float(q) for q in r.split("-")]
    a, b = rng or (S[name]["start"], S[name]["end"])
    seg = x[int(max(0, a - 0.5) * 16000):int((b + 0.5) * 16000)]
    segs, _ = m.transcribe(seg, language=lang, beam_size=5, condition_on_previous_text=False, vad_filter=False)
    text = " ".join(s.text.strip() for s in segs)
    got, want = norm(text), norm(exp)
    L = [[0] * (len(got) + 1) for _ in range(len(want) + 1)]       # longest common subsequence
    for i, w in enumerate(want):
        for j, g in enumerate(got):
            L[i + 1][j + 1] = L[i][j] + 1 if w == g else max(L[i][j + 1], L[i + 1][j])
    n = L[-1][-1]
    tot += len(want); hit += n
    print("%-12s %2d/%2d %3.0f%% | %s" % (name, n, len(want), 100 * n / len(want), text[:150]))
print("total %d/%d = %.0f%%" % (hit, tot, 100 * hit / tot))
