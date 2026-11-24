"""Pitch-track the engine's render (monophonic piano) and compare with the transcription note by note.
python3 -I check_render.py render.wav bpm out_seq.json"""
import sys, json, numpy as np, librosa
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from melody import stanza
from midi_dump import nn
wav, bpm, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3]
sr, hop = 22050, 256
y, _ = librosa.load(wav, sr=sr, mono=True)
f0, vf, vp = librosa.pyin(y, fmin=200, fmax=1000, sr=sr, hop_length=hop, frame_length=2048)
on = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop, backtrack=False, units='frames', delta=0.05)
beat = 60 / bpm
# expected: pickup at beat 3 of a lead-in bar; a, b with 2nd ending (no repeat of b)
seq = stanza(3)
a_b = []
pos = 3.0
cnt = 0
# a + b once: pickup + 10 + 10 bars (stanza() = pickup + a + b + b(2nd ending)); take pickup, a, last b
bars_beats = 1 + 40 + 40
full = []
for p, d in seq:
    full.append((p, d, pos)); pos += d
exp = [(p, d, b) for p, d, b in full if p is not None and b < 3 + 1 + 40] + \
      [(p, d, b - 40) for p, d, b in full if p is not None and b >= 3 + 1 + 80]
got = []
for k, f in enumerate(on):
    g = on[k + 1] if k + 1 < len(on) else len(f0)
    seg = f0[f:f + max(2, int(0.6 * (g - f)))]
    seg = seg[~np.isnan(seg)]
    if len(seg):
        got.append((int(round(np.median(librosa.hz_to_midi(seg)))), f * hop / sr / beat))
print(f'{len(got)} notes tracked in the render, {len(exp)} expected')
ok = 0
for i, (p, d, b) in enumerate(exp):
    c = [g for g in got if abs(g[1] - b) < 0.2]
    hit = c and c[0][0] == p
    ok += bool(hit)
    if not hit:
        print('  mismatch at beat', b, 'expected', nn(p), 'got', c)
print(f'render vs transcription: {ok}/{len(exp)} notes at the right pitch and onset (within 0.2 beat)')
json.dump([[g[0], g[1]] for g in got], open(outp, 'w'))
