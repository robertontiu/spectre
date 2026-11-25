"""`singer` `"source": "svs"` voices whose bank has `"engine": "soulx"`: SoulX-Singer (Soul AI Lab, Apache 2.0, code and
weights), a zero-shot singing synthesizer. It sings words on notes like the DiffSinger banks, but its voice is not
trained in: it continues a short reference recording (the "prompt"), so the timbre is the prompt singer's. That is how
the engine gets male voices: the prompts are two male singers of VocalSet (CC BY 4.0; engine/soulx_prompts.json).

Score control: the engine gives words (CMUdict phonemes with stress), one or more notes per word and their lengths;
the model draws the pitch curve and the timing inside each word. Left alone it sings notes 10-60 cents off (measured:
mean 17-22 cents on the audition line, the first note up to 60 sharp), so by default (`tune` 1) a phrase is sung twice:
a quick first pass in score control gives a natural pitch curve, each note of that curve is moved so that its median
sits on the written pitch (scoops, transitions and vibrato are kept), and the final pass follows the corrected curve
(SoulX's melody control). Mean deviation after: about 8 cents. `svs_tune` 0 is the single pass.
Rendering is seeded (torch.manual_seed per phrase) and phrase-cached by svs.take like every svs voice. English only
here (the model also sings Mandarin and Cantonese).

Slow on CPU: on 2 threads a 6 s phrase takes about 100 s with tuning (75 s without), once; then it is cached. About
3-5 GB of RAM while loaded. Output is 24 kHz (nothing above 12 kHz), resampled to 44.1 kHz.

Files, never in git: ~/.cache/spectre/svs/soulx/{repo, weights/model.pt, prompts/<id>.wav}. Set them up with
    python3 engine/svs_soulx.py setup
Needs: pip install torch (CPU build), omegaconf, cmudict, librosa, soundfile. The two classes SoulX takes from
`transformers` (Llama decoder layers, as in transformers 4.41) are provided here, so `transformers` is not needed.
"""
import io
import json
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SVS_DIR = os.path.expanduser(os.environ.get("SPECTRE_SVS_DIR", "~/.cache/spectre/svs"))
ROOT = os.path.join(SVS_DIR, "soulx")
REPO_URL = "https://github.com/Soul-AILab/SoulX-Singer"
REPO_COMMIT = "81aeb3ae772c70093c3de74dc23c92d983801ae4"  # 2026-05-29
MODEL_URL = "https://huggingface.co/Soul-AILab/SoulX-Singer/resolve/main/model.pt"
MODEL_BYTES = 2818092278
SX_SR = 24000
HOP = 480
VERSION = 1  # bump when the rendering changes: part of every phrase cache key
STEPS = 16
CFG = 3.0
HEAD_S = 0.3  # silence (<SP>) before the first word of a phrase
TAIL_S = 0.3
PROMPT_PEAK = 0.5
_STATE = {}


def _warn(msg):
    print(f"warning: singer svs (soulx): {msg}", file=sys.stderr)


def prompts():
    return json.load(open(os.path.join(HERE, "soulx_prompts.json"), encoding="utf-8"))


