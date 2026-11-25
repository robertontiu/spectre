"""svs voices with a `"convert"` entry in voices.json: a phrase sung by another svs voice (Hanami: timing and diction
the catalogue trusts, English and Spanish) and made male. docs/voice/VOICES.md "Male voices from Hanami" has the
research, the licences, the consent basis of every target and the measurements; examples/vocals/svs/svc.py the study.

The source voice sings the written line `sing` semitones higher (12: where its bank was trained); what comes after is
one of two things.

`"route": "synth"` (`hanami-male`, `hanami-male-es`): no second model and no target person. The duration and pitch
models work at the upper octave, the pitch curve is moved down (`f0_shift`, inside the synthesizer: svs.Bank.render)
before the acoustic model and the vocoder, and the voice's `gender` (-0.2) lowers the formants. `formant` (1.0 = off,
the wired setting) adds `formant_filter` on the rendered voice: formants moved by a ratio, pitch left alone. Both steps
are what Lotte V's terms name as allowed (a derivative voice "through settings contained within the synthesis
software itself"; "formant filter effects applied to the rendered voice").

`"route": "svc"` (`male-svc`, `male-svc-es`): SoulX-Singer-SVC (Soul AI Lab, Apache 2.0, code and weights), a
zero-shot singing voice converter. It keeps the source's words, timing and melody (moved down by `sing` semitones)
and takes the timbre from a short reference recording, the `target`. A target is a consent question (cloning a real
person who did not agree is the problem the VocalSet voices have), so every target states whose voice it is and on
what basis it is used, in `engine/soulx_prompts.json` ("svc_targets"). Output is 24 kHz (nothing above 12 kHz),
resampled to 44.1 kHz. About 85 s per phrase on 2 CPU threads, 5.3 GB of RAM. `"source_low": true` (the study's
variant) sings the source low in the synthesizer first and converts without a shift.

Everything is seeded and deterministic; svs.take caches the converted phrase like any other.
Files, never in git: ~/.cache/spectre/svs/soulx/{repo, weights/model-svc.pt, whisper/, targets/<id>.wav}. Set up with
    python3 engine/svs_convert.py setup
Needs for `svc`: torch (CPU build), omegaconf, transformers (any recent version: only its Whisper encoder is used),
pyworld. `synth` with `formant` 1.0 needs nothing beyond the DiffSinger packages (the filter: pyworld, scipy).
"""
import gc
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
SX_SR = 24000
VERSION = 1  # bump when a conversion changes: part of every converted phrase's cache key
SVC_URL = "https://huggingface.co/Soul-AILab/SoulX-Singer/resolve/main/model-svc.pt"
SVC_BYTES = 2793965154
SVC_STEPS = 16
SVC_CFG = 3.0
TARGET_PEAK = 0.5
_STATE = {}


def _warn(msg):
    print(f"warning: singer svs (convert): {msg}", file=sys.stderr)


def _root():
    import svs_soulx
    return svs_soulx.ROOT


# ------------------------------------------------------------------------------------------------ formants (no model)
def _warp(sp, ratio):
    """A WORLD spectral envelope (frames x bins) with its frequency axis scaled: what was at f is at f * ratio."""
    n = sp.shape[1]
    src = np.arange(n) / ratio
    lo = np.clip(np.floor(src).astype(int), 0, n - 1)
    hi = np.clip(lo + 1, 0, n - 1)
    w = np.clip(src - lo, 0.0, 1.0)
    logsp = np.log(sp + 1e-16)
    return np.exp(logsp[:, lo] * (1 - w) + logsp[:, hi] * w)


