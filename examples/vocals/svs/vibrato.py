"""`svs_vibrato` for singer source "svs": measurement and a choir A/B (docs/voice/GENERAL.md, "Vibrato and pitch
scatter"; docs/MANUAL.md "Voices").

python3 examples/vocals/svs/vibrato.py measure   # fast pitch movement inside held vowels at svs_vibrato 1, 0.5, 0
python3 examples/vocals/svs/vibrato.py choir     # choir-vibrato-1.mp3 and choir-vibrato-0.3.mp3

measure: six short English lines (Hanami Root, 100 bpm, F#4-B4 area) are sung through the bank at each setting. Inside
each vowel (its phoneme span minus 60 ms at both ends, so consonants and transitions are out) of at least 300 ms, the
pitch of the rendered audio (pyworld harvest, 5 ms frames) minus its 205 ms moving average gives the fast movement
(vibrato and jitter): its standard deviation in cents, averaged over the vowels. The output follows the f0 the
vocoder is fed to within about 1 cent, so this measures what the setting does. Phrase caches go to /tmp.
choir: a three-take texture (hanami on the melody, hanami-soft a third below, leona-soft on the melody; separate
seeds, panned), dry, through singer.sing as a session would use it, once as the model sings it and once with
svs_vibrato 0.3 (straighter tone, as ensembles do for blend).
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
SR = 44100
LINES = [("here you are, round and round", "F#4:4 A4:4 B4:8 A4:4 F#4:2 A4:10"),
         ("hold on tight, round we go", "A4:4 B4:4 A4:6 F#4:2 E4:4 F#4:10"),
         ("and you stay on the ride", "E4:2 F#4:2 A4:4 B4:4 A4:2 F#4:10"),
         ("close your eyes and let it go", "F#4:4 E4:2 F#4:4 A4:2 B4:2 A4:2 F#4:10"),
         ("stars fall slow-ly through the night", "B4:4 A4:4 F#4:2 E4:2 F#4:4 A4:2 B4:10"),
         ("bring the light back home", "E4:2 F#4:2 A4:4 B4:4 A4:12")]


def notes(mel, bpm=100, start=0.3):
    from hand import note_to_midi
    q = 60.0 / bpm / 4
    t, out = start, []
    for tok in mel.split():
        n, ln = tok.split(":")
        m = note_to_midi(n)
        out.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), f=440 * 2 ** ((m - 69) / 12), vel=0.9,
                        glide=False))
        t += float(ln) * q
    return out, int((t + 0.8) * SR)


def fast_sd(c):
    c = np.asarray(c, float)
    return float(np.std(c - np.convolve(np.pad(c, 20, mode="edge"), np.ones(41) / 41, "valid")))


def measure():
    import pyworld as pw
    import svs
    svs.PHRASES = "/tmp/spectre_svs/vibrato-phrases"
    bank = svs.Bank.get("hanami", svs.voices()["banks"])
    res = {}
    for amount in (1.0, 0.5, 0.0):
        vals = []
        for lyr, mel in LINES:
            sylls = []
            for w in lyr.replace(",", "").split():
                sylls += bank.syllables(w, len([x for x in w.split("-") if x]))
            ns, _ = notes(mel)
            nn = [[x["t0"] / SR * 1000, 0, int(round(69 + 12 * np.log2(x["f"] / 440))), k] for k, x in enumerate(ns)]
            for a, b in zip(nn, nn[1:]):
                a[1] = b[0] - a[0]
            nn[-1][1] = ns[-1]["n"] / SR * 1000
            wav, t0, ph = bank.render(sylls, [tuple(x) for x in nn], "Root", 7, vibrato=amount)
            f0, t = pw.harvest(wav.astype(np.float64), SR, f0_floor=150, f0_ceil=900, frame_period=5.0)
            for x, s, e, k, part in ph:
                if not bank.is_vowel(x) or x in ("SP", "AP") or e - s < 300:
                    continue
                m = (t * 1000 + t0 >= s + 60) & (t * 1000 + t0 <= e - 60) & (f0 > 0)
                if m.sum() > 40:
                    vals.append(fast_sd(1200 * np.log2(f0[m])))
        res[amount] = round(float(np.mean(vals)), 1)
        print(f"svs_vibrato {amount}: fast pitch movement inside held vowels {res[amount]} cents sd ({len(vals)} vowels)",
              flush=True)
    return res


def choir():
    import singer
    lyr, mel = LINES[0]
    third = " ".join({"F#4": "D4", "A4": "F#4", "B4": "G4"}[t.split(":")[0]] + ":" + t.split(":")[1] for t in mel.split())
    parts = [("hanami", mel, 1, -0.5), ("hanami-soft", third, 2, 0.5), ("leona-soft", mel, 3, 0.1)]  # a diatonic third
    # below in D major for the second voice; voice, melody, seed, pan
    for amount in (1.0, 0.3):
        mixL = mixR = None
        for voice, line, seed, pan in parts:
            ns, total = notes(line)
            p = {"source": "svs", "voice": voice, "lyrics": lyr, "seed": seed, "svs_vibrato": amount,
                 "svs_fade_in_ms": 30, "svs_fade_out_ms": 120}
            y = singer.sing(p, ns, total) * 0.3
            a = (pan + 1) * np.pi / 4
            L, R = y * np.cos(a), y * np.sin(a)
            mixL = L if mixL is None else mixL + L
            mixR = R if mixR is None else mixR + R
        st = np.stack([mixL, mixR], 1)
        st = st / (np.abs(st).max() + 1e-9) * 0.8
        out = os.path.join(HERE, f"choir-vibrato-{amount:g}.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-b:a", "128k", out], input=st.astype("<f4").tobytes(), check=True)
        print("wrote", out)


if __name__ == "__main__":
    {"measure": measure, "choir": choir}[sys.argv[1] if len(sys.argv) > 1 else "measure"]()
