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
Model files: models/tts/kokoro/ in the repo (kokoro-v1.0.onnx versioned as kokoro-v1.0.onnx.part00-06, joined and
checksum-verified on first use into the gitignored kokoro-v1.0.onnx; voices-v1.0.bin; source, licence and checksums in
models/tts/kokoro/README.md); $SPECTRE_TTS_DIR points elsewhere if they move out of the repo.
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
MODEL_SHA256 = "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"  # kokoro-v1.0.onnx


def _join_parts(path):
    """GitHub refuses files over 100 MB (and git LFS uploads are blocked from the sandbox), so the 325 MB model is
    versioned as <name>.part00, .part01, ... Join them once into <name> (atomically, checksum-verified)."""
    import glob
    parts = sorted(glob.glob(path + ".part[0-9][0-9]"))
    if not parts:
        return False
    tmp = path + f".tmp{os.getpid()}"
    h = hashlib.sha256()
    with open(tmp, "wb") as out:
        for pp in parts:
            with open(pp, "rb") as f:
                while True:
                    b = f.read(1 << 22)
                    if not b:
                        break
                    h.update(b)
                    out.write(b)
    if h.hexdigest() != MODEL_SHA256:
        os.unlink(tmp)
        raise RuntimeError(f"the joined {os.path.basename(path)} has the wrong checksum: re-fetch its parts")
    os.replace(tmp, path)
    return True

# `voice` name -> Kokoro voice. af_heart is Kokoro's flagship US-English female voice, am_michael a US-English male
# voice; `tts_voice` takes any Kokoro voice name (af_bella, af_sarah, am_adam, bf_emma, bm_george, ...)
VOICES = {"female": "af_heart", "male": "am_michael", "female2": "af_bella", "male2": "am_adam"}


def kokoro_voice(p):
    return p.get("tts_voice") or VOICES.get(p.get("voice", "female"), VOICES["female"])


