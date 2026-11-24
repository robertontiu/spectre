"""Word sampler for `singer` with `"source": "tts"`: neutral spoken words from a local neural text-to-speech, cached.

This is the one place where Spectre uses a neural model, and only as a word sampler (approved by the owner): Kokoro
(82M parameters, Apache 2.0 weights, run locally with onnxruntime through `kokoro-onnx`) speaks each lyric word once,
neutrally. Everything musical happens afterwards in the engine (engine/singer.py): the WORLD vocoder analyses the word,
the melody replaces its pitch, its vowels are stretched over the notes while its consonants keep their spoken length,
and breath, doubling and reverb go on top. No singing model, no recordings.

Cache: every spoken word is written once to ~/.cache/spectre/words/<voice>/<key>.wav (44.1 kHz float WAV; key = a hash
of model, voice, speed and text; a .txt beside it holds the text). The cache is outside the repo and can be deleted at
any time: a render regenerates the words it needs (deterministic for the same model files and onnxruntime build). With
every word of a project in the cache, rendering doesn't need the model at all.
Model files: models/tts/kokoro/ in the repo (kokoro-v1.0.onnx in git LFS, voices-v1.0.bin; source, licence and checksums
in models/tts/kokoro/README.md); $SPECTRE_TTS_DIR points elsewhere if they move out of the repo.
"""
import functools
import hashlib
import os
import sys

import numpy as np
from scipy import signal

SR = 44100
FP = 5.0  # WORLD frame period, ms (same as singer.py)
MODEL_TAG = "kokoro-v1.0"
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.expanduser(os.environ.get("SPECTRE_TTS_DIR", os.path.join(_REPO, "models", "tts", "kokoro")))
CACHE_DIR = os.path.expanduser(os.environ.get("SPECTRE_WORDS_DIR", "~/.cache/spectre/words"))
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"

# `voice` name -> Kokoro voice. af_heart is Kokoro's flagship US-English female voice, am_michael a US-English male
# voice; `tts_voice` takes any Kokoro voice name (af_bella, af_sarah, am_adam, bf_emma, bm_george, ...)
VOICES = {"female": "af_heart", "male": "am_michael", "female2": "af_bella", "male2": "am_adam"}


def kokoro_voice(p):
    return p.get("tts_voice") or VOICES.get(p.get("voice", "female"), VOICES["female"])


@functools.lru_cache(maxsize=1)
def _model():
    paths = [os.path.join(MODEL_DIR, f) for f in MODEL_FILES]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise RuntimeError(
            "singer source 'tts' needs the Kokoro model files, missing: " + ", ".join(missing) +
            f". They are versioned in models/tts/kokoro/ (the .onnx in git LFS: run `git lfs pull`), or download "
            f"{MODEL_URL}kokoro-v1.0.onnx (325 MB) and {MODEL_URL}voices-v1.0.bin (28 MB) into {MODEL_DIR} (or set "
            "SPECTRE_TTS_DIR); and pip install kokoro-onnx")
    try:
        from kokoro_onnx import Kokoro
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("singer source 'tts' needs kokoro-onnx: pip install kokoro-onnx") from e
    return Kokoro(*paths)


def _key(text, voice, speed):
    return hashlib.sha1(f"{MODEL_TAG}|{voice}|{speed:.3f}|{text}".encode()).hexdigest()[:20]


