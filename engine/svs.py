"""`singer` `"source": "svs"`: words sung by a singing voice synthesizer (DiffSinger, OpenVPI ONNX voicebanks as
OpenUtau uses them).

A neural model trained on a singer's recordings sings the line in one piece: its duration model sets each phoneme's
length, its pitch model draws the f0 (scoops, transitions, vibrato) around the notes, its acoustic model and a vocoder
make the sound. The engine only gives it the words, the notes and the voice; it does not stitch anything.

The code path follows OpenUtau (OpenUtau.Core/DiffSinger: DiffSingerBasePhonemizer.ProcessPart, DiffSingerPitch,
DiffSingerRenderer) with OpenUtau's defaults, plus: a closing SP token after each phrase (DiffSinger's training phrases
end in SP; without it a final consonant can hang for half a second), an optional breath (AP) before a phrase, and the
diffusion noise fed from a seeded generator instead of onnxruntime's own, so every phrase renders bit for bit the same
regardless of what was rendered before (the models are patched once: their RandomNormalLike node becomes an input).

Voices are listed in engine/voices.json (id, bank, vocal mode, licence, credit, tags); docs/voice/VOICES.md describes
them. Model files never go in the repo: banks live in ~/.cache/spectre/svs/<bank>/bank/ (SPECTRE_SVS_DIR moves it),
rendered phrases in ~/.cache/spectre/svs/phrases/ (safe to delete; they regenerate identically).
Needs: pip install onnxruntime onnx cmudict pyyaml.
"""
import hashlib
import json
import os
import sys

import numpy as np

SR = 44100
PAD_MS = 500.0  # OpenUtau: room for the consonants before the first note
HEAD_FR = TAIL_FR = 8
VERSION = 2  # bump when the rendering changes: part of every phrase cache key
LANG_VERSION = 1  # bump when a non-English G2P (lang_es.py) changes: part of those phrases' cache keys
HERE = os.path.dirname(os.path.abspath(__file__))
SVS_DIR = os.path.expanduser(os.environ.get("SPECTRE_SVS_DIR", "~/.cache/spectre/svs"))
PHRASES = os.path.join(SVS_DIR, "phrases")


def _warn(msg):
    print(f"warning: singer svs: {msg}", file=sys.stderr)


def voices():
    return json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))


def voice_spec(p):
    """The voice for a track: `svs_voice` or `voice` (an id from voices.json), default the first listed."""
    vs = voices()
    vid = p.get("svs_voice") or p.get("voice")
    byid = {v["id"]: v for v in vs["voices"]}
    if vid in ("female", None):
        vid = vs["default"]
    if vid not in byid:
        _warn(f"unknown svs voice {vid!r}; using {vs['default']} (voices: {', '.join(byid)})")
        vid = vs["default"]
    return byid[vid], vs["banks"]


# ------------------------------------------------------------------------------------------------ helpers
def _yaml(path):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8"))


def _entries(path):
    out = {}
    if os.path.exists(path):
        for e in _yaml(path).get("entries") or []:
            out[str(e["grapheme"]).lower()] = list(e["phonemes"])
    return out


def frames_from_ms(durs_ms, frame_ms):
    """OpenUtau DiffSingerUtils.DurationsMsToFrames: cumulative rounding, round(cum/frame + 0.5)."""
    out, acc, prev = [], 0.0, 0
    for d in durs_ms:
        acc += d
        f = int(np.round(acc / frame_ms + 0.5))
        out.append(f - prev)
        prev = f
    return out


def _atomic_save(path, data_fn):
    tmp = f"{path}.{os.getpid()}.tmp"
    data_fn(tmp)
    os.replace(tmp, path)