@functools.lru_cache(maxsize=1)
def _model():
    paths = [os.path.join(MODEL_DIR, f) for f in MODEL_FILES]
    if not os.path.exists(paths[0]):
        _join_parts(paths[0])
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise RuntimeError(
            "singer source 'tts' needs the Kokoro model files, missing: " + ", ".join(missing) +
            f". They are versioned in models/tts/kokoro/ (the .onnx as .part00-06, joined on first use), or download "
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
    # the spoken decay after the trim (down to 60 dB under the peak, at most 300 ms): kept apart, so segmentation
    # doesn't see it, and played as the natural release when the word ends before a rest
    lo = np.where(r_db > r_db.max() - 60)[0]
    b2 = min(max(b, (lo[-1] + 1) if len(lo) else b), b + 60, n)
    decay = dict(f0=f0[b:b2], sp=sp[b:b2], ap=ap[b:b2], e=e_db[b:b2], r=r_db[b:b2], v=v_db[b:b2])
    return dict(f0=f0[a:b], sp=sp[a:b], ap=ap[a:b], e=e_db[a:b], r=r_db[a:b], v=v_db[a:b], sr=SR, freqs=freqs,
                text=text, decay=decay, off=int(a), voice=voice, speed=speed)


_KEYS = ("f0", "sp", "ap", "e", "r", "v")


def release(w, start, last, fade_ms=None):
    """Frames for a syllable's release into a rest, starting at analysis frame `start`. When the syllable is the
    last of its spoken word or phrase (`last`), the release follows the speech itself: the rest of the word after
    the coda (an open vowel's falling tail) and then the spoken decay that the analysis trimmed; it ends with a
    30 ms fade (60 ms when there is no spoken decay, after a voiced stop's release). Otherwise (a syllable inside a phrase, followed by a rest) the last frame is held and faded out over
    about 100 ms. The fade is in power on the envelope, ending 45 dB down. Cached on the analysis."""
    key = (start, bool(last), fade_ms)
    cache = w.setdefault("_rel", {})
    if key in cache:
        return cache[key]
    parts = {k: [] for k in _KEYS}
    n = len(w["f0"])
    if last:
        for k in _KEYS:
            parts[k].append(w[k][start:n])
        dec = w.get("decay")
        if dec is not None and len(dec["f0"]):
            for k in _KEYS:
                parts[k].append(dec[k])
        dec_ok = dec is not None and len(dec["f0"]) > 0
        fm = (30.0 if dec_ok else 60.0) if fade_ms is None else fade_ms  # no spoken decay (a stop's release): longer
    else:
        fm = 100.0 if fade_ms is None else fade_ms
    have = sum(len(x) for x in parts["f0"])
    if have:
        base = {k: np.concatenate(parts[k])[-1] for k in _KEYS}
    else:
        i = min(max(start - 1, 0), n - 1)
        base = {k: w[k][i] for k in _KEYS}
    K = max(2, int(round(fm / FP)))
    g = 10 ** (-45 / 10 * (np.arange(1, K + 1) / K))  # power ramp to -45 dB
    parts["f0"].append(np.full(K, base["f0"]))
    parts["sp"].append(base["sp"][None, :] * g[:, None])
    parts["ap"].append(np.repeat(base["ap"][None, :], K, 0))
    for k in ("e", "r", "v"):
        parts[k].append(base[k] + 10 * np.log10(g))
    out = {k: np.concatenate(parts[k]) for k in _KEYS}
    out["freqs"] = w["freqs"]
    out["sr"] = w["sr"]
    cache[key] = out
    return out


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


_VOICED_STOPS = set("dbɡg")
_VOICED_FRIC = set("zvðʒ")


def _voiced_coda(sy, fin, closure_ms=25, release_ms=20, release_db=-9.0):
    """Keep a word-final voiced consonant voiced. The TTS ends 'round', 'and', 'ride' with a long (about 90 ms)
    aspirated release burst, louder than the /n/ before it, that WORLD marks aperiodic; resynthesized on a sung note
    it reads as 't' ('rount and rount'). For a final voiced stop (d, b, g) the coda becomes: the nasal or vowel as
    spoken, a short voiced closure (a 'voice bar': the last voiced frame's envelope, low-passed and 15-25 dB down,
    with the pitch carried through, reached over 25 ms), then the first 20 ms of the release only, 9 dB softer and partly voiced. A final
    voiced fricative (z, v, the 'th' of 'with') keeps its frication but gets voicing below 1 kHz. Returns a new
    syllable (the analysis is copied, never changed in place); 'tail' frames are played at natural speed."""
    if not fin:
        return sy
    last = fin[-1]
    if last not in _VOICED_STOPS and last not in _VOICED_FRIC:
        return sy
    w = sy["w"]
    c0, c1 = sy["co"]
    fr = w["freqs"]
    ap_low = w["ap"][:, fr < 1000].mean(1)
    noisy = [i for i in range(c0, c1) if w["f0"][i] <= 0 or ap_low[i] > 0.5]
    if not noisy:
        return sy
    rel = noisy[0]
    voiced = [i for i in range(c0 if c0 > 0 else 0, rel) if w["f0"][i] > 0]
    if not voiced and c0 > 0:
        voiced = [c0 - 1] if w["f0"][c0 - 1] > 0 else []
    if not voiced:
        return sy
    f_carry = float(w["f0"][voiced[-1]])
    keys = ("f0", "sp", "ap", "e", "r", "v")
    if last in _VOICED_STOPS:
        cl = rel
        if rel - c0 >= 3:  # the closure: the level dip just before the burst
            lo = max(c0, rel - 6)
            cl = lo + int(np.argmin(w["r"][lo:rel + 1]))
            cl = min(cl, rel)
        base = voiced[-1] if voiced[-1] < cl else max(c0, cl - 1)
        nc = max(2, int(round(closure_ms / FP)))
        nr = max(2, int(round(release_ms / FP)))
        bar = np.where(fr < 500, 10 ** (-15 / 10), 10 ** (-25 / 10))  # power: low-passed voice bar
        new = {k: [w[k][:cl]] for k in keys}
        new["f0"].append(np.full(nc, f_carry))
        # the voicing fades into the closure (a power ramp from the nasal or vowel down to the voice bar) instead of
        # switching to it: an instant 25 dB drop reads as a cut
        u = (np.arange(1, nc + 1) / nc)[:, None]
        new["sp"].append(w["sp"][base][None, :] * bar[None, :] ** u)
        new["ap"].append(np.repeat(np.minimum(w["ap"][base], 0.3)[None, :], nc, 0))
        for k in ("e", "r", "v"):
            new[k].append(np.full(nc, w[k][base] - 15))
        r1 = min(rel + nr, len(w["f0"]))
        n_rel = r1 - rel
        fade = np.linspace(1.0, 0.25, n_rel) ** 2
        new["f0"].append(np.full(n_rel, f_carry))
        new["sp"].append(w["sp"][rel:r1] * (10 ** (release_db / 10)) * fade[:, None])
        apr = w["ap"][rel:r1].copy()
        apr[:, fr < 1500] = np.minimum(apr[:, fr < 1500], 0.4)  # a voiced, unaspirated release
        new["ap"].append(apr)
        for k in ("e", "r", "v"):
            new[k].append(w[k][rel:r1] + release_db)
        w2 = dict(w)
        for k in keys:
            w2[k] = np.concatenate(new[k])
        w2.pop("micro", None)
        w2.pop("_rel", None)
        w2["decay"] = None
        out = dict(sy, w=w2, co=(c0, cl + nc + n_rel), tail=nc + n_rel)
        return out
    # voiced fricative: carry the pitch through and give it a voiced low band, keep the frication above it
    w2 = dict(w)
    w2["f0"] = w["f0"].copy()
    w2["ap"] = w["ap"].copy()
    w2.pop("micro", None)
    w2.pop("_rel", None)
    idx = np.arange(rel, c1)
    w2["f0"][idx] = f_carry
    lowb = fr < 1000
    w2["ap"][np.ix_(idx, np.where(lowb)[0])] = np.minimum(w2["ap"][np.ix_(idx, np.where(lowb)[0])], 0.25)
    return dict(sy, w=w2)


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
        fin = final_consonants(text, "en-gb" if voice[:1] == "b" else "en-us")
        out[-1] = dict(_voiced_coda(_cap_coda(out[-1], fin), fin), last=True)
        return out
    print(f"warning: singer: couldn't find {len(pieces)} syllables in the spoken '{text}'; speaking them one by one",
          file=sys.stderr)
    for s in pieces:
        ws = analyze(s, voice, speed)
        on, nu, co = _parts(ws, 0, len(ws["f0"]))
        out.append(dict(w=ws, on=on, nu=nu, co=co, last=True))
    return out


def _tilt(w, rng):
    """Spectral tilt of frames rng of an analysis: energy 2-8 kHz against 0.1-1 kHz of the envelope (dB). Relative
    high-band energy is the clearest acoustic correlate of stress (Campbell 1995)."""
    fr = w["freqs"]
    sp = w["sp"][rng[0]:max(rng[1], rng[0] + 1)]
    hi = sp[:, (fr >= 2000) & (fr < 8000)].sum(1)
    lo = sp[:, (fr >= 100) & (fr < 1000)].sum(1)
    return float(np.mean(10 * np.log10((hi + 1e-20) / (lo + 1e-20))))


def _onf(w, on, nu):
    """Onset force: the onset's loudest frame against the vowel's mean level (dB)."""
    return float(np.max(w["r"][on[0]:on[1]]) - np.mean(w["r"][nu[0]:max(nu[1], nu[0] + 1)]))


def _feats(w):
    """Per-frame features for alignment: 24 log band energies of the spectral envelope (mel-like spacing up to
    8 kHz), voicing and level."""
    fr = w["freqs"]
    edges = 700 * (10 ** (np.linspace(np.log10(1 + 80 / 700), np.log10(1 + 8000 / 700), 25)) - 1)
    lsp = np.log(w["sp"] + 1e-20)
    bands = np.stack([lsp[:, (fr >= a) & (fr < b)].mean(1) for a, b in zip(edges[:-1], edges[1:])], 1)
    return np.concatenate([bands, 3.0 * (w["f0"] > 0)[:, None], (w["r"] / 4.0)[:, None]], 1)


def _dtw_map(A, B):
    """Dynamic time warping of feature sequences A (m frames) onto B (n frames): for each frame of A, the mean B
    frame it aligns to."""
    mu, sd = np.concatenate([A, B]).mean(0), np.concatenate([A, B]).std(0) + 1e-6
    A, B = (A - mu) / sd, (B - mu) / sd
    m, n = len(A), len(B)
    C = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(2))
    D = np.full((m + 1, n + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, m + 1):
        row = D[i]
        prev = D[i - 1]
        diag = np.minimum(prev[:-1], prev[1:])  # (i-1, j-1) and (i-1, j)
        for j in range(1, n + 1):
            row[j] = C[i - 1, j - 1] + min(diag[j - 1], row[j - 1])
    i, j = m, n
    acc = [[] for _ in range(m)]
    while i > 0 and j > 0:
        acc[i - 1].append(j - 1)
        k = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        if k == 0:
            i, j = i - 1, j - 1
        elif k == 1:
            i -= 1
        else:
            j -= 1
    return np.array([np.mean(a) if a else np.nan for a in acc])


def phrase_syllables(words, p):
    """Phrase mode: the TTS speaks the whole phrase (the words between two rests) in one go, so the joins between
    words keep their natural linking ('here-you', 'round-and'); the phrase is then cut into its syllables. words: the
    lyric words in order (hyphens mark syllables). How it cuts: each word is also spoken alone (cached), its syllable
    cuts found as in word mode, and the words in a row are aligned to the phrase by dynamic time warping on their
    spectral envelopes and voicing; every syllable and word boundary is mapped through that alignment onto the
    phrase and moved to the deepest vowel-strength dip within 20 ms. Returns the analysed syllables in order (same
    form as syllables()), or None when the phrase doesn't segment cleanly (the caller then falls back to word mode)."""
    voice = kokoro_voice(p)
    speed = float(p.get("tts_speed", 0.9))
    pieces = [[s for s in wd.split("-") if s] for wd in words]
    N = sum(len(x) for x in pieces)
    text = " ".join("".join(x) for x in pieces)
    w = analyze(text, voice, speed)
    nF = len(w["f0"])
    if nF < 4 * N:
        return None
    feats, bounds, t = [], [], 0
    cites = []  # each syllable as spoken in its word alone (citation form): the reference for `prosody`
    for x in pieces:
        ww = analyze("".join(x), voice, speed)
        rng = _split(ww, len(x)) if len(ww["f0"]) > 6 else None
        if rng is None:
            n = len(ww["f0"])
            rng = [(int(n * k / len(x)), int(n * (k + 1) / len(x))) for k in range(len(x))]
        for a_, b_ in rng:
            cites.append((ww,) + _parts(ww, a_, b_))
        if t > 0:
            bounds.append(t)  # the word boundary
        bounds += [t + a for a, _ in rng[1:]]  # syllable boundaries inside the word
        feats.append(_feats(ww))
        t += len(ww["f0"])
    mp = _dtw_map(np.concatenate(feats), _feats(w))
    v = np.where(w["f0"] > 0, w["v"], w["v"].min() - 10)
    vs = np.convolve(v, np.ones(3) / 3, mode="same")
    cuts = [0]
    for b in bounds:
        c = int(round(mp[min(b, len(mp) - 1)]))
        lo, hi = max(cuts[-1] + 3, c - 4), min(nF - 3, c + 5)
        c = lo + int(np.argmin(vs[lo:hi])) if hi > lo else max(cuts[-1] + 3, min(c, nF - 3))
        cuts.append(c)
    cuts.append(nF)
    if any(b - a < 3 for a, b in zip(cuts[:-1], cuts[1:])):
        return None
    out = []
    f0v = w["f0"][w["f0"] > 0]
    med = float(np.median(12 * np.log2(f0v / 440.0))) if len(f0v) else 0.0
    for (a, b), (ww, con, cnu, cco) in zip(zip(cuts[:-1], cuts[1:]), cites):
        on, nu, co = _parts(w, a, b)
        # the phrase's own stress on this syllable, against the same syllable spoken alone: spectral tilt (the
        # strongest acoustic cue of stress), onset force, and the pitch accent (nucleus F0 against the phrase)
        pf = w["f0"][nu[0]:nu[1]]
        acc = float(np.mean(12 * np.log2(pf[pf > 0] / 440.0)) - med) if (pf > 0).any() else 0.0
        out.append(dict(w=w, on=on, nu=nu, co=co,
                        tilt_fix=float(np.clip(_tilt(ww, cnu) - _tilt(w, nu), -8, 8)),
                        # only where the word has an onset of its own: a vowel-initial word's onset in the phrase is
                        # the previous word's linking consonant ("round-and"), which its citation form lacks
                        onf_fix=float(np.clip(_onf(ww, con, cnu) - _onf(w, on, nu), -4, 4))
                        if on[1] > on[0] and con[1] - con[0] >= 3 else 0.0,
                        accent=acc))
    fin = final_consonants("".join(pieces[-1]), "en-gb" if voice[:1] == "b" else "en-us")
    out[-1] = dict(_voiced_coda(_cap_coda(out[-1], fin), fin), last=True)
    return out
