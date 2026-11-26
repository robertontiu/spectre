"""Bass-music voices for the modern dubstep strands (docs/DUBSTEP.md "Engine mapping", gaps 1-4; docs/MANUAL.md "Bass
music"). Additive: used only when a track names `fmgrowl` or `wavetable` (polyphonic, stereo), or a `vowel` fx;
the module RNG (instruments.RNG) is drawn at call time, so per-track seeds give each track its own stream.

  fmgrowl     2-4 operator FM (ratios, indices, operator feedback; stack or parallel), unison, then the bass chain
  wavetable   a wavetable oscillator with a morphing position (built-in tables: basic, vocal, harsh, fm, pwm), unison,
              then the bass chain
  the chain   wavefolder -> drive -> bit reduction -> formant (vowel) filter -> filter (lp/bp/hp, resonant) -> amp
  mod         per-note modulation: LFOs with rates in note values ("1/8t", "1/16d", "1/4", "2/1") or Hz, retriggered
              per note or locked to the song's grid, shapes sine / tri / saw / ramp / square / steps / random, and
              envelopes (one-shot or looping), to: index, index.N, feedback, pos, vowel, fold, drive, cutoff, reso,
              pitch, level, pan. A note can change the first LFO's rate: "0:F1:8/r=1/8t" (r2= the second's).
  formant     a three-formant vowel filter (Peterson & Barney 1952, adult male means): oo, oh, ah, eh, ee at positions
              0-4, morphing continuously; also the `vowel` fx.
"""
import math

import numpy as np
from scipy import signal

import instruments as I

SR = I.SR
TWO_PI = 2 * np.pi

try:
    from numba import njit
except Exception:  # pragma: no cover
    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


def _rng():
    return I.RNG


# ------------------------------------------------------------------ tempo-synced rates

def note_seconds(v, bpm):
    """A note value as seconds: "1/4" (a beat), "1/8", "1/16", "1/8t" (triplet: x 2/3), "1/8d" (dotted: x 1.5),
    "1/1" (a bar of 4/4), "2/1" (two bars). A number is a rate in Hz (returns its period)."""
    if isinstance(v, (int, float)):
        return 1.0 / max(float(v), 1e-6)
    s = str(v).strip().lower()
    mult = 1.0
    if s.endswith("t"):
        mult, s = 2.0 / 3.0, s[:-1]
    elif s.endswith("d") or s.endswith("."):
        mult, s = 1.5, s[:-1]
    if s.endswith("hz"):
        return 1.0 / max(float(s[:-2]), 1e-6)
    if "/" in s:
        a, b = s.split("/")
        beats = 4.0 * float(a) / float(b)
    else:
        beats = 4.0 * float(s)
    return beats * 60.0 / float(bpm) * mult


def rate_hz(v, bpm):
    return 1.0 / note_seconds(v, bpm)


def art_rates(art):
    """Per-note rate tokens from a note's articulations: r=1/8t (the first LFO), r2=1/16 (the second)..."""
    out = {}
    for a in art or []:
        if "=" in a and a[0] == "r":
            k, v = a.split("=", 1)
            i = 0 if k == "r" else int(k[1:]) - 1
            out[i] = v
    return out


# ------------------------------------------------------------------ modulation

def _wave(shape, ph, steps=None, rng=None):
    t = ph % 1.0
    if shape == "sine":
        return 0.5 - 0.5 * np.cos(TWO_PI * ph)          # 0..1, starts at 0
    if shape in ("tri", "triangle"):
        return 1 - np.abs(2 * t - 1)
    if shape == "saw":                                  # falling: the classic wobble "wub"
        return 1 - t
    if shape == "ramp":
        return t
    if shape == "square":
        return (t < 0.5).astype(np.float64)
    if shape == "steps":
        st = np.asarray(steps if steps else [0, 1], dtype=np.float64)
        return st[(np.floor(ph * len(st)).astype(np.int64)) % len(st)]
    if shape in ("random", "smooth"):
        k = np.floor(ph).astype(np.int64)
        k0 = int(k.min())
        vals = rng.uniform(0, 1, int(k.max()) - k0 + 2)
        a = vals[k - k0]
        if shape == "random":
            return a
        b = vals[k - k0 + 1]
        return a + (b - a) * (0.5 - 0.5 * np.cos(np.pi * t))
    raise ValueError(f"unknown mod shape '{shape}' (sine, tri, saw, ramp, square, steps, random, smooth)")


