"""dsinger: a minimal headless DiffSinger (OpenVPI ONNX, OpenUtau voicebank layout) driver, for the SVS trial.

Follows OpenUtau's DiffSinger code path (OpenUtau.Core/DiffSinger: DiffSingerBasePhonemizer.ProcessPart,
DiffSingerPitch.Process, DiffSingerRenderer.InvokeDiffsinger), so a line sounds the way it would in OpenUtau with
default settings and no hand edits:

1. words -> phonemes (the bank's dsdict-en.yaml first, then CMUdict ARPAbet, lower case, no stress, as OpenUtau's
   DiffSingerEnglishPhonemizer);
2. phonemes are grouped per note: a note's group starts at its vowel (or at a w/y glide right after a consonant), so
   onset consonants belong to the previous group and are sung BEFORE the note: the vowel lands on the note;
3. the bank's duration model predicts every phoneme's length from context (learned from the singer's recordings);
   OpenUtau then stretches each group to fill its note-to-note span (the first group's consonants keep their length);
4. the pitch model draws the f0 curve from the notes and phonemes (auto-pitch: scoops, transitions, vibrato);
5. the acoustic model makes the mel spectrogram, the vocoder the waveform.

A phrase is a run of notes without a gap; each phrase is rendered on its own (500 ms SP lead, 8 frames head/tail
padding) and placed on the timeline. Model files are never in the repo: banks live in ~/.cache/spectre/svs/<bank>/.
"""
import os
import time

import numpy as np
import onnxruntime as ort
import yaml

SR = 44100
PAD_MS = 500.0  # OpenUtau: padding time for consonants at the beginning of a phrase
HEAD_FR = TAIL_FR = 8


def _dict_entries(path):
    out = {}
    if not os.path.exists(path):
        return out
    d = yaml.safe_load(open(path, encoding="utf-8"))
    for e in d.get("entries") or []:
        out[str(e["grapheme"]).lower()] = list(e["phonemes"])
    return out


def _symbols(path):
    d = yaml.safe_load(open(path, encoding="utf-8"))
    return {s["symbol"]: s["type"] for s in d.get("symbols") or []}


def frames_from_ms(durs_ms, frame_ms):
    """OpenUtau DiffSingerUtils.DurationsMsToFrames: cumulative rounding, round(cum/frame + 0.5)."""
    out, acc, prev = [], 0.0, 0
    for d in durs_ms:
        acc += d
        f = int(np.round(acc / frame_ms + 0.5))
        out.append(f - prev)
        prev = f
    return out


def fit_sum(durs, total):
    durs = list(durs)
    durs[-1] += total - sum(durs)
    return durs