def formant_filter(y, ratio, sr=SR, limit_db=24.0):
    """Move the formants of a voice by `ratio` (below 1: down, a longer vocal tract) and leave its pitch, timing and
    harmonics alone. The spectral envelope of every 5 ms frame is measured (WORLD CheapTrick), the gain between the
    scaled envelope and the measured one is applied to the signal's short-time spectrum (a time-varying filter; the
    voice is not resynthesized, so there is no vocoder buzz)."""
    if abs(ratio - 1.0) < 1e-6:
        return np.asarray(y, dtype=np.float32)
    import pyworld as pw
    from scipy.ndimage import gaussian_filter
    from scipy.signal import istft, stft
    x = np.asarray(y, dtype=np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=60.0, f0_ceil=1100.0, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr)
    gain = 10 * np.log10(_warp(sp, ratio) / (sp + 1e-16) + 1e-16)
    gain = np.clip(gaussian_filter(gain, (1.5, 2.0)), -limit_db, limit_db)
    nfft, hop = sp.shape[1] * 2 - 2, 256
    _, tt, z = stft(x, sr, nperseg=nfft, noverlap=nfft - hop, window="hann")
    idx = np.clip(np.searchsorted(t, tt), 0, len(t) - 1)
    z *= 10 ** (gain[idx].T / 20)
    _, out = istft(z, sr, nperseg=nfft, noverlap=nfft - hop, window="hann")
    out = np.pad(out, (0, max(0, len(x) - len(out))))[:len(x)]
    return out.astype(np.float32)


def world_shift(y, semitones, ratio, sr=SR):
    """Pitch and formants moved by analysis and resynthesis (WORLD): the classic DSP gender change, here only as the
    study's comparison (examples/vocals/svs/svc.py). It pitch-shifts rendered audio, which Lotte V's terms don't
    allow as a way to make a derivative voice, and it resynthesizes, which adds the vocoder's buzz."""
    import pyworld as pw
    x = np.asarray(y, dtype=np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=60.0, f0_ceil=1100.0, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr)
    ap = pw.d4c(x, f0, t, sr)
    out = pw.synthesize(f0 * 2 ** (semitones / 12.0), np.ascontiguousarray(_warp(sp, ratio)), ap, sr, 5.0)
    return np.pad(out, (0, max(0, len(x) - len(out))))[:len(x)].astype(np.float32)


# ------------------------------------------------------------------------------------------------ SoulX-Singer-SVC
def _f0(y, n=None):
    """Hz per SoulX frame (20 ms) of a 24 kHz signal, 0 where unvoiced."""
    import pyworld as pw
    f0, _ = pw.harvest(np.asarray(y, dtype=np.float64), SX_SR, f0_floor=60.0, f0_ceil=1100.0, frame_period=20.0)
    if n is not None:
        f0 = np.pad(f0, (0, max(0, n - len(f0))))[:n]
    return f0.astype(np.float32)


def _svc():
    """The SVC model, loaded once. The SoulX modules are imported with svs_soulx's stand-in for the `transformers`
    Llama classes (as the male SoulX voices do); only the Whisper encoder comes from the real `transformers`.
    The singing model of svs_soulx is dropped first: the two don't fit in memory together on a small machine."""
    if "model" in _STATE:
        return _STATE["model"]
    import svs_soulx
    root = _root()
    repo, weights = os.path.join(root, "repo"), os.path.join(root, "weights", "model-svc.pt")
    if not (os.path.isdir(os.path.join(repo, "soulxsinger")) and os.path.exists(weights)):
        raise FileNotFoundError(f"SoulX-Singer-SVC is not installed under {root}: run "
                                "`python3 engine/svs_convert.py setup` (docs/voice/VOICES.md, 'Male voices from Hanami')")
    if svs_soulx._STATE:
        svs_soulx._STATE.clear()
        gc.collect()
    import torch
    import transformers as real
    torch.set_num_threads(int(os.environ.get("SPECTRE_SVS_THREADS", "2")))
    wdir = os.path.join(root, "whisper")
    fe_cls, wm_cls = real.WhisperFeatureExtractor, real.WhisperModel

    class _FE:
        @staticmethod
        def from_pretrained(name, **kw):
            return fe_cls.from_pretrained(name, cache_dir=wdir)

    class _WM:
        @staticmethod
        def from_pretrained(name, **kw):
            m = wm_cls.from_pretrained(name, cache_dir=wdir)
            m.decoder = None  # only the encoder is used
            return m.eval()

    shim = svs_soulx._install_shim()
    shim["transformers"].WhisperFeatureExtractor, shim["transformers"].WhisperModel = _FE, _WM
    saved = {k: sys.modules.get(k) for k in shim}
    sys.modules.update(shim)
    sys.path.insert(0, repo)
    try:
        from soulxsinger.models.soulxsinger_svc import SoulXSingerSVC
        from soulxsinger.utils.file_utils import load_config
    finally:
        sys.path.remove(repo)
        for k, m in saved.items():
            if m is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = m
    cfg = load_config(os.path.join(repo, "soulxsinger", "config", "soulxsinger.yaml"))
    model = SoulXSingerSVC(cfg)
    try:  # mmap + assign: the 2.8 GB of weights are not held twice
        ck = torch.load(weights, weights_only=False, map_location="cpu", mmap=True)
        model.load_state_dict(ck["state_dict"], strict=True, assign=True)
    except (TypeError, RuntimeError):
        ck = torch.load(weights, weights_only=False, map_location="cpu")
        model.load_state_dict(ck["state_dict"], strict=True)
    del ck
    model.eval()
    _STATE["model"] = model
    return model