def patched_model(src, dst_dir):
    """A copy of an ONNX model whose top-level RandomNormalLike (the diffusion/flow starting noise) is replaced by an
    input `noise_in`, so the caller supplies seeded noise. Returns (path, noise shape prefix, has_inner_random).
    Inner random nodes (DDPM banks add noise inside the sampling loop) get a fixed seed attribute instead."""
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(src))
    meta_p = dst + ".json"
    if os.path.exists(dst) and os.path.exists(meta_p):
        m = json.load(open(meta_p))
        return dst, m["prefix"], m["inner"]
    import onnx
    import onnxruntime as ort
    m = onnx.load(src)
    top = [n for n in m.graph.node if n.op_type == "RandomNormalLike"]
    inner = 0

    def walk(g, depth):
        nonlocal inner
        for n in g.node:
            if depth and n.op_type.startswith("Random"):
                inner += 1
                n.attribute.append(onnx.helper.make_attribute("seed", 1234.0))
            for a in n.attribute:
                if a.type == onnx.AttributeProto.GRAPH:
                    walk(a.g, depth + 1)
    walk(m.graph, 0)
    prefix = None
    if len(top) == 1:
        node = top[0]
        shape_src = [x for x in m.graph.node if node.input[0] in x.output][0].input[0]
        # probe the noise shape: expose the shape tensor and run a tiny input
        probe = onnx.ModelProto()
        probe.CopyFrom(m)
        probe.graph.output.append(onnx.helper.make_tensor_value_info(shape_src, onnx.TensorProto.INT64, None))
        s = ort.InferenceSession(probe.SerializeToString(), providers=["CPUExecutionProvider"])
        out = s.run([shape_src], _probe_feed(s))[0]
        prefix = [int(x) for x in out[:-1]]
        m.graph.node.remove(node)
        m.graph.input.append(onnx.helper.make_tensor_value_info("noise_in", onnx.TensorProto.FLOAT,
                                                                 [None] * (len(prefix) + 1)))
        m.graph.node.insert(0, onnx.helper.make_node("Identity", ["noise_in"], [node.output[0]]))
    _atomic_save(dst, lambda t: onnx.save(m, t))
    json.dump({"prefix": prefix, "inner": inner > 0}, open(meta_p, "w"))
    return dst, prefix, inner > 0


def _probe_feed(s, T=37, n=5):
    feed = {}
    for i in s.get_inputs():
        sh = [(T if "frame" in d else n) if isinstance(d, str) else d for d in i.shape]
        dt = {"tensor(int64)": np.int64, "tensor(float)": np.float32, "tensor(bool)": bool}[i.type]
        feed[i.name] = np.ones(sh, dtype=dt)
    for k in ("durations", "ph_dur", "note_dur"):
        if k in feed:
            feed[k] = np.array([[7, 7, 7, 8, 8]], dtype=np.int64)
    if "encoder_out" in feed:
        feed["encoder_out"] = np.zeros(feed["encoder_out"].shape, np.float32)
    if "f0" in feed:
        feed["f0"] = feed["f0"] * 220
    for k, v in (("depth", None), ("steps", 4), ("speedup", 100)):
        if k in feed:
            feed[k] = (np.array(0.5, np.float32) if feed[k].dtype == np.float32 else np.array(400, np.int64)) \
                if k == "depth" else np.array(v, np.int64)
    return feed