def mod_curves(p, n, hold, vel):
    """The per-sample modulation of one note: {dest: curve}. dest units: index (FM index), feedback, pos (0-1),
    vowel (0-4), fold, drive (0-1), cutoff (octaves), reso, pitch (semitones), level (dB), pan (-1..1)."""
    bpm = float(p.get("_bpm", 120.0))
    t0 = float(p.get("_t0", 0.0))
    rng = _rng()
    t = np.arange(n) / SR
    over = art_rates(p.get("_art"))
    out = {}
    li = 0
    for m in p.get("mod") or []:
        kind = m.get("type", "lfo")
        depth = float(m.get("depth", 1.0))
        dest = m.get("dest", "cutoff")
        if kind == "lfo":
            rate = over.get(li, m.get("rate", "1/8"))
            li += 1
            hz = rate_hz(rate, bpm)
            ph0 = float(m.get("phase", 0.0))
            if not m.get("retrig", True):          # locked to the song's grid: the phase it would have at t0
                ph0 += hz * t0
            w = _wave(m.get("shape", "sine"), ph0 + hz * t, m.get("steps"), rng)
            if m.get("bipolar"):
                w = 2 * w - 1
            d = float(m.get("delay", 0.0))
            if d > 0:
                w = w * np.clip((t - d) / max(float(m.get("fade", 0.05)), 1e-3), 0, 1)
            c = depth * w
        elif kind == "env":
            a = max(float(m.get("attack", 0.0)), 1e-4)
            dec = max(float(m.get("decay", 0.3)), 1e-4)
            sus = float(m.get("sustain", 0.0))
            if m.get("loop"):                       # a looping envelope (the "honk" retriggered at a rate)
                per = note_seconds(m["loop"], bpm)
                tt = t % per
            else:
                tt = t
            e = np.where(tt < a, tt / a, sus + (1 - sus) * np.exp(-(tt - a) / (dec / 4.6)))
            if not m.get("loop"):
                rel = max(float(m.get("release", 0.05)), 1e-4)
                th = hold / SR
                e = np.where(t > th, e * np.exp(-(t - th) / (rel / 4.6)), e)
            c = depth * e
        else:
            raise ValueError(f"unknown mod type '{kind}' (lfo or env)")
        if m.get("vel"):
            c = c * vel
        out[dest] = out.get(dest, 0.0) + c
    return out


# ------------------------------------------------------------------ filters (numba, per-sample cutoff)

@njit(cache=True)
def svf(x, fc, q, mode):
    """Zero-delay state-variable filter (Zavalishin), cutoff and Q per sample. mode 0 lp, 1 bp (0 dB peak), 2 hp."""
    n = len(x)
    y = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    for i in range(n):
        f = fc[i]
        if f > 0.45 * 44100.0:
            f = 0.45 * 44100.0
        if f < 10.0:
            f = 10.0
        g = math.tan(math.pi * f / 44100.0)
        k = 1.0 / max(q[i], 0.05)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = k * v1
        else:
            y[i] = x[i] - k * v1 - v2
    return y


# Peterson & Barney (1952), adult male means: F1, F2, F3 (Hz) of /u/ (oo), /ɔ/ (oh), /ɑ/ (ah), /ɛ/ (eh), /i/ (ee);
# the order makes F2 rise steadily from 0 to 4, so a sweep of the position reads as "oo-ah-ee" (the "yoi" / "wow").
VOWELS = ["oo", "oh", "ah", "eh", "ee"]
VOWEL_F = np.array([[300, 870, 2240], [570, 840, 2410], [730, 1090, 2440], [530, 1840, 2480], [270, 2290, 3010]],
                   dtype=np.float64)