def spoken(text, voice="af_heart", speed=0.9):
    """The word (or phrase) spoken neutrally by the TTS: float64 mono at 44.1 kHz, from the cache or generated into it.
    """
    import soundfile as sf
    d = os.path.join(CACHE_DIR, voice)
    path = os.path.join(d, _key(text, voice, speed) + ".wav")
    if os.path.exists(path):
        x, sr = sf.read(path, dtype="float64")
        return x
    lang = "en-gb" if voice[:1] == "b" else "en-us"
    a, sr = _model().create(text, voice=voice, speed=float(speed), lang=lang)
    a = np.asarray(a, dtype=np.float64)
    g = np.gcd(SR, int(sr))
    x = signal.resample_poly(a, SR // g, int(sr) // g) if sr != SR else a
    os.makedirs(d, exist_ok=True)
    tmp = path + f".tmp{os.getpid()}.wav"
    sf.write(tmp, x.astype(np.float32), SR, subtype="FLOAT")
    os.replace(tmp, path)  # atomic: a parallel render never reads half a file
    with open(path[:-4] + ".txt", "w") as f:
        f.write(text + "\n")
    x, _ = sf.read(path, dtype="float64")  # read back so a fresh word and a cached word are bit-identical
    return x


@functools.lru_cache(maxsize=4096)
def analyze(text, voice, speed):
    """WORLD analysis of a spoken word, trimmed to its sounding part: f0, spectral envelope, aperiodicity, frame level
    (waveform RMS) and a 'vowel strength' (300-3000 Hz band level from the waveform), per 5 ms frame."""
    import pyworld as pw
    x = np.ascontiguousarray(spoken(text, voice, speed))
    f0, t = pw.harvest(x, SR, frame_period=FP, f0_floor=60, f0_ceil=600)
    sp = pw.cheaptrick(x, f0, t, SR)
    ap = pw.d4c(x, f0, t, SR)
    freqs = np.linspace(0, SR / 2, sp.shape[1])
    hop = int(SR * FP / 1000)
    n = len(f0)
    xp = np.pad(x, (hop, 2 * hop))
    fr = np.stack([xp[i * hop:i * hop + 2 * hop] for i in range(n)])
    r_db = 10 * np.log10((fr ** 2).mean(1) + 1e-12)
    bp = signal.sosfiltfilt(signal.butter(3, [300, 3000], "bandpass", fs=SR, output="sos"), x)
    bpp = np.pad(bp, (hop, 2 * hop))
    v_db = 10 * np.log10(np.stack([(bpp[i * hop:i * hop + 2 * hop] ** 2).mean() for i in range(n)]) + 1e-12)
    # trim: keep from 45 dB under the peak at the start (soft /h/ and fricatives) to 38 dB under it at the end (the
    # spoken word's last decay is not part of the syllable)
    on = np.where(r_db > r_db.max() - 45)[0]
    off = np.where(r_db > r_db.max() - 38)[0]
    a, b = (max(on[0] - 1, 0), min(off[-1] + 2, n)) if len(on) else (0, n)
    e_db = 10 * np.log10(sp[:, (freqs > 250) & (freqs < 4000)].mean(1) + 1e-20)
    return dict(f0=f0[a:b], sp=sp[a:b], ap=ap[a:b], e=e_db[a:b], r=r_db[a:b], v=v_db[a:b], sr=SR, freqs=freqs,
                text=text)


def _split(w, n_syl):
    """Cut a word into n_syl syllables at the dips of its vowel strength between the n_syl strongest voiced peaks
    (forced alignment by energy and voicing: Kokoro's ONNX export gives no phoneme timings)."""
    if n_syl == 1:
        return [(0, len(w["f0"]))]
    v = np.where(w["f0"] > 0, w["v"], w["v"].min() - 10)
    k = 7
    vs = np.convolve(v, np.ones(k) / k, mode="same")
    for prom in (3.0, 1.5, 0.5):
        peaks, _ = signal.find_peaks(vs, distance=6, prominence=prom)
        if len(peaks) >= n_syl:
            break
    if len(peaks) < n_syl:
        return None
    peaks = np.sort(peaks[np.argsort(vs[peaks])[-n_syl:]])
    cuts = [0] + [p0 + int(np.argmin(vs[p0:p1 + 1])) for p0, p1 in zip(peaks[:-1], peaks[1:])] + [len(v)]
    return list(zip(cuts[:-1], cuts[1:]))


def _parts(w, a, b, thresh_db=9.0):
    """Onset, nucleus, coda inside [a, b): the nucleus is the contiguous voiced stretch around the syllable's peak
    vowel strength that stays within thresh_db of it. The 300-3000 Hz band drops 10-25 dB on nasals and voiced
    stops and 6-12 dB on liquids, so /r/, /l/, /n/, /m/ mostly stay in the onset and coda and keep their length."""
    f0, v = w["f0"][a:b], w["v"][a:b]
    vv = np.where(f0 > 0, v, -1e9)
    if not (f0 > 0).any():
        m = (b - a) // 2
        return (a, a + m), (a + m, a + m + 1), (a + m + 1, b)
    pk = int(np.argmax(vv))
    top = vv[pk]
    i0 = pk
    while i0 > 0 and vv[i0 - 1] > top - thresh_db:
        i0 -= 1
    i1 = pk + 1
    while i1 < len(vv) and vv[i1] > top - thresh_db:
        i1 += 1
    if i1 - i0 < 3:  # a nucleus needs a few frames to stretch
        i0, i1 = max(0, pk - 1), min(len(vv), pk + 2)
    return (a, a + i0), (a + i0, a + i1), (a + i1, b)


_VOWELS = set("aeiouyɑɐɒæəɘɚɛɜɝɞɨɪʊʌɔøɵɤʏɯœɶː")
_GLIDES = set("ɹlwjɾ")


@functools.lru_cache(maxsize=4096)
def final_consonants(text, lang="en-us"):
    """The consonant phonemes after the word's last vowel (IPA from Kokoro's own phonemizer, eSpeak NG based)."""
    try:
        from kokoro_onnx.tokenizer import Tokenizer
        ph = Tokenizer().phonemize(text, lang)
    except Exception:  # pragma: no cover
        return None
    ph = "".join(c for c in ph if c.isalpha() or c in _VOWELS or c in _GLIDES)
    i = max((k for k, c in enumerate(ph) if c in _VOWELS), default=-1)
    return ph[i + 1:]


def _cap_coda(sy, fin):
    """A spoken word ends with its pitch and level falling away; in a sung syllable that tail would eat the note. An
    open syllable ('we', 'go') keeps 50 ms of it, one ending on a liquid or glide ('here', 'are') 120 ms; a real final
    consonant ('round', 'tight') keeps its full length (already trimmed at -38 dB)."""
    if fin is None:
        return sy
    cap = 10 if fin == "" else (24 if all(c in _GLIDES for c in fin) else None)
    if cap is not None:
        c0, c1 = sy["co"]
        sy["co"] = (c0, min(c1, c0 + cap))
    return sy


def syllables(word, n_syl, p):
    """Analysed syllables of one lyric word for singer.py: list of dict(w=analysis, on, nu, co frame ranges)."""
    voice = kokoro_voice(p)
    speed = float(p.get("tts_speed", 0.9))
    pieces = [s for s in word.split("-") if s]
    text = "".join(pieces)
    w = analyze(text, voice, speed)
    rng = _split(w, len(pieces)) if len(w["f0"]) > 6 else None
    out = []
    if rng is not None:
        for a, b in rng:
            on, nu, co = _parts(w, a, b)
            out.append(dict(w=w, on=on, nu=nu, co=co))
        out[-1] = _cap_coda(out[-1], final_consonants(text, "en-gb" if voice[:1] == "b" else "en-us"))
        return out
    print(f"warning: singer: couldn't find {len(pieces)} syllables in the spoken '{text}'; speaking them one by one",
          file=sys.stderr)
    for s in pieces:
        ws = analyze(s, voice, speed)
        on, nu, co = _parts(ws, 0, len(ws["f0"]))
        out.append(dict(w=ws, on=on, nu=nu, co=co))
    return out