# ------------------------------------------------------------------------------------------------ a voicebank
class Bank:
    _cache = {}

    @classmethod
    def get(cls, name, banks):
        if name not in cls._cache:
            cls._cache[name] = cls(name, banks[name])
        return cls._cache[name]

    def __init__(self, name, info, threads=2):
        import onnxruntime as ort
        self.ort = ort
        self.name = name
        self.root = os.path.join(SVS_DIR, info.get("dir", name), "bank")
        if not os.path.exists(os.path.join(self.root, "dsconfig.yaml")):
            raise FileNotFoundError(f"svs bank {name!r} not found at {self.root}: download it from {info['url']} "
                                    "and unpack it there (docs/voice/VOICES.md)")
        self.cfg = _yaml(os.path.join(self.root, "dsconfig.yaml"))
        self.frame_ms = 1000.0 * self.cfg.get("hop_size", 512) / SR
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self.so = so
        self.dur_dir = os.path.join(self.root, "dsdur")
        self.pitch_dir = os.path.join(self.root, "dspitch")
        self.dur_cfg = _yaml(os.path.join(self.dur_dir, "dsconfig.yaml"))
        self.pitch_cfg = _yaml(os.path.join(self.pitch_dir, "dsconfig.yaml"))
        self.tok_ac = self._phonemes(os.path.join(self.root, self.cfg["phonemes"]))
        self.tok_dur = self._phonemes(os.path.join(self.dur_dir, self.dur_cfg["phonemes"]))
        self.tok_pitch = self._phonemes(os.path.join(self.pitch_dir, self.pitch_cfg["phonemes"]))
        self.types = {s["symbol"]: s["type"] for s in _yaml(os.path.join(self.dur_dir, "dsdict.yaml"))["symbols"]}
        self.words = {}
        for fn in ("dsdict-en.yaml", "dsdict-en-tgm.yaml"):
            self.words.update(_entries(os.path.join(self.dur_dir, fn)))
        self.lang_words = {}  # lang -> the bank's own dictionary for that language (dsdict-<lang>.yaml), loaded on use
        voc = info.get("vocoder")
        vy = os.path.join(SVS_DIR, os.path.dirname(voc), "vocoder.yaml") if voc else os.path.join(
            self.root, "dsvocoder", "vocoder.yaml")
        vcfg = _yaml(vy)
        self.vocoder = os.path.join(os.path.dirname(vy), vcfg["model"])
        # the acoustic model's mel may be log10 (older banks) and the vocoder's natural log, or the reverse (OpenUtau
        # converts the same way)
        a_base, v_base = str(self.cfg.get("mel_base", "10")), str(vcfg.get("mel_base", "10"))
        self.mel_scale = 1.0 if a_base == v_base else (np.log(10) if a_base == "10" else 1 / np.log(10))
        pdir = os.path.join(SVS_DIR, info.get("dir", name), "patched")
        self.ac_path, self.ac_prefix, self.ac_inner = patched_model(os.path.join(self.root, self.cfg["acoustic"]),
                                                                    pdir)
        self.pitch_path, self.pitch_prefix, self.pitch_inner = patched_model(
            os.path.join(self.pitch_dir, self.pitch_cfg["pitch"]), os.path.join(pdir, "pitch"))
        self._s = {}

    def _phonemes(self, path):
        return {ln.strip(): i for i, ln in enumerate(open(path, encoding="utf-8")) if ln.strip()}

    def sess(self, path, fresh=False):
        if fresh or path not in self._s:
            self._s[path] = self.ort.InferenceSession(path, self.so, providers=["CPUExecutionProvider"])
        return self._s[path]

    def emb(self, sub_dir, spk_list, mode):
        if not spk_list:
            return np.zeros(256, dtype=np.float32)
        pick = [s for s in spk_list if os.path.basename(s).endswith(mode)] if mode else []
        s = (pick or spk_list)[0]
        return np.fromfile(os.path.join(sub_dir, s + ".emb"), dtype=np.float32)

    def mix_emb(self, sub_dir, spk_list, mix):
        """mix: {mode: weight}; embeddings interpolated (OpenUtau speaker mixing)."""
        tot = sum(mix.values())
        return sum(self.emb(sub_dir, spk_list, m) * (w / tot) for m, w in mix.items()).astype(np.float32)

    def is_vowel(self, ph):
        return ph in ("SP", "AP") or self.types.get(ph) == "vowel"

    def is_glide(self, ph):
        return self.types.get(ph) in ("semivowel", "liquid")

    # -------------------------------------------------------------------------------------------- words
    def g2p(self, word, lang="en", prev=None):
        if lang == "es":
            import lang_es
            if "es" not in self.lang_words:
                self.lang_words["es"] = _entries(os.path.join(self.dur_dir, "dsdict-es.yaml"))
            w = lang_es._clean(word)
            if w in self.lang_words["es"]:
                return list(self.lang_words["es"][w])
            return lang_es.g2p(word, prev) or None
        w = word.lower().strip(",.!?;:'\"")
        if w in self.words:
            return list(self.words[w])
        import cmudict
        global _CMU
        try:
            _CMU
        except NameError:
            _CMU = cmudict.dict()
        prons = _CMU.get(w)
        if not prons:
            return None
        return ["".join(c for c in ph if not c.isdigit()).lower() for ph in prons[0]]

    def syllables(self, word, n, lang="en", prev=None):
        """A word's phonemes cut into n syllables (one vowel each). Consonants between two vowels: one goes to the
        next syllable, the rest stay with the previous one (Spanish: lang_es.syllables). Falls back to each hyphen
        part spelled on its own."""
        parts = [x for x in word.split("-") if x]
        if lang == "es":
            import lang_es
            whole = self.g2p("".join(parts), "es", prev)
            cut = lang_es.syllables(whole, n) if whole else None
            if cut:
                return cut
            out, pv = [], prev
            for x in parts[:n]:
                ph = self.g2p(x, "es", pv) or ["a"]
                out.append(ph)
                pv = ph[-1]
            if len(parts) != n:
                _warn(f"word {word!r}: {n} notes but the Spanish syllables don't match; hyphenate it (co-ra-zon)")
            return out + [["a"]] * (n - len(out))
        whole = self.g2p("".join(parts))
        if whole:
            vi = [i for i, ph in enumerate(whole) if self.is_vowel(ph)]
            if len(vi) == n:
                cuts = [0] + [max(vi[k] - 1, vi[k - 1] + 1) for k in range(1, n)] + [len(whole)]
                return [whole[cuts[k]:cuts[k + 1]] for k in range(n)]
        out = []
        for x in parts[:n]:
            ph = self.g2p(x)
            if not ph:
                _warn(f"word {word!r} not in the dictionary: sung as 'ah'")
                ph = ["ah"]
            out.append(ph)
        return out + [["ah"]] * (n - len(out))

    def note_groups(self, phs):
        """OpenUtau ProcessWord: (before-vowel part, from-vowel part) of one syllable."""
        isv = [self.is_vowel(x) for x in phs]
        start = 0
        for i in range(len(phs)):
            if isv[i]:
                start = i - 1 if (i >= 2 and self.is_glide(phs[i - 1]) and not isv[i - 2]) else i
                break
        return phs[:start], phs[start:]

    # -------------------------------------------------------------------------------------------- one phrase
    def render(self, sylls, notes, mode, seed, steps=20, pitch_steps=10, gender=0.0, velocity=1.0, breath=False,
               tail_sp_ms=300.0, detune_cents=0.0, mix=None, vibrato=1.0):
        """sylls: [phonemes per syllable]; notes: [(start_ms, dur_ms, midi, syllable index)] contiguous, in order
        (melisma notes repeat the syllable index). Returns (wave, t0_ms, phones).
        vibrato: scales the pitch model's vibrato and other fast pitch movement inside held notes (transitions
        between notes are kept). 1.0 = as the model sings it (bit-identical)."""
        fm = self.frame_ms
        rng = np.random.default_rng(seed)
        first_note = {}
        for j, n in enumerate(notes):
            first_note.setdefault(n[3], j)
        groups = [[("SP", -1, "pad")] + ([("AP", -1, "pad")] if breath else [])]
        for k, phs in enumerate(sylls):
            pre, post = self.note_groups(phs)
            groups[-1] += [(x, k, "on") for x in pre]
            groups.append([(x, k, "nu") for x in post])
        spos = [notes[first_note[k]][0] for k in range(len(sylls))]
        end = notes[-1][0] + notes[-1][1]
        pos = [spos[0] - PAD_MS] + spos + [end]
        if tail_sp_ms > 0:
            groups.append([("SP", len(sylls) - 1, "pad")])
            pos.append(end + tail_sp_ms)
        flat = [g for grp in groups for g in grp]
        midi_s = [notes[first_note[k]][2] for k in range(len(sylls))]
        tokens = np.array([[self.tok_dur[x] for x, _, _ in flat]], dtype=np.int64)
        word_div = np.array([[len(g) for g in groups]], dtype=np.int64)
        word_dur = np.array([frames_from_ms(np.diff(pos), fm)], dtype=np.int64)
        ling = self.sess(os.path.join(self.dur_dir, self.dur_cfg["linguistic"]))
        enc, mask = ling.run(None, {"tokens": tokens, "word_div": word_div, "word_dur": word_dur})
        dur = self.sess(os.path.join(self.dur_dir, self.dur_cfg["dur"]))
        midi_ph = [midi_s[0]] * len(groups[0]) + [midi_s[min(k, len(sylls) - 1)] for k in range(len(groups) - 1)
                                                  for _ in groups[k + 1]]
        e = (self.mix_emb(self.dur_dir, self.dur_cfg.get("speakers"), mix) if mix
             else self.emb(self.dur_dir, self.dur_cfg.get("speakers"), mode))
        feed = {"encoder_out": enc, "x_masks": mask, "ph_midi": np.array([midi_ph], dtype=np.int64),
                "spk_embed": np.tile(e[None, None, :], (1, len(flat), 1)), "word_div": word_div, "word_dur": word_dur}
        names = [i.name for i in dur.get_inputs()]
        dpred = dur.run(None, {k: v for k, v in feed.items() if k in names})[0][0].astype(np.float64)
        # OpenUtau alignment: the first group keeps its predicted lengths and ends on the first note
        n0 = len(groups[0])
        g0 = dpred[1:n0]
        starts = list(pos[1] - g0.sum() * fm + np.concatenate([[0], np.cumsum(g0 * fm)])[:-1])
        i = n0
        for k in range(1, len(groups)):
            g = dpred[i:i + len(groups[k])]
            r = (pos[k + 1] - pos[k]) / max(g.sum(), 1e-6)
            starts += list(pos[k] + np.concatenate([[0], np.cumsum(g * r)])[:-1])
            i += len(groups[k])
        ends = starts[1:] + [pos[-1]]
        phones = [(x, s, en, k, part) for (x, k, part), s, en in zip(flat[1:], starts, ends)
                  if not (part == "pad" and x == "SP")]
        # pitch (phoneme mode)
        t0 = phones[0][1] - HEAD_FR * fm
        seg = [("SP", HEAD_FR * fm)] + [(x, en - s) for x, s, en, _, _ in phones] + [("SP", TAIL_FR * fm)]
        ph_dur = frames_from_ms([d for _, d in seg], fm)
        total = sum(ph_dur)
        pd = np.array([ph_dur], dtype=np.int64)
        pling = self.sess(os.path.join(self.pitch_dir, self.pitch_cfg["linguistic"]))
        penc, _ = pling.run(None, {"tokens": np.array([[self.tok_pitch[x] for x, _ in seg]], dtype=np.int64),
                                   "ph_dur": pd})
        nd = [max(0.0, notes[0][0] - t0)] + [n[1] for n in notes] + [TAIL_FR * fm]
        nm = [notes[0][2]] + [n[2] for n in notes] + [notes[-1][2]]
        nr = [True] + [False] * len(notes) + [True]
        note_dur = frames_from_ms(nd, fm)
        note_dur[-1] += total - sum(note_dur)
        pe = (self.mix_emb(self.pitch_dir, self.pitch_cfg.get("speakers"), mix) if mix
              else self.emb(self.pitch_dir, self.pitch_cfg.get("speakers"), mode))
        if self.pitch_inner:
            self.ort.set_seed(int(seed) % (2 ** 31))
        pitch = self.sess(self.pitch_path, fresh=self.pitch_inner)
        pf = {"encoder_out": penc, "ph_dur": pd, "note_midi": np.array([nm], dtype=np.float32),
              "note_rest": np.array([nr], dtype=bool), "note_dur": np.array([note_dur], dtype=np.int64),
              "pitch": np.full((1, total), 60.0, dtype=np.float32), "expr": np.ones((1, total), dtype=np.float32),
              "retake": np.ones((1, total), dtype=bool),
              "spk_embed": np.tile(pe[None, None, :], (1, total, 1)).astype(np.float32),
              "steps": np.array(pitch_steps, dtype=np.int64), "speedup": np.array(self._speedup(pitch_steps), np.int64)}
        if self.pitch_prefix is not None:
            pf["noise_in"] = rng.standard_normal(self.pitch_prefix + [total]).astype(np.float32)
        names = [x.name for x in pitch.get_inputs()]
        curve = pitch.run(None, {k: v for k, v in pf.items() if k in names})[0][0]
        if vibrato != 1.0:
            curve = scale_vibrato(curve, [((n[0] - t0) / fm, (n[0] + n[1] - t0) / fm) for n in notes], fm, vibrato)
        f0 = (440.0 * 2 ** ((curve + detune_cents / 100.0 - 69) / 12)).astype(np.float32)
        # acoustic + vocoder
        if self.ac_inner:
            self.ort.set_seed(int(seed + 1) % (2 ** 31))
        ac = self.sess(self.ac_path, fresh=self.ac_inner)
        ae = (self.mix_emb(self.root, self.cfg.get("speakers"), mix) if mix
              else self.emb(self.root, self.cfg.get("speakers"), mode))
        depth, speedup = self._depth(steps)
        af = {"tokens": np.array([[self.tok_ac[x] for x, _ in seg]], dtype=np.int64), "durations": pd,
              "f0": f0[None, :], "gender": np.full((1, total), gender, dtype=np.float32),
              "velocity": np.full((1, total), velocity, dtype=np.float32),
              "spk_embed": np.tile(ae[None, None, :], (1, total, 1)).astype(np.float32),
              "depth": depth, "steps": np.array(steps, dtype=np.int64), "speedup": speedup,
              "key_shift": np.zeros((1, total), np.float32), "speed": np.ones((1, total), np.float32)}
        if self.ac_prefix is not None:
            af["noise_in"] = rng.standard_normal(self.ac_prefix + [total]).astype(np.float32)
        names = [x.name for x in ac.get_inputs()]
        mel = ac.run(None, {k: v for k, v in af.items() if k in names and v is not None})[0]
        wav = self.sess(self.vocoder).run(None, {"mel": (mel * self.mel_scale).astype(np.float32),
                                                 "f0": f0[None, :]})[0][0]
        return wav.astype(np.float32), t0, phones

    def _speedup(self, steps):
        sp = max(1, int(round(1000 / max(0.5, steps))))
        while 1000 % sp and sp > 1:
            sp -= 1
        return sp

    def _depth(self, steps):
        var = self.cfg.get("use_variable_depth", self.cfg.get("use_shallow_diffusion", False))
        if self.cfg.get("use_continuous_acceleration"):
            return np.array(min(1.0, float(self.cfg.get("max_depth", 1.0))) if var else 1.0, np.float32), None
        if var:
            dd = int(round(min(1.0, float(self.cfg.get("max_depth", 1000)) / 1000.0) * 1000))
            sp = max(1, dd // steps)
            return np.array(dd // sp * sp, np.int64), np.array(sp, np.int64)
        sp = max(1, 1000 // steps)
        while 1000 % sp and sp > 1:
            sp -= 1
        return np.array(1000, np.int64), np.array(sp, np.int64)


def scale_vibrato(curve, spans, frame_ms, amount, sigma_ms=70.0, edge_ms=100.0, ramp_ms=50.0):
    """Scale the fast part of a pitch curve (MIDI per frame) inside held notes. The slow part is a Gaussian low-pass of
    the curve (sigma_ms 70: a 5-6 Hz vibrato passes at 3-10%, a 2 Hz drift or scoop at about 75%); the fast part
    (vibrato, jitter) is the rest. Only frames at least edge_ms inside a note are scaled (ramped in over ramp_ms), so
    transitions between notes stay as sung. spans: (start, end) of each note in frames."""
    c = np.asarray(curve, dtype=np.float64)
    sg = sigma_ms / frame_ms
    h = int(np.ceil(3 * sg))
    k = np.exp(-0.5 * (np.arange(-h, h + 1) / sg) ** 2)
    smooth = np.convolve(np.pad(c, (h, h), mode="edge"), k / k.sum(), mode="valid")
    mask = np.zeros(len(c))
    e, r = edge_ms / frame_ms, max(1.0, ramp_ms / frame_ms)
    idx = np.arange(len(c))
    for a, b in spans:
        inside = np.minimum(idx - (a + e), (b - e) - idx)
        mask = np.maximum(mask, np.clip(inside / r, 0.0, 1.0))
    return (c + (amount - 1.0) * mask * (c - smooth)).astype(np.float32)


# ------------------------------------------------------------------------------------------------ the line
def _groups(p, notes):
    """Notes -> syllable groups: [(token, [note indices])] (a `_` token extends the previous group: a melisma)."""
    toks = list(p.get("_lyrics") or [])
    groups = []
    for i, nt in enumerate(notes):
        tok = nt.get("syl")
        if tok is None:
            tok = toks[i] if i < len(toks) else "_"
        if tok == "_" and groups:
            groups[-1][1].append(i)
        else:
            if tok == "_":
                tok = ("oo", 0, 1)
            groups.append((tok, [i]))
    return groups


def _phrases(notes, groups, legato=0.12, min_gap_ms=25.0):
    """Split syllable groups into phrases at rests. A gap counts as legato (the notes are joined, as notes touch in
    OpenUtau) when it is under `legato` of the note's slot or under min_gap_ms: the engine plays notes at 95% length."""
    out = [[groups[0]]]
    for g in groups[1:]:
        prev = notes[out[-1][-1][1][-1]]
        a = notes[g[1][0]]
        gap = (a["t0"] - (prev["t0"] + prev["n"])) / SR * 1000
        slot = (a["t0"] - prev["t0"]) / SR * 1000
        if gap > max(min_gap_ms, legato * slot):
            out.append([g])
        else:
            out[-1].append(g)
    return out


def _key(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:20]


def take(p, notes, total_n, seed, jitter_ms=0.0, detune_cents=0.0):
    """One take of the line: every phrase rendered (or loaded from the phrase cache) and placed. Mono float32."""
    v, banks = voice_spec(p)
    bank_name = v["bank"]
    info = banks[bank_name]
    mode = v.get("mode")
    mix = v.get("mix")
    gender = float(p.get("gender", v.get("gender", 0.0)))
    velocity = float(p.get("velocity", v.get("velocity", 1.0)))
    steps = int(p.get("svs_steps", 20))
    vib = float(p.get("svs_vibrato", 1.0))
    groups = _groups(p, notes)
    lang = str(p.get("lang") or v.get("lang") or "en")
    if lang != "en" and lang not in info.get("languages", ["en"]):
        _warn(f"voice {v['id']!r} (bank {bank_name}) has no {lang!r} data; languages: {info.get('languages', ['en'])}")
    y = np.zeros(total_n + SR, dtype=np.float32)
    rng = np.random.default_rng(seed)
    prev_end = -1e9
    fade_in = float(p.get("svs_fade_in_ms", 5.0))
    fade_out = float(p.get("svs_fade_out_ms", 5.0))
    breath_after = float(p.get("breath_after_s", 0.4))
    breath = float(p.get("inhale", 0.0)) > 0
    bank = None
    for ph in _phrases(notes, groups):
        ns = []
        for k, (tok, idx) in enumerate(ph):
            for j in idx:
                nt = notes[j]
                ns.append([nt["t0"] / SR * 1000, nt["n"] / SR * 1000, 69 + 12 * np.log2(nt["f"] / 440.0), k])
        for a, b in zip(ns, ns[1:]):  # legato: each note lasts to the next onset
            a[1] = b[0] - a[0]
        ns = [(a, d, int(round(m)), k) for a, d, m, k in ns]
        sh = float(rng.normal(0, jitter_ms)) if jitter_ms else 0.0
        ns = [(a + sh, d, m, k) for a, d, m, k in ns]
        words = [tok for tok, _ in ph]
        br = breath and (ns[0][0] - prev_end) / 1000 >= breath_after
        pseed = int(_key("seed", seed, words, ns)[:8], 16)
        key = _key(VERSION, bank_name, info.get("vocoder"), mode, mix, gender, velocity, steps, br, detune_cents,
                   words, [(round(a, 1), round(d, 1), m, k) for a, d, m, k in ns], pseed,
                   *(() if lang == "en" else ("lang", lang, LANG_VERSION)),
                   *(() if vib == 1.0 else ("vib", vib)))
        path = os.path.join(PHRASES, key[:2], key + ".npz")
        if os.path.exists(path):
            z = np.load(path)
            wav, t0 = z["wav"], float(z["t0"])
        else:
            if bank is None:
                bank = Bank.get(bank_name, banks)
            phs = []
            done = {}
            prev = None  # last phoneme of the previous word in this phrase (Spanish connected-speech allophones)
            for wi, (word, si, n) in enumerate(words):
                if lang == "en":
                    if (word, n) not in done:
                        done[(word, n)] = bank.syllables(word, n)
                    phs.append(done[(word, n)][si])
                    continue
                if wi > 0 and si == 0:
                    prev = phs[-1][-1] if phs and phs[-1] else prev
                kk = (word, n, prev)
                if kk not in done:
                    done[kk] = bank.syllables(word, n, lang, prev)
                phs.append(done[kk][si])
            wav, t0, _ = bank.render(phs, ns, mode, pseed, steps=steps, gender=gender, velocity=velocity,
                                     breath=br, detune_cents=detune_cents, mix=mix, vibrato=vib)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            _atomic_save(path, lambda t: np.savez(open(t, "wb"), wav=wav, t0=t0))
        wav = wav.copy()
        fi = min(len(wav) // 4, int(fade_in / 1000 * SR))
        fo = min(len(wav) // 4, int(fade_out / 1000 * SR))
        if fi > 0:
            wav[:fi] *= np.linspace(0, 1, fi) ** 2
        if fo > 0:
            wav[-fo:] *= np.linspace(1, 0, fo) ** 2
        a = int(round(t0 / 1000 * SR))
        if a < 0:
            wav, a = wav[-a:], 0
        b = min(len(y), a + len(wav))
        if b > a:
            y[a:b] += wav[:b - a]
        prev_end = ns[-1][0] + ns[-1][1]
    return y[:total_n]


def sing(p, notes, total_n):
    """singer.sing for `source: "svs"`: mono, or stereo (2, N) with a double (a second take: its own seeded pitch
    and timbre noise, its phrases moved by a few ms, a few cents off, panned opposite), levelled by singer._norm."""
    import singer as _singer
    p = dict(p)
    if "lyrics" in p and not p.get("_lyrics"):
        p["_lyrics"] = _singer.parse_lyrics(p["lyrics"])
    if not notes:
        return np.zeros(total_n, dtype=np.float32)
    v, _ = voice_spec(p)
    lo, hi = v.get("range_midi", [0, 127])
    out = [nt for nt in notes if not lo <= 69 + 12 * np.log2(nt["f"] / 440.0) <= hi]
    if out:
        _warn(f"{len(out)} of {len(notes)} notes are outside {v['id']}'s range "
              f"({v.get('range', '')}); transpose the line")
    seed = int(p.get("seed", 1))
    main = take(p, notes, total_n, _singer._seed("svs", seed, 0))
    norm = _singer._norm(main)
    dbl = float(p.get("double", 0.0))
    if dbl <= 0:
        return (main * norm).astype(np.float32)
    take2 = take(p, notes, total_n, _singer._seed("svs", seed, 1), jitter_ms=float(p.get("double_ms", 12)),
                 detune_cents=float(p.get("double_cents", 7)))
    sp_ = float(p.get("double_pan", 0.5))
    a = (sp_ + 1) * np.pi / 4
    b = (-sp_ + 1) * np.pi / 4
    L = main * np.cos(b) + dbl * take2 * np.cos(a)
    R = main * np.sin(b) + dbl * take2 * np.sin(a)
    return (np.stack([L, R]) / (1 + dbl) * norm).astype(np.float32)