VOWEL_G = np.array([1.0, 0.5, 0.25])
VOWEL_Q = np.array([5.0, 9.0, 12.0])


def vowel_pos(v):
    if isinstance(v, str):
        if v not in VOWELS:
            raise ValueError(f"vowel must be one of {VOWELS} or a number 0-4, not {v!r}")
        return float(VOWELS.index(v))
    return float(v)


def formant(x, pos, q_scale=1.0, shift=1.0):
    """x mono, pos (n,) vowel position 0-4 (fractional = a morph). Three band-passes in parallel, their centres
    following the position, gains 0 / -6 / -12 dB, Q 5 / 9 / 12 x q_scale; `shift` scales the formants."""
    p = np.clip(pos, 0, 4)
    i = np.minimum(np.floor(p).astype(np.int64), 3)
    fr = (p - i)[:, None]
    F = VOWEL_F[i] * (1 - fr) + VOWEL_F[i + 1] * fr
    F = F * shift
    y = np.zeros(len(x))
    for j in range(3):
        y += VOWEL_G[j] * svf(x, np.ascontiguousarray(F[:, j]), np.full(len(x), VOWEL_Q[j] * q_scale), 1)
    return y * 1.8


# ------------------------------------------------------------------ FM core

@njit(cache=True)
def _fm_kernel(f, ratios, idx, fb, algo, ph0):
    """f (n,) Hz; ratios (K,); idx (K, n) modulation indices (op 0 = carrier, its index unused); fb (n,) feedback of the
    top operator; algo 0 stack (K-1 -> ... -> 1 -> 0), 1 parallel (1..K-1 -> 0). Returns the carrier (n,)."""
    n = len(f)
    K = len(ratios)
    ph = ph0.copy()
    prev = np.zeros(K)
    y = np.empty(n)
    for t in range(n):
        mod = 0.0
        if algo == 0:
            m = 0.0
            for k in range(K - 1, 0, -1):
                if k == K - 1:
                    v = math.sin(TWO_PI * ph[k] + fb[t] * prev[k])
                else:
                    v = math.sin(TWO_PI * ph[k] + m)
                prev[k] = v
                m = idx[k, t] * v
            mod = m
        else:
            for k in range(1, K):
                if k == K - 1:
                    v = math.sin(TWO_PI * ph[k] + fb[t] * prev[k])
                else:
                    v = math.sin(TWO_PI * ph[k])
                prev[k] = v
                mod += idx[k, t] * v
        y[t] = math.sin(TWO_PI * ph[0] + mod)
        for k in range(K):
            ph[k] += f[t] * ratios[k] / 44100.0
            if ph[k] > 1.0:
                ph[k] -= 1.0
    return y


# ------------------------------------------------------------------ wavetables

TABLES = ("basic", "vocal", "harsh", "fm", "pwm")
_WT_FRAMES = 32
_WT_SIZE = 2048
_WT_CACHE = {}
_NH_LEVELS = np.array([1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1023])