class Bank:
    def __init__(self, root, speaker=None, threads=2, vocoder=None, seed=0):
        # the pitch and acoustic models sample noise (diffusion / rectified flow); onnxruntime seeds its random
        # kernels when a session is created, so seeding here makes a fresh Bank's renders repeat bit for bit
        # (the same calls in the same order give the same audio)
        ort.set_seed(int(seed))
        self.root = root
        self.cfg = yaml.safe_load(open(os.path.join(root, "dsconfig.yaml"), encoding="utf-8"))
        self.hop = self.cfg.get("hop_size", 512)
        self.frame_ms = 1000.0 * self.hop / SR
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self._so = so
        self._sess = {}
        self.tokens = self._phonemes(os.path.join(root, self.cfg["phonemes"]))
        self.speaker = speaker or (os.path.basename(self.cfg["speakers"][0]) if self.cfg.get("speakers") else None)
        # duration and pitch sub-models
        self.dur_dir = os.path.join(root, "dsdur")
        self.pitch_dir = os.path.join(root, "dspitch")
        self.var_dir = os.path.join(root, "dsvariance")
        self.dur_cfg = yaml.safe_load(open(os.path.join(self.dur_dir, "dsconfig.yaml"), encoding="utf-8"))
        self.pitch_cfg = yaml.safe_load(open(os.path.join(self.pitch_dir, "dsconfig.yaml"), encoding="utf-8"))
        self.var_cfg = (yaml.safe_load(open(os.path.join(self.var_dir, "dsconfig.yaml"), encoding="utf-8"))
                        if os.path.exists(os.path.join(self.var_dir, "dsconfig.yaml")) else None)
        self.tok_dur = self._phonemes(os.path.join(self.dur_dir, self.dur_cfg["phonemes"]))
        self.tok_pitch = self._phonemes(os.path.join(self.pitch_dir, self.pitch_cfg["phonemes"]))
        self.types = _symbols(os.path.join(self.dur_dir, "dsdict.yaml"))
        self.words = {}
        for name in ("dsdict-en.yaml", "dsdict-en-tgm.yaml"):  # the bank's own English entries win over CMUdict
            self.words.update(_dict_entries(os.path.join(self.dur_dir, name)))
        self.lang_ids = None
        lid = self.cfg.get("languages")
        if self.cfg.get("use_lang_id") and lid:
            self.lang_ids = yaml.safe_load(open(os.path.join(root, lid), encoding="utf-8"))
        voc = yaml.safe_load(open(os.path.join(root, "dsvocoder", "vocoder.yaml"), encoding="utf-8"))
        self.vocoder_path = vocoder or os.path.join(root, "dsvocoder", voc["model"])
        self.timings = {}

    def _phonemes(self, path):
        if path.endswith(".json"):
            import json
            return json.load(open(path))
        return {ln.strip(): i for i, ln in enumerate(open(path, encoding="utf-8")) if ln.strip()}

    def sess(self, path):
        if path not in self._sess:
            self._sess[path] = ort.InferenceSession(path, self._so, providers=["CPUExecutionProvider"])
        return self._sess[path]

    def emb(self, sub_dir, spk_list):
        """Speaker embedding (256 float32) for the bank's speaker name, from a model's speakers list."""
        if not spk_list:
            return np.zeros(256, dtype=np.float32)  # single-speaker model: no spk_embed input
        for s in spk_list or []:
            if os.path.basename(s) == self.speaker:
                return np.fromfile(os.path.join(sub_dir, s + ".emb"), dtype=np.float32)
        return np.fromfile(os.path.join(sub_dir, spk_list[0] + ".emb"), dtype=np.float32)

    def tok(self, ph, table=None, lang="en"):
        table = self.tokens if table is None else table
        for k in (f"{lang}/{ph}", ph):
            if k in table:
                return table[k]
        raise KeyError(f"phoneme {ph!r} not in the bank")

    def lang(self, ph):
        if self.lang_ids is None:
            return 0
        return self.lang_ids.get("en", 0) if ph not in ("SP", "AP") else 0

    def is_vowel(self, ph):
        return self.types.get(ph, "vowel" if ph in ("SP", "AP") else "") == "vowel"

    def is_glide(self, ph):
        return self.types.get(ph) in ("semivowel", "liquid")

    def _continuous(self):
        return bool(self.cfg.get("use_continuous_acceleration"))

    def _pitch_speedup(self, steps):
        """OpenUtau ComputePitchSpeedup (old DDPM pitch models): 1000 timesteps / steps, a factor of 1000."""
        sp = max(1, int(round(1000 / max(0.5, steps))))
        while 1000 % sp and sp > 1:
            sp -= 1
        return sp

    def _acoustic_depth(self, depth, steps):
        """OpenUtau DiffSingerRenderer: depth = min(1, max_depth); continuous models take it as a float, old ones as
        int timesteps (max_depth out of 1000) with a speedup."""
        var = self.cfg.get("use_variable_depth", self.cfg.get("use_shallow_diffusion", False))
        d = 1.0 if depth is None else depth
        if self._continuous():
            md = float(self.cfg.get("max_depth", 1.0))
            return np.array(min(d, md) if var else 1.0, dtype=np.float32), None
        if var:
            md = float(self.cfg.get("max_depth", 1000)) / 1000.0
            dd = int(round(min(d, md) * 1000))
            sp = max(1, dd // steps)
            return np.array(dd // sp * sp, dtype=np.int64), np.array(sp, dtype=np.int64)
        sp = max(1, 1000 // steps)
        while 1000 % sp and sp > 1:
            sp -= 1
        return np.array(1000, dtype=np.int64), np.array(sp, dtype=np.int64)

    # ---------------------------------------------------------------- phonemizer
    def g2p(self, word):
        import cmudict
        w = word.lower().strip(",.!?;:'\"")
        if w in self.words:
            return self.words[w]
        global _CMU
        try:
            _CMU
        except NameError:
            _CMU = cmudict.dict()
        prons = _CMU.get(w)
        if not prons:
            raise KeyError(f"word {word!r} not in CMUdict")
        return ["".join(c for c in p if not c.isdigit()).lower() for p in prons[0]]

    def note_groups(self, phs):
        """OpenUtau ProcessWord for a one-syllable word: (before-vowel part, from-vowel part)."""
        isv = [self.is_vowel(p) for p in phs]
        start = None
        for i, p in enumerate(phs):
            if isv[i]:
                start = i - 1 if (i >= 2 and self.is_glide(phs[i - 1]) and not isv[i - 2]) else i
                break
        if start is None:
            start = 0
        return phs[:start], phs[start:]

    # ---------------------------------------------------------------- the phrase
    def render_phrase(self, words, notes, steps=20, pitch_steps=10, depth=None, gender=0.0, velocity=1.0,
                      detune_cents=0.0, tail_sp_ms=0.0):
        """words: one per note; notes: [(start_ms, dur_ms, midi)] contiguous. Returns (wave, t0_ms, phones, f0)
        where phones = [(phoneme, start_ms, end_ms, note_index, part)] with part 'on' (before the vowel) or 'nu'."""
        fm = self.frame_ms
        # 1. phonemes per note (first group: SP + the first word's onset)
        groups = [[("SP", -1, "pad")]]
        for k, w in enumerate(words):
            pre, post = self.note_groups(self.g2p(w))
            groups[-1] += [(p, k, "on") for p in pre]
            groups.append([(p, k, "nu") for p in post])
        pos = [notes[0][0] - PAD_MS] + [n[0] for n in notes] + [notes[-1][0] + notes[-1][1]]
        if tail_sp_ms > 0:  # a closing rest token, as DiffSinger's training phrases end in SP
            groups.append([("SP", len(notes) - 1, "pad")])
            pos.append(pos[-1] + tail_sp_ms)
        flat = [g for grp in groups for g in grp]
        tokens = np.array([[self.tok(p, self.tok_dur) for p, _, _ in flat]], dtype=np.int64)
        word_div = np.array([[len(g) for g in groups]], dtype=np.int64)
        word_dur = np.array([frames_from_ms(np.diff(pos), fm)], dtype=np.int64)
        t = time.time()
        ling = self.sess(os.path.join(self.dur_dir, self.dur_cfg["linguistic"]))
        feed = {"tokens": tokens, "word_div": word_div, "word_dur": word_dur}
        if "languages" in [i.name for i in ling.get_inputs()]:
            feed["languages"] = np.array([[self.lang(p) for p, _, _ in flat]], dtype=np.int64)
        enc, mask = ling.run(None, feed)
        dur = self.sess(os.path.join(self.dur_dir, self.dur_cfg["dur"]))
        midi_ph = [notes[0][2]] * len(groups[0]) + [notes[min(k, len(notes) - 1)][2] for k in range(len(groups) - 1)
                                                    for _ in groups[k + 1]]
        e = self.emb(self.dur_dir, self.dur_cfg.get("speakers"))
        dfeed = {"encoder_out": enc, "x_masks": mask, "ph_midi": np.array([midi_ph], dtype=np.int64),
                 "spk_embed": np.tile(e[None, None, :], (1, len(flat), 1)).astype(np.float32)}
        din = [i.name for i in dur.get_inputs()]
        if "word_div" in din:
            dfeed.update(word_div=word_div, word_dur=word_dur)
        dfeed = {k: v for k, v in dfeed.items() if k in din}
        dpred = dur.run(None, dfeed)[0][0].astype(np.float64)
        self.timings["dur"] = self.timings.get("dur", 0) + time.time() - t
        # 2. alignment (OpenUtau): the first group's consonants keep their predicted length and end on the first
        # note; every later group is stretched to its note span
        starts = []
        n0 = len(groups[0])
        g0 = dpred[1:n0]
        s = pos[1] - g0.sum() * fm
        starts += list(s + np.concatenate([[0], np.cumsum(g0 * fm)])[:-1])
        i = n0
        for k in range(1, len(groups)):
            g = dpred[i:i + len(groups[k])]
            span = pos[k + 1] - pos[k]
            r = span / g.sum()
            starts += list(pos[k] + np.concatenate([[0], np.cumsum(g * r)])[:-1])
            i += len(groups[k])
        ends = starts[1:] + [pos[-1]]
        phones = [(p, st, en, k, part) for (p, k, part), st, en in zip(flat[1:], starts, ends) if part != "pad"]
        # 3. pitch model (phoneme mode)
        t = time.time()
        t0 = phones[0][1] - HEAD_FR * fm
        seg = [("SP", HEAD_FR * fm)] + [(p, en - st) for p, st, en, _, _ in phones] + [("SP", TAIL_FR * fm)]
        ph_dur = frames_from_ms([d for _, d in seg], fm)
        total = sum(ph_dur)
        ptoks = np.array([[self.tok(p, self.tok_pitch) for p, _ in seg]], dtype=np.int64)
        atoks = np.array([[self.tok(p) for p, _ in seg]], dtype=np.int64)
        pd = np.array([ph_dur], dtype=np.int64)
        pling = self.sess(os.path.join(self.pitch_dir, self.pitch_cfg["linguistic"]))
        pfeed = {"tokens": ptoks, "ph_dur": pd}
        if "languages" in [x.name for x in pling.get_inputs()]:
            pfeed["languages"] = np.array([[self.lang(p) for p, _ in seg]], dtype=np.int64)
        penc, _ = pling.run(None, pfeed)
        nd = [max(0.0, notes[0][0] - t0)] + [n[1] for n in notes] + [TAIL_FR * fm]
        nm = [notes[0][2]] + [n[2] for n in notes] + [notes[-1][2]]
        nr = [True] + [False] * len(notes) + [True]
        note_dur = fit_sum(frames_from_ms(nd, fm), total)
        pitch = self.sess(os.path.join(self.pitch_dir, self.pitch_cfg["pitch"]))
        pe = self.emb(self.pitch_dir, self.pitch_cfg.get("speakers"))
        pf = {"encoder_out": penc, "ph_dur": pd, "note_midi": np.array([nm], dtype=np.float32),
              "note_rest": np.array([nr], dtype=bool), "note_dur": np.array([note_dur], dtype=np.int64),
              "pitch": np.full((1, total), 60.0, dtype=np.float32), "expr": np.ones((1, total), dtype=np.float32),
              "retake": np.ones((1, total), dtype=bool),
              "spk_embed": np.tile(pe[None, None, :], (1, total, 1)).astype(np.float32),
              "steps": np.array(pitch_steps, dtype=np.int64),
              "speedup": np.array(self._pitch_speedup(pitch_steps), dtype=np.int64)}
        pin = [x.name for x in pitch.get_inputs()]
        pf = {k: v for k, v in pf.items() if k in pin}
        midi_curve = pitch.run(None, pf)[0][0]
        f0 = (440.0 * 2 ** ((midi_curve + detune_cents / 100.0 - 69) / 12)).astype(np.float32)
        self.timings["pitch"] = self.timings.get("pitch", 0) + time.time() - t
        # 4. acoustic + vocoder
        t = time.time()
        ac = self.sess(os.path.join(self.root, self.cfg["acoustic"]))
        ae = self.emb(self.root, self.cfg.get("speakers"))
        dep, sp = self._acoustic_depth(depth, steps)
        af = {"tokens": atoks, "durations": pd, "f0": f0[None, :],
              "gender": np.full((1, total), gender, dtype=np.float32),
              "velocity": np.full((1, total), velocity, dtype=np.float32),
              "spk_embed": np.tile(ae[None, None, :], (1, total, 1)).astype(np.float32),
              "depth": dep, "steps": np.array(steps, dtype=np.int64), "speedup": sp}
        ain = {x.name: x for x in ac.get_inputs()}
        if "languages" in ain:
            af["languages"] = pfeed.get("languages")
        if "key_shift" in ain:
            af["key_shift"] = np.zeros((1, total), dtype=np.float32)
        if "speed" in ain:
            af["speed"] = np.ones((1, total), dtype=np.float32)
        af = {k: v for k, v in af.items() if v is not None}
        missing = [k for k in ain if k not in af]
        if missing:
            raise RuntimeError(f"acoustic inputs not handled: {missing}")
        af = {k: v for k, v in af.items() if k in ain}
        mel = ac.run(None, af)[0]
        self.timings["acoustic"] = self.timings.get("acoustic", 0) + time.time() - t
        t = time.time()
        voc = self.sess(self.vocoder_path)
        wav = voc.run(None, {"mel": mel, "f0": f0[None, :]})[0][0]
        self.timings["vocoder"] = self.timings.get("vocoder", 0) + time.time() - t
        return wav.astype(np.float32), t0, phones, (t0, f0)


def phrases(notes, legato_ms=0.0):
    """Split [(start_ms, dur_ms, midi, word)] into runs without a rest. A gap of at most legato_ms counts as legato
    (the note is extended to the next onset, as notes touch in OpenUtau)."""
    out = [[notes[0]]]
    for n in notes[1:]:
        p = out[-1][-1]
        gap = n[0] - (p[0] + p[1])
        if gap > max(legato_ms, 0.5):
            out.append([n])
        else:
            out[-1][-1] = (p[0], n[0] - p[0], p[2], p[3])
            out[-1].append(n)
    return out


def sing(bank, notes, total_s, legato_ms=0.0, jitter_ms=0.0, seed=0, tail_sp_ms=300.0, **kw):
    """notes: [(start_ms, dur_ms, midi, word)]. Returns (mono wave, phones with absolute ms, per-note index).
    jitter_ms moves each phrase by a random few ms (for a double take)."""
    y = np.zeros(int(total_s * SR) + 2 * SR, dtype=np.float32)
    rng = np.random.default_rng(seed)
    allph = []
    k0 = 0
    for ph in phrases(notes, legato_ms):
        sh = float(rng.normal(0, jitter_ms)) if jitter_ms else 0.0
        wav, t0, phones, _ = bank.render_phrase([n[3] for n in ph], [(n[0] + sh, n[1], n[2]) for n in ph],
                                                tail_sp_ms=tail_sp_ms, **kw)
        f = min(len(wav) // 4, int(0.005 * SR))  # 5 ms fades at the phrase edges (no click where it starts)
        wav[:f] *= np.linspace(0, 1, f)
        wav[-f:] *= np.linspace(1, 0, f)
        a = int(round(t0 / 1000 * SR))
        if a < 0:
            wav, a = wav[-a:], 0
        b = min(len(y), a + len(wav))
        y[a:b] += wav[:b - a]
        allph += [(p, st, en, k + k0, part) for p, st, en, k, part in phones]
        k0 += len(ph)
    return y[:int(total_s * SR)], allph