# ------------------------------------------------------------------------------------------------ transformers shim
def _install_shim():
    """SoulX's flow-matching transformer subclasses two `transformers` classes. Their 4.41 behaviour, in torch only."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class LlamaConfig:
        def __init__(self, vocab_size=32000, hidden_size=4096, intermediate_size=11008, num_hidden_layers=32,
                     num_attention_heads=32, max_position_embeddings=2048, rms_norm_eps=1e-6, rope_theta=10000.0,
                     **kw):
            self.vocab_size, self.hidden_size, self.intermediate_size = vocab_size, hidden_size, intermediate_size
            self.num_hidden_layers, self.num_attention_heads = num_hidden_layers, num_attention_heads
            self.max_position_embeddings, self.rms_norm_eps = max_position_embeddings, rms_norm_eps
            self.rope_theta = rope_theta
            self.output_attentions = self.output_hidden_states = self.use_cache = False

    class Attention(nn.Module):  # LlamaAttention: no biases, rotary position embedding on queries and keys
        def __init__(self, c):
            super().__init__()
            self.h, self.d, self.theta = c.num_attention_heads, c.hidden_size // c.num_attention_heads, c.rope_theta
            self.q_proj = nn.Linear(c.hidden_size, c.hidden_size, bias=False)
            self.k_proj = nn.Linear(c.hidden_size, c.hidden_size, bias=False)
            self.v_proj = nn.Linear(c.hidden_size, c.hidden_size, bias=False)
            self.o_proj = nn.Linear(c.hidden_size, c.hidden_size, bias=False)

        def forward(self, hidden_states, attention_mask=None, position_ids=None, **kw):
            b, t, _ = hidden_states.shape
            q, k, v = (p(hidden_states).view(b, t, self.h, self.d).transpose(1, 2)
                       for p in (self.q_proj, self.k_proj, self.v_proj))
            inv = 1.0 / (self.theta ** (torch.arange(0, self.d, 2, dtype=torch.float32, device=q.device) / self.d))
            fr = position_ids[:, :, None].float() * inv[None, None, :]
            emb = torch.cat((fr, fr), dim=-1)
            cos, sin = emb.cos()[:, None].to(q.dtype), emb.sin()[:, None].to(q.dtype)

            def rot(x):
                return torch.cat((-x[..., x.shape[-1] // 2:], x[..., :x.shape[-1] // 2]), dim=-1)
            q, k = q * cos + rot(q) * sin, k * cos + rot(k) * sin
            o = F.scaled_dot_product_attention(q, k, v, attn_mask=attention_mask)
            return self.o_proj(o.transpose(1, 2).reshape(b, t, -1)), None, None

    class MLP(nn.Module):
        def __init__(self, c):
            super().__init__()
            self.gate_proj = nn.Linear(c.hidden_size, c.intermediate_size, bias=False)
            self.up_proj = nn.Linear(c.hidden_size, c.intermediate_size, bias=False)
            self.down_proj = nn.Linear(c.intermediate_size, c.hidden_size, bias=False)

        def forward(self, x):
            return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))

    class LlamaDecoderLayer(nn.Module):
        def __init__(self, config, layer_idx=0):
            super().__init__()
            self.self_attn, self.mlp = Attention(config), MLP(config)

    class LlamaModel(nn.Module):
        def __init__(self, config):
            super().__init__()
            self.config, self.gradient_checkpointing = config, False

        def post_init(self):
            pass

    t = types.ModuleType("transformers")
    t._spectre_shim = True
    t.LlamaConfig, t.LlamaModel = LlamaConfig, LlamaModel
    t.WhisperFeatureExtractor = t.WhisperModel = None  # only the SVC model uses them
    mm = types.ModuleType("transformers.models.llama.modeling_llama")
    mm.LlamaDecoderLayer, mm.BaseModelOutputWithPast = LlamaDecoderLayer, object
    return {"transformers": t, "transformers.models": types.ModuleType("transformers.models"),
            "transformers.models.llama": types.ModuleType("transformers.models.llama"),
            "transformers.models.llama.modeling_llama": mm, "accelerate": types.ModuleType("accelerate")}


def _engine():
    """(model, data processor), loaded once. The SoulX modules are imported with the shim in place of `transformers`
    and `accelerate`; whatever those names were in sys.modules before is put back afterwards."""
    if "model" in _STATE:
        return _STATE["model"], _STATE["proc"]
    repo, weights = os.path.join(ROOT, "repo"), os.path.join(ROOT, "weights", "model.pt")
    if not (os.path.isdir(os.path.join(repo, "soulxsinger")) and os.path.exists(weights)):
        raise FileNotFoundError(f"SoulX-Singer is not installed under {ROOT}: run `python3 engine/svs_soulx.py setup` "
                                "(docs/voice/VOICES.md, 'Male voices')")
    import torch
    torch.set_num_threads(int(os.environ.get("SPECTRE_SVS_THREADS", "2")))
    shim = _install_shim()
    saved = {k: sys.modules.get(k) for k in shim}
    sys.modules.update(shim)
    sys.path.insert(0, repo)
    try:
        from soulxsinger.models.soulxsinger import SoulXSinger
        from soulxsinger.utils.data_processor import DataProcessor
        from soulxsinger.utils.file_utils import load_config
    finally:
        sys.path.remove(repo)
        for k, m in saved.items():
            if m is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = m
    cfg = load_config(os.path.join(repo, "soulxsinger", "config", "soulxsinger.yaml"))
    model = SoulXSinger(cfg)
    try:  # mmap + assign: the 2.8 GB of weights are not held twice
        ck = torch.load(weights, weights_only=False, map_location="cpu", mmap=True)
        model.load_state_dict(ck["state_dict"], strict=True, assign=True)
    except (TypeError, RuntimeError):
        ck = torch.load(weights, weights_only=False, map_location="cpu")
        model.load_state_dict(ck["state_dict"], strict=True)
    del ck
    model.eval()
    proc = DataProcessor(hop_size=cfg.audio.hop_size, sample_rate=cfg.audio.sample_rate, device="cpu",
                         phoneset_path=os.path.join(repo, "soulxsinger", "utils", "phoneme", "phone_set.json"))
    _STATE.update(model=model, proc=proc)
    return model, proc


def _meta(rows):
    """rows: [(text, phoneme, midi, type, seconds)] -> SoulX metadata (one entry per note; rests are <SP>, type 1)."""
    return {"duration": " ".join(f"{r[4]:.4f}" for r in rows), "text": " ".join(r[0] for r in rows),
            "phoneme": " ".join(r[1] for r in rows), "note_pitch": " ".join(str(int(r[2])) for r in rows),
            "note_type": " ".join(str(int(r[3])) for r in rows)}


def _prompt(pid):
    """The processed prompt (reference recording with its words and notes) for a prompt id."""
    key = ("prompt", pid)
    if key in _STATE:
        return _STATE[key]
    spec = prompts()["prompts"][pid]
    path = os.path.join(ROOT, "prompts", pid + ".wav")
    if not os.path.exists(path):
        raise FileNotFoundError(f"SoulX prompt {pid!r} not found at {path}: run `python3 engine/svs_soulx.py setup`")
    import soundfile as sf
    import torch
    _, proc = _engine()
    w, sr = sf.read(path, dtype="float32")
    if sr != SX_SR or w.ndim != 1:
        raise ValueError(f"{path}: expected mono {SX_SR} Hz")
    rows = [(n[0], _phones(n[0]) if n[0] != "<SP>" else "<SP>", n[1], n[2], n[3]) for n in spec["notes"]]
    item = proc.process(_meta(rows), None)
    n = item["mel2note"].shape[1]
    w = np.pad(w, (0, max(0, n * HOP - len(w))))[:n * HOP]
    item["waveform"] = torch.from_numpy(w / max(np.abs(w).max(), 1e-9) * PROMPT_PEAK)[None, :]
    item["f0"] = torch.from_numpy(_f0(w, n))[None, :]  # for melody control (the tuned pass)
    _STATE[key] = item
    return item


def _f0(y, n):
    """Hz per SoulX frame (20 ms) of a 24 kHz signal, 0 where unvoiced; n frames."""
    import pyworld as pw
    f0, _ = pw.harvest(np.asarray(y, dtype=np.float64), SX_SR, f0_floor=60.0, f0_ceil=1000.0, frame_period=20.0)
    return np.pad(f0, (0, max(0, n - len(f0))))[:n].astype(np.float32)


def _tuned(f0, rows, amount):
    """The pitch curve of a first pass with every note moved towards its written pitch: the median deviation over
    25-90% of the note, times `amount`, taken off the whole note; the steps between notes smoothed over 60 ms."""
    from scipy.ndimage import gaussian_filter1d
    corr, t, fps = np.zeros(len(f0)), 0.0, SX_SR / HOP
    for (_, ph, m, _, d) in rows:
        if ph != "<SP>" and m > 0:
            v = f0[int((t + 0.25 * d) * fps):int((t + 0.9 * d) * fps)]
            v = v[v > 0]
            if len(v) > 2:
                corr[int(t * fps):int((t + d) * fps)] = np.median(1200 * np.log2(v / (440 * 2 ** ((m - 69) / 12))))
        t += d
    corr = gaussian_filter1d(corr, 3) * amount
    return np.where(f0 > 0, f0 * 2 ** (-corr / 1200), 0).astype(np.float32)


# ------------------------------------------------------------------------------------------------ words
def _cmu():
    if "cmu" not in _STATE:
        import cmudict
        _STATE["cmu"] = cmudict.dict()
    return _STATE["cmu"]


def _phones(word):
    """A word as SoulX writes it: en_ + CMUdict phonemes with stress, joined by '-'. Unknown words: each hyphen part
    on its own, then 'ah'."""
    w = word.lower().strip(",.!?;:'\"")
    d = _cmu()
    pr = d.get(w.replace("-", ""))
    if pr:
        return "en_" + "-".join(pr[0])
    out = []
    for part in [x for x in w.split("-") if x]:
        pp = d.get(part)
        if not pp:
            _warn(f"word {word!r} not in the dictionary: sung as 'ah'")
            pp = [["AA1"]]
        out += pp[0]
    return "en_" + "-".join(out or ["AA1"])


def render(v, info, words, ns, seed, steps=STEPS, cfg=CFG, tune=1.0):
    """One phrase. words: the phrase's syllable tokens [(word, syllable index, syllable count)] as svs.take has them;
    ns: [(start_ms, dur_ms, midi, token index)] contiguous. Returns (wave at 44.1 kHz, t0_ms).
    SoulX works per word: every note of a word carries the whole word's phonemes, the first as a word start (type 2),
    the others as continuations (type 3); the model places the syllables. tune > 0: two passes (module docstring)."""
    import torch
    from scipy.signal import resample_poly
    model, proc = _engine()
    prompt = _prompt(v["prompt"])
    # syllable tokens -> words: a token with syllable index 0 starts a new word
    word_of, wi = [], -1
    for (word, si, n) in words:
        if si == 0 or wi < 0:
            wi += 1
        word_of.append(wi)
    names = {}
    for k, (word, si, n) in enumerate(words):
        names.setdefault(word_of[k], word)
    rows, seen = [("<SP>", "<SP>", 0, 1, HEAD_S)], set()
    for (a, d, m, k) in ns:
        w = word_of[k]
        text = names[w].replace("-", "")
        rows.append((text, _phones(names[w]), int(round(m)), 3 if w in seen else 2, d / 1000.0))
        seen.add(w)
    rows.append(("<SP>", "<SP>", 0, 1, TAIL_S))
    target = proc.process(_meta(rows), None)

    def run(tg, n_steps, control):
        torch.manual_seed(int(seed) % (2 ** 31))
        with torch.no_grad():
            out = model.infer({"prompt": prompt, "target": tg}, auto_shift=False, pitch_shift=0, n_steps=int(n_steps),
                              cfg=float(cfg), control=control)
        return out.squeeze().float().numpy()
    if tune > 0:
        first = run(target, max(8, int(steps) // 2), "score")
        n = target["mel2note"].shape[1]
        target = dict(target, f0=torch.from_numpy(_tuned(_f0(first, n), rows, float(tune)))[None, :])
        y = run(target, steps, "melody")
    else:
        y = run(target, steps, "score")
    wav = resample_poly(y, 147, 80).astype(np.float32)  # 24 kHz -> 44.1 kHz
    return wav, ns[0][0] - HEAD_S * 1000.0


# ------------------------------------------------------------------------------------------------ setup
class _RemoteFile(io.RawIOBase):
    """A remote file read by HTTP range requests: zipfile can take single members out of a large archive."""

    def __init__(self, url):
        import urllib.request
        self.rq, self.url, self.pos = urllib.request, url, 0
        self.size = int(self.rq.urlopen(self.rq.Request(url, method="HEAD")).headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, o, w=0):
        self.pos = o if w == 0 else self.pos + o if w == 1 else self.size + o
        return self.pos

    def readinto(self, b):
        n = min(len(b), self.size - self.pos)
        if n <= 0:
            return 0
        req = self.rq.Request(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"})
        d = self.rq.urlopen(req).read()
        b[:len(d)] = d
        self.pos += len(d)
        return len(d)


def setup():
    """Clone SoulX-Singer at the pinned commit, download its weights (2.8 GB) and cut the prompts out of VocalSet
    (only the members needed are read from the 2 GB archive)."""
    import subprocess
    import zipfile
    import librosa
    import soundfile as sf
    os.makedirs(os.path.join(ROOT, "weights"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "prompts"), exist_ok=True)
    repo = os.path.join(ROOT, "repo")
    if not os.path.isdir(os.path.join(repo, "soulxsinger")):
        subprocess.run(["git", "clone", "-q", REPO_URL, repo], check=True)
        subprocess.run(["git", "-C", repo, "checkout", "-q", REPO_COMMIT], check=True)
    weights = os.path.join(ROOT, "weights", "model.pt")
    if not (os.path.exists(weights) and os.path.getsize(weights) == MODEL_BYTES):
        subprocess.run(["curl", "-L", "-C", "-", "-o", weights, MODEL_URL], check=True)
    ps = prompts()
    todo = {pid: s for pid, s in ps["prompts"].items()
            if not os.path.exists(os.path.join(ROOT, "prompts", pid + ".wav"))}
    by_url = {}
    for pid, s in todo.items():
        by_url.setdefault(ps["sources"][s["source"]]["archive"], []).append((pid, s))
    for url, items in by_url.items():
        z = zipfile.ZipFile(io.BufferedReader(_RemoteFile(url), buffer_size=1 << 20))
        for pid, s in items:
            x, sr = sf.read(io.BytesIO(z.read(s["member"])), dtype="float32")
            x = x.mean(1) if x.ndim > 1 else x
            a, b = int(s["cut_s"][0] * sr), int(s["cut_s"][1] * sr)
            y = librosa.resample(x[a:b], orig_sr=sr, target_sr=SX_SR)
            f = int(0.01 * SX_SR)
            y[:f] *= np.linspace(0, 1, f)
            y[-f:] *= np.linspace(1, 0, f)
            sf.write(os.path.join(ROOT, "prompts", pid + ".wav"), y, SX_SR, subtype="PCM_16")
            print(f"prompt {pid}: {s['member']} {s['cut_s']} s")
    print("SoulX-Singer ready under", ROOT)


if __name__ == "__main__":
    if sys.argv[1:] == ["setup"]:
        setup()
    else:
        print(__doc__)