def _harmonics(table, k, K, H):
    """Complex harmonic amplitudes 1..H of frame k of K."""
    x = k / (K - 1)
    h = np.arange(1, H + 1, dtype=np.float64)
    if table == "basic":   # sine -> triangle -> saw -> square
        sine = (h == 1).astype(float)
        sgn = np.where(((h.astype(np.int64) - 1) // 2) % 2 == 0, 1.0, -1.0)
        tri = np.where(h % 2 == 1, 8 / np.pi ** 2 / h ** 2 * sgn, 0.0)
        saw = 2 / np.pi / h * (-1.0) ** (h + 1)
        sq = np.where(h % 2 == 1, 4 / np.pi / h, 0.0)
        seq = [sine, tri, saw, sq]
        s = x * 3
        i = min(int(s), 2)
        fr = s - i
        return (seq[i] * (1 - fr) + seq[i + 1] * fr).astype(np.complex128) * 1j
    if table == "vocal":   # a saw shaped by a formant envelope moving oo -> oh -> ah -> eh -> ee
        p = x * 4
        i = min(int(p), 3)
        fr = p - i
        F = VOWEL_F[i] * (1 - fr) + VOWEL_F[i + 1] * fr
        f0 = 110.0                                     # the formants are placed for an A2 (harmonic n = n x 110 Hz)
        env = np.zeros(H)
        for j in range(3):
            bw = F[j] / VOWEL_Q[j]
            env += VOWEL_G[j] / (1 + ((h * f0 - F[j]) / bw) ** 2)
        return (env * 2 / np.pi / h ** 0.3).astype(np.complex128) * 1j
    # time-domain frames, analysed into harmonics
    N = 8192
    t = np.arange(N) / N
    if table == "harsh":   # hard-synced saw, slave ratio 1 -> 8
        r = 1 + 7 * x
        w = 2 * ((t * r) % 1.0) - 1
    elif table == "fm":    # 2-op FM 1:1 (carrier) with a 2:1 modulator, index 0 -> 8
        w = np.sin(TWO_PI * t + 8 * x * np.sin(TWO_PI * 2 * t))
    elif table == "pwm":   # pulse width 0.5 -> 0.03
        w = np.where(t < 0.5 - 0.47 * x, 1.0, -1.0)
    else:
        raise ValueError(f"unknown wavetable '{table}' ({', '.join(TABLES)})")
    X = np.fft.rfft(w) / (N / 2)
    return X[1:H + 1]


def _table(table, nh):
    key = (table, nh)
    if key not in _WT_CACHE:
        fr = np.zeros((_WT_FRAMES, _WT_SIZE + 1))
        for k in range(_WT_FRAMES):
            spec = np.zeros(_WT_SIZE // 2 + 1, dtype=np.complex128)
            spec[1:nh + 1] = _harmonics(table, k, _WT_FRAMES, nh)
            w = np.fft.irfft(spec, _WT_SIZE) * (_WT_SIZE / 2)
            fr[k, :_WT_SIZE] = w
            fr[k, _WT_SIZE] = w[0]
        peak = np.abs(fr).max()
        fr /= peak if peak > 0 else 1.0
        _WT_CACHE[key] = fr
    return _WT_CACHE[key]


@njit(cache=True)
def _wt_kernel(frames, f, pos, ph0):
    n = len(f)
    K = frames.shape[0]
    S = frames.shape[1] - 1
    y = np.empty(n)
    ph = ph0
    for t in range(n):
        p = pos[t]
        if p < 0.0:
            p = 0.0
        if p > 1.0:
            p = 1.0
        fp = p * (K - 1)
        k = int(fp)
        if k > K - 2:
            k = K - 2
        fk = fp - k
        xs = ph * S
        i = int(xs)
        fi = xs - i
        a = frames[k, i] + (frames[k, i + 1] - frames[k, i]) * fi
        b = frames[k + 1, i] + (frames[k + 1, i + 1] - frames[k + 1, i]) * fi
        y[t] = a + (b - a) * fk
        ph += f[t] / 44100.0
        if ph >= 1.0:
            ph -= math.floor(ph)
    return y


# ------------------------------------------------------------------ the voice

DEFAULTS = dict(attack=0.004, decay=0.3, sustain_level=1.0, release=0.08, voices=1, detune=12.0, spread=0.7,
                fold=0.0, drive=0.0, bits=0, vowel=None, vowel_mix=1.0, vowel_q=1.0, formant_shift=1.0,
                filter="lp", cutoff=16000.0, reso=0.0, keytrack=0.0, out=0.5, glide_ms=60.0)


def _core(kind, p, fr, n, mods, rng):
    """One unison voice of the core oscillator at frequency curve fr."""
    if kind == "fmgrowl":
        ops = p.get("ops") or [{"ratio": 1.0}, {"ratio": 1.0, "index": 3.0}]
        K = len(ops)
        if not 2 <= K <= 4:
            raise ValueError("fmgrowl: `ops` takes 2-4 operators (the first is the carrier)")
        ratios = np.array([float(o.get("ratio", 1.0)) for o in ops])
        idx = np.zeros((K, n))
        base_all = mods.get("index", 0.0)
        for k in range(1, K):
            idx[k] = float(ops[k].get("index", 2.0)) + base_all + mods.get(f"index.{k}", 0.0)
        idx = np.maximum(idx, 0.0)
        fb = np.broadcast_to(np.asarray(float(p.get("feedback", 0.0)) + mods.get("feedback", 0.0), dtype=np.float64),
                             (n,)).copy()
        algo = 1 if p.get("algo", "stack") == "parallel" else 0
        return _fm_kernel(fr, ratios, idx, np.clip(fb, 0, 3), algo, rng.random(K))
    table = p.get("table", "basic")
    nh = int(SR * 0.45 / max(float(fr.max()), 20.0))
    nh = int(_NH_LEVELS[_NH_LEVELS <= max(nh, 1)].max())
    pos = np.broadcast_to(np.asarray(float(p.get("pos", 0.0)) + mods.get("pos", 0.0), dtype=np.float64), (n,)).copy()
    return _wt_kernel(_table(table, nh), fr, pos, rng.random())


def bass_voice(kind, p, f, vel, dur):
    """One note of `fmgrowl` or `wavetable`. Returns stereo (2, n)."""
    q = dict(DEFAULTS)
    q.update(p)
    rng = _rng()
    hold = I._n(dur)
    env = I.adsr(hold, q["attack"], q["decay"], q["sustain_level"], q["release"])
    n = len(env)
    t = np.arange(n) / SR
    mods = mod_curves(q, n, hold, vel)
    semis = mods.get("pitch", 0.0)
    gf = q.get("_glide_from")
    if gf:
        tau = max(float(q["glide_ms"]), 1.0) / 1000 / 2.3
        semis = semis + 12 * np.log2(float(gf) / f) * np.exp(-t / tau)
    base = f * 2 ** (np.broadcast_to(np.asarray(semis, dtype=np.float64), (n,)) / 12)
    voices = max(1, int(q["voices"]))
    det = float(q["detune"])
    offs = np.array([0.0]) if voices == 1 else np.linspace(-1, 1, voices)
    L = np.zeros(n)
    R = np.zeros(n)
    sp = float(q["spread"])
    for o in offs:
        x = _core(kind, q, base * 2 ** (o * det / 1200), n, mods, rng)
        a = (o * sp + 1) * np.pi / 4
        L += x * np.cos(a) * np.sqrt(2)
        R += x * np.sin(a) * np.sqrt(2)
    L /= np.sqrt(voices)
    R /= np.sqrt(voices)
    out = []
    for x in (L, R):
        fold = np.clip(float(q["fold"]) + mods.get("fold", 0.0), 0, 1)
        if np.any(fold > 0):
            g = 1 + 6 * fold
            x = np.sin(np.pi / 2 * g * x) * (1 - 0.3 * fold)
        dr = np.clip(float(q["drive"]) + mods.get("drive", 0.0), 0, 1)
        if np.any(dr > 0):
            k = 1 + 9 * dr
            x = np.tanh(x * k) / np.tanh(k)
        bits = int(q["bits"])
        if bits > 0:
            lv = 2 ** (bits - 1)
            x = np.round(x * lv) / lv
        vw = q.get("vowel")
        if vw is not None or "vowel" in mods:
            pos = np.broadcast_to(np.asarray(vowel_pos(vw if vw is not None else 2) + mods.get("vowel", 0.0),
                                             dtype=np.float64), (n,)).copy()
            m = float(q["vowel_mix"])
            x = x * (1 - m) + formant(x, pos, float(q["vowel_q"]), float(q["formant_shift"])) * m
        ft = q["filter"]
        if ft != "none":
            cut = float(q["cutoff"]) * (f / 261.63) ** float(q["keytrack"])
            cut = cut * 2 ** np.broadcast_to(np.asarray(mods.get("cutoff", 0.0), dtype=np.float64), (n,))
            reso = np.clip(float(q["reso"]) + mods.get("reso", 0.0), 0, 1)
            qq = np.broadcast_to(np.asarray(0.707 + reso * 9, dtype=np.float64), (n,)).copy()
            x = svf(np.ascontiguousarray(x), np.ascontiguousarray(cut, dtype=np.float64), qq,
                    {"lp": 0, "bp": 1, "hp": 2}[ft])
        out.append(x)
    amp = env.astype(np.float64) * vel * float(q["out"])
    if "level" in mods:
        amp = amp * 10 ** (mods["level"] / 20)
    y = np.stack(out) * amp
    if "pan" in mods:
        a = (np.clip(mods["pan"], -1, 1) + 1) * np.pi / 4
        y = y * np.stack([np.cos(a), np.sin(a)]) * np.sqrt(2)
    return y.astype(np.float32)


def fmgrowl(p, f, vel, dur):
    return bass_voice("fmgrowl", p, f, vel, dur)


def wavetable(p, f, vel, dur):
    return bass_voice("wavetable", p, f, vel, dur)


# ------------------------------------------------------------------ sampler (resampling)

def sampler(p, f, vel, dur):
    """One note of `sampler`: plays the region of audio the engine rendered from the `source` track (studio.py puts it
    in p["_src"], stereo). mode "pitch" (default): the note transposes the region from `root` (C3) by resampling
    (slower and lower, like a tape); mode "slice": the region is cut into `slices` equal parts and the note picks one
    chromatically from `root` (C3 = slice 0), at `pitch` semitones (0); a note's "/s=3" picks slice 3 whatever its
    pitch. `reverse`, `start` (0-1 into the region or slice), `attack_ms` (2), `release_ms` (30), `gain_db` (0). The
    note's length gates the sound (a sampler holding its key); a slid note (`~`, with `glide_ms`) slides its rate."""
    from hand import note_to_midi, midi_to_hz
    src = p.get("_src")
    if src is None or src.shape[1] < 2:  # no source audio (a gallery call, an empty region): silence
        return np.zeros((2, 16), dtype=np.float32)
    root = float(midi_to_hz(note_to_midi(p.get("root", "C3"))))
    mode = p.get("mode", "pitch")
    a = src
    if mode == "slice":
        N = max(1, int(p.get("slices", 8)))
        k = None
        for t in p.get("_art") or []:
            if t.startswith("s="):
                k = int(t[2:])
        if k is None:
            k = int(round(12 * np.log2(f / root)))
        k %= N
        L = src.shape[1] // N
        a = src[:, k * L:(k + 1) * L]
        rate = 2 ** (float(p.get("pitch", 0.0)) / 12)
    else:
        rate = f / root
    if p.get("reverse"):
        a = a[:, ::-1]
    s0 = int(float(p.get("start", 0.0)) * a.shape[1])
    a = a[:, s0:]
    hold = I._n(dur)
    rel = I._n(float(p.get("release_ms", 30.0)) / 1000)
    n = hold + rel
    t = np.arange(n)
    r = np.full(n, rate)
    gf = p.get("_glide_from")
    if gf:
        tau = max(float(p.get("glide_ms", 60.0)), 1.0) / 1000 * SR / 2.3
        r = rate * 2 ** (np.log2(float(gf) / f) * np.exp(-t / tau))
    pos = np.concatenate([[0.0], np.cumsum(r[:-1])])
    m = pos < a.shape[1] - 1
    y = np.zeros((2, n))
    for c in range(2):
        y[c, m] = np.interp(pos[m], np.arange(a.shape[1]), a[c])
    env = np.ones(n)
    at = I._n(float(p.get("attack_ms", 2.0)) / 1000)
    env[:at] = np.linspace(0, 1, at)
    env[hold:] = np.exp(-np.arange(rel) / max(rel / 5, 1))
    end = int(m.sum())
    if 0 < end < n:
        fo = min(64, end)
        env[end - fo:end] *= np.linspace(1, 0, fo)
    return (y * env * vel * 10 ** (float(p.get("gain_db", 0.0)) / 20)).astype(np.float32)