def drop():
    """Free the SVC model (svs.take calls this before a SoulX-Singer voice renders: one large model at a time)."""
    if _STATE:
        _STATE.clear()
        gc.collect()


def targets():
    return json.load(open(os.path.join(HERE, "soulx_prompts.json"), encoding="utf-8")).get("svc_targets", {})


def _target(tid):
    """(wave, f0) tensors of a conversion target: ~/.cache/spectre/svs/soulx/targets/<id>.wav (24 kHz mono), made by
    `setup` from the recipe in soulx_prompts.json."""
    key = ("target", tid)
    if key in _STATE:
        return _STATE[key]
    import soundfile as sf
    import torch
    path = os.path.join(_root(), "targets", tid + ".wav")
    if not os.path.exists(path):
        if targets().get(tid, {}).get("make") == "engine":
            make_target(tid)
        else:
            raise FileNotFoundError(f"conversion target {tid!r} not found at {path}: run "
                                    "`python3 engine/svs_convert.py setup`")
    w, sr = sf.read(path, dtype="float32")
    if sr != SX_SR or w.ndim != 1:
        raise ValueError(f"{path}: expected mono {SX_SR} Hz")
    w = w / max(np.abs(w).max(), 1e-9) * TARGET_PEAK
    out = (torch.from_numpy(w)[None, :], torch.from_numpy(_f0(w))[None, :])
    _STATE[key] = out
    return out


