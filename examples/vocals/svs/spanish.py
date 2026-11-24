"""Spanish check for singer source "svs" (docs/voice/VOICES.md "Spanish", docs/voice/languages/es.md).

python3 examples/vocals/svs/spanish.py      # renders, transcribes, writes voices/<id>.mp3 and spanish.json
Five short Spanish lines (F#4-B4 area, 92 bpm, one syllable per note) are sung dry through the engine
(singer.sing, source "svs", lang "es") by each Spanish-capable voice, then transcribed by Whisper (faster-whisper
"small", multilingual, int8 on CPU; model cached in ~/.cache/spectre/svs/hf) once forced to Spanish (word accuracy
against the lyric, accents and punctuation ignored) and once with language detection (which language Whisper
hears, and how sure it is). The control sings the same lines with the English path (cmudict letters: Spanish
words it doesn't know are sung as "ah"), to show what the Spanish G2P adds.
"""
import json
import os
import subprocess
import sys
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
SR = 44100
OUT = os.path.join(HERE, "voices")
BPM = 92
LINES = [  # (lyrics with hyphenated syllables, melody: note:length in 16ths, one per syllable)
    ("ca-da pa-la-bra lle-va tu nom-bre", "E4:2 F#4:2 G4:2 A4:2 B4:4 A4:2 G4:2 F#4:4 G4:2 E4:8"),
    ("quie-ro que-dar-me a-quí con-ti-go", "B4:4 A4:2 G4:2 A4:2 B4:2 G4:2 A4:6 F#4:2 G4:2 E4:8"),
    ("guar-do tu voz en el pa-pel", "A4:4 G4:2 F#4:2 G4:6 E4:2 F#4:2 G4:2 A4:10"),
    ("mi co-ra-zón no sa-be es-pe-rar", "F#4:2 G4:2 A4:2 B4:6 A4:2 G4:2 F#4:2 G4:2 A4:2 B4:10"),
    ("te es-cri-bo con la luz de la ma-ña-na", "E4:2 F#4:2 G4:2 A4:4 G4:2 F#4:2 G4:4 A4:2 B4:2 A4:2 G4:2 E4:8"),
]
JOBS = [  # (output name, voice id, extra params)
    ("hanami-es", "hanami-es", {}),
    ("hanami-es-soft", "hanami-es-soft", {}),
    ("ctl-hanami-es-english-g2p", "hanami", {"lang": "en"}),
]


def notes(melody, start=0.3):
    from hand import note_to_midi
    q = 60.0 / BPM / 4
    t, out = start, []
    for tok in melody.split():
        n, ln = tok.split(":")
        m = note_to_midi(n)
        out.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), f=440 * 2 ** ((m - 69) / 12), vel=0.9,
                        glide=False))
        t += float(ln) * q
    return out, int((t + 0.8) * SR)


def norm_words(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))
    s = "".join(c if c.isalnum() or c.isspace() else " " for c in s.replace("-", ""))
    return s.split()


def word_accuracy(ref, hyp):
    r, h = norm_words(ref), norm_words(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1))
    d[:, 0] = range(len(r) + 1)
    d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return 1 - d[len(r), len(h)] / len(r)


_W = None


def whisper(y):
    global _W
    os.environ.setdefault("HF_HOME", os.path.expanduser("~/.cache/spectre/svs/hf"))
    from faster_whisper import WhisperModel
    import librosa
    if _W is None:
        _W = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
    a = librosa.resample(y.astype(np.float32), orig_sr=SR, target_sr=16000)
    segs, _ = _W.transcribe(a, language="es", beam_size=5, condition_on_previous_text=False)
    text = " ".join(s.text.strip() for s in segs)
    _, info = _W.transcribe(a, beam_size=1, condition_on_previous_text=False)
    return text, info.language, float(info.language_probability)


def main():
    import singer
    import soundfile as sf
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for name, vid, extra in JOBS:
        lines, takes = [], []
        for lyr, mel in LINES:
            ns, n = notes(mel)
            p = dict({"source": "svs", "voice": vid, "lyrics": lyr, "seed": 1}, **extra)
            y = singer.sing(p, ns, n)
            text, lang, prob = whisper(y)
            acc = word_accuracy(lyr, text)
            lines.append(dict(lyrics=lyr.replace("-", ""), heard=text, words=round(acc, 3), detected=lang,
                              detected_p=round(prob, 2)))
            print(f"{name}: {acc:.0%} | {lyr.replace('-', '')} -> {text} [{lang} {prob:.2f}]")
            takes.append(y / max(np.abs(y).max(), 1e-9) * 0.89)
            takes.append(np.zeros(int(0.4 * SR), dtype=np.float32))
        nw = [len(norm_words(l["lyrics"])) for l in lines]
        tot = sum(l["words"] * k for l, k in zip(lines, nw)) / sum(nw)
        res[name] = dict(voice=vid, params=extra, word_accuracy=round(tot, 3), lines=lines,
                         detected_spanish=sum(l["detected"] == "es" for l in lines))
        print(f"{name}: word accuracy {tot:.0%}, heard as Spanish {res[name]['detected_spanish']}/{len(lines)}")
        wav = f"/tmp/spectre_svs/{name}.wav"
        os.makedirs("/tmp/spectre_svs", exist_ok=True)
        sf.write(wav, np.concatenate(takes), SR)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", os.path.join(OUT, name + ".mp3")],
                       check=True)
    json.dump(res, open(os.path.join(HERE, "spanish.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    main()