def soulx_svc(y, target, pitch_shift=0, seed=1, steps=SVC_STEPS, cfg=SVC_CFG):
    """A 44.1 kHz phrase converted to the target's timbre, its melody moved by `pitch_shift` semitones (whole
    numbers: the model's pitch grid is 20 cents). Returns 44.1 kHz, the same length."""
    import torch
    from scipy.signal import resample_poly
    model = _svc()
    pt_wav, pt_f0 = _target(target)
    x = resample_poly(np.asarray(y, dtype=np.float64), 80, 147).astype(np.float32)
    peak = max(np.abs(x).max(), 1e-9)
    x = x / peak * TARGET_PEAK
    gt_f0 = torch.from_numpy(_f0(x, len(x) // 480 + 1))[None, :]
    torch.manual_seed(int(seed) % (2 ** 31))
    with torch.no_grad():
        out, _ = model.infer(pt_wav=pt_wav, gt_wav=torch.from_numpy(x)[None, :], pt_f0=pt_f0, gt_f0=gt_f0,
                             auto_shift=False, pitch_shift=int(pitch_shift), n_steps=int(steps), cfg=float(cfg))
    out = resample_poly(out.squeeze().float().numpy(), 147, 80).astype(np.float32)
    n = len(y)
    return np.pad(out, (0, max(0, n - len(out))))[:n]


# ------------------------------------------------------------------------------------------------ the engine's hook
def source_render_args(conv):
    """(semitones the source voice sings above the written notes, in-synth pitch offset)."""
    sing = int(conv.get("sing", 12))
    synth = conv.get("route", "synth") == "synth" or conv.get("source_low")
    return sing, (-float(sing) if synth else 0.0)


def apply(conv, wav, seed, steps=None):
    """The conversion after the source phrase is rendered. conv: a voice's `"convert"` entry."""
    route = conv.get("route", "synth")
    if route == "synth":
        return formant_filter(wav, float(conv.get("formant", 1.0)))
    if route == "svc":
        if conv.get("source_low"):  # the source was already sung low in the synthesizer: convert without a shift
            wav = formant_filter(wav, float(conv.get("formant", 1.0)))
            shift = 0
        else:
            shift = -int(conv.get("sing", 12))
        return soulx_svc(wav, conv["target"], shift, seed, steps=steps or int(conv.get("steps", SVC_STEPS)),
                         cfg=float(conv.get("cfg", SVC_CFG)))
    raise ValueError(f"unknown convert route {route!r}")


# ------------------------------------------------------------------------------------------------ targets, setup
def make_target(tid):
    """Write a target's 24 kHz reference recording from its recipe (soulx_prompts.json, "svc_targets")."""
    import soundfile as sf
    from scipy.signal import resample_poly
    spec = targets()[tid]
    os.makedirs(os.path.join(_root(), "targets"), exist_ok=True)
    path = os.path.join(_root(), "targets", tid + ".wav")
    if spec["make"] == "engine":  # a line sung by one of the engine's own voices: a synthetic target, nobody's voice
        import singer
        from hand import note_to_midi
        q = 60.0 / float(spec.get("bpm", 100)) / 4
        t, ns = 0.2, []
        for tok in spec["melody"].split():
            name, ln = tok.split(":")
            if name != "r":
                ns.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), vel=0.9, glide=False,
                               f=440 * 2 ** ((note_to_midi(name) - 69) / 12)))
            t += float(ln) * q
        y = singer.sing({"source": "svs", "voice": spec["voice"], "lyrics": spec["lyrics"], "seed": 1}, ns,
                        int((t + 0.3) * SR))
        y = resample_poly(np.asarray(y, dtype=np.float64), 80, 147)
    elif spec["make"] == "download":  # recordings given for voice synthesis: fetched, cut and joined
        import io
        import urllib.request
        import librosa
        parts = []
        for url in spec["files"]:
            x, sr = sf.read(io.BytesIO(urllib.request.urlopen(url, timeout=60).read()), dtype="float32")
            x = x.mean(1) if x.ndim > 1 else x
            x, _ = librosa.effects.trim(x, top_db=35)
            x = x[:int(float(spec.get("each_s", 60.0)) * sr)]
            x[-int(0.02 * sr):] *= np.linspace(1, 0, int(0.02 * sr))
            parts += [librosa.resample(x, orig_sr=sr, target_sr=SX_SR), np.zeros(int(0.15 * SX_SR), np.float32)]
        y = np.concatenate(parts)[:int(float(spec.get("max_s", 9.0)) * SX_SR)]
    else:
        raise ValueError(f"target {tid!r}: unknown recipe {spec['make']!r}")
    y = np.asarray(y, dtype=np.float32)
    f = int(0.01 * SX_SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    sf.write(path, y / max(np.abs(y).max(), 1e-9) * 0.89, SX_SR, subtype="PCM_16")
    return path


def setup():
    """SoulX-Singer's code (svs_soulx.setup's clone), the SVC weights (2.8 GB), the Whisper-base encoder it listens
    with (0.3 GB, into the same folder) and the conversion targets."""
    import subprocess
    import svs_soulx
    root = _root()
    os.makedirs(os.path.join(root, "weights"), exist_ok=True)
    repo = os.path.join(root, "repo")
    if not os.path.isdir(os.path.join(repo, "soulxsinger")):
        subprocess.run(["git", "clone", "-q", svs_soulx.REPO_URL, repo], check=True)
        subprocess.run(["git", "-C", repo, "checkout", "-q", svs_soulx.REPO_COMMIT], check=True)
    weights = os.path.join(root, "weights", "model-svc.pt")
    if not (os.path.exists(weights) and os.path.getsize(weights) == SVC_BYTES):
        subprocess.run(["curl", "-L", "-C", "-", "-o", weights, SVC_URL], check=True)
    _svc()
    for tid in targets():
        if not os.path.exists(os.path.join(root, "targets", tid + ".wav")):
            print("target", tid, make_target(tid))
    print("SoulX-Singer-SVC ready under", root)


if __name__ == "__main__":
    if sys.argv[1:] == ["setup"]:
        setup()
    else:
        print(__doc__)
