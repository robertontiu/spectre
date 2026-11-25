"""Modern synth voice and low-end / top-end sources (queue item 9b, sound side; docs/PRODUCTION.md "Gaps and
proposals" 4 and 5; docs/MANUAL.md "Production: stacks, buses, synth voice").

Additive: nothing here is used unless a project asks for it. Every random draw goes through `instruments.RNG` at call
time, so per-track seeds (`"seeds": "per-track"`) give each track and each stack layer its own streams.

  polysynth      a general subtractive voice: up to several oscillators (saw, square/pulse, triangle, sine, noise,
                 supersaw) with unison, a sub and a noise layer, a filter (lp/hp/bp) with envelope and key tracking,
                 a second envelope, LFOs, analogue drift and delayed vibrato as modulation sources assignable to
                 cutoff, pitch, level, pan, pulse width and detune. STEREO.
  supersaw v2    `supersaw` with `"model": 2`: Szabo's (2010) measured JP-8000 behaviour (the pitch-tracking high-pass
                 at the fundamental, the mix curve that lowers the centre saw as it raises the sides, the 11th-order
                 detune curve for `knob`), on the polysynth core, so every polysynth feature works on it.
  sub            a clean monophonic sine or triangle sub line with glide (phase-continuous), optional 2nd/3rd
                 harmonics for small speakers.
  kicksub, kickpunch, kickclick
                 the three layers of a modern kick (tuned sub/body 45-80 Hz, punch 100-200 Hz, click 2-5 kHz), each a
                 drum, tunable to the key (`note`), to be stacked.
  metalhat       a hi-hat or cymbal built from tones: six square oscillators at the TR-808's metal frequencies, ring
                 sums and band-passed, plus high modal partials; noise only as a small seasoning.
  air            an air layer: detuned saws an octave up and pitched noise (noise gated at the note's period), both
                 high-passed (default 7 kHz). STEREO.
"""
import numpy as np
from scipy import signal

import instruments as I

SR = I.SR
TWO_PI = 2 * np.pi


def _rng():
    return I.RNG


def note_hz(p, default):
    """A `note` ("F1") or a `tune` in Hz; `note` wins."""
    if p.get("note"):
        from hand import note_to_midi, midi_to_hz
        return float(midi_to_hz(note_to_midi(p["note"])))
    return float(p.get("tune", default))


# ------------------------------------------------------------------ oscillators

def _phase(freq, n, ph0):
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    dt = f / SR
    return (np.cumsum(dt) + ph0), dt


def _blep(t, dt):
    """PolyBLEP residual for a discontinuity at phase 0 (t in [0,1))."""
    y = np.zeros_like(t)
    m1 = t < dt
    x = t[m1] / dt[m1]
    y[m1] = x + x - x * x - 1
    m2 = t > 1 - dt
    x = (t[m2] - 1) / dt[m2]
    y[m2] = x * x + x + x + 1
    return y


def osc(shape, freq, n, ph0=None, pw=0.5):
    """One band-limited oscillator. freq: scalar or (n,) Hz; pw: scalar or (n,) for pulse."""
    if ph0 is None:
        ph0 = _rng().random()
    if shape == "noise":
        return _rng().standard_normal(n).astype(np.float32)
    ph, dt = _phase(freq, n, ph0)
    t = ph % 1.0
    if shape == "sine":
        return np.sin(TWO_PI * ph).astype(np.float32)
    if shape == "triangle":  # harmonics fall as 1/k^2: the naive shape aliases little
        return (1 - 4 * np.abs(t - 0.5)).astype(np.float32)
    saw = 2 * t - 1 - _blep(t, dt)
    if shape == "saw":
        return saw.astype(np.float32)
    if shape in ("square", "pulse"):
        w = np.clip(np.broadcast_to(np.asarray(pw if shape == "pulse" else 0.5, dtype=np.float64), (n,)), 0.02, 0.98)
        t2 = (t + 1 - w) % 1.0  # a second saw shifted by the pulse width
        saw2 = 2 * t2 - 1 - _blep(t2, dt)
        return (0.5 * (saw - saw2)).astype(np.float32)
    raise ValueError(f"unknown oscillator shape '{shape}' (saw, square, pulse, triangle, sine, noise, supersaw)")


# Szabo (2010), "How to Emulate the Super Saw" (KTH): the JP-8000's detune knob, measured, as an 11th-order fit
# (offsets in instruments.SZABO, multiplied by f x curve(knob)), and the mix knob's centre and side gains.
_SZ_DET = [10028.7312891634, -50818.8652045924, 111363.4808729368, -138150.6761080548, 106649.6679158292,
           -53046.9642751875, 17019.9518580080, -3425.0836591318, 404.2703938388, -24.1878824391, 0.6717417634,
           0.0030115596]


def szabo_detune(knob):
    """Szabo's detune curve: knob 0-1 -> the factor the offsets are scaled by (about 0.003 at 0, 1.0 at 1)."""
    return float(np.polyval(_SZ_DET, float(np.clip(knob, 0, 1))))


def szabo_mix(mix):
    """Szabo's mix curve: (centre gain, side gain) for mix 0-1."""
    m = float(np.clip(mix, 0, 1))
    return -0.55366 * m + 0.99785, -0.73764 * m * m + 1.2841 * m + 0.044372


# ------------------------------------------------------------------ modulation

def _lfo_wave(shape, ph, rng):
    t = ph % 1.0
    if shape == "sine":
        return np.sin(TWO_PI * ph)
    if shape == "triangle":
        return 1 - 4 * np.abs(t - 0.5)
    if shape == "saw":
        return 2 * t - 1
    if shape == "square":
        return np.where(t < 0.5, 1.0, -1.0)
    if shape in ("random", "smooth"):  # sample and hold per cycle, smoothed for "smooth"
        k = np.floor(ph).astype(np.int64)
        k -= k.min()
        vals = rng.uniform(-1, 1, int(k.max()) + 2)
        if shape == "random":
            return vals[k]
        return vals[k] + (vals[k + 1] - vals[k]) * (0.5 - 0.5 * np.cos(np.pi * t))
    raise ValueError(f"unknown lfo shape '{shape}'")


def _drift_curve(n, rate, rng):
    """Slow random wander, unit standard deviation: smoothed noise at about `rate` Hz (analogue drift)."""
    m = max(4, int(n / SR * rate * 4) + 4)
    pts = rng.standard_normal(m)
    x = np.linspace(0, m - 3, n)
    i = np.floor(x).astype(np.int64)
    fr = x - i
    w = 0.5 - 0.5 * np.cos(np.pi * fr)
    return (pts[i] * (1 - w) + pts[i + 1] * w)


def mod_sources(p, n, hold, vel):
    """The modulation per destination for one note: dict dest -> (n,) curve in the destination's units
    (cutoff: octaves, pitch: cents, level: dB, pan: -1..1, pw: fraction, detune: fraction of the detune)."""
    rng = _rng()
    t = np.arange(n) / SR
    out = {}

    def add(dest, curve):
        out[dest] = out.get(dest, 0.0) + curve
    for L in p.get("lfo", []) or []:
        rate = float(L.get("rate", 0.5))
        ph0 = rng.random() if L.get("phase", "free") == "free" else float(L.get("phase0", 0.0))
        w = _lfo_wave(L.get("shape", "sine"), ph0 + rate * t, rng)
        d = float(L.get("delay", 0.0))
        if d > 0:  # fades in after `delay` s, over `fade` s
            w = w * np.clip((t - d) / max(float(L.get("fade", 0.3)), 1e-3), 0, 1)
        add(L.get("dest", "cutoff"), float(L.get("depth", 0.3)) * w)
    e2 = p.get("env2")
    if e2:
        env = I.adsr(hold, e2.get("attack", 0.01), e2.get("decay", 0.3), e2.get("sustain", 0.0), e2.get("release", 0.3))
        env = np.pad(env, (0, max(0, n - len(env))))[:n]
        add(e2.get("dest", "cutoff"), float(e2.get("depth", 1.0)) * env * (vel if e2.get("vel", True) else 1.0))
    vib = float(p.get("vibrato", 0.0))
    if vib > 0:  # delayed vibrato in cents, fading in over 0.3 s
        d = float(p.get("vib_delay", 0.25))
        rate = float(p.get("vib_rate", 5.5))
        add("pitch", vib * np.sin(TWO_PI * rate * t + rng.random() * TWO_PI) * np.clip((t - d) / 0.3, 0, 1))
    return out


# ------------------------------------------------------------------ filters with moving cutoff

def tv_filter(x, cut, q, kind="lp", B=256):
    """Biquad (lp, hp, bp) whose cutoff follows `cut` (Hz per sample), block-wise; settled cutoffs finish in one call."""
    n = len(x)
    y = np.empty(n, dtype=np.float32)
    zi = np.zeros(2)
    cut = np.broadcast_to(np.asarray(cut, dtype=np.float64), (n,))
    s = 0
    while s < n:
        c = float(cut[s])
        e = n if np.all(np.abs(cut[s:] - c) < 0.02 * c) else min(n, s + B)
        if kind == "bp":
            fc = float(np.clip(c, 10, SR * 0.45))
            w = TWO_PI * fc / SR
            al = np.sin(w) / (2 * q)
            b = np.array([al, 0, -al])
            a = np.array([1 + al, -2 * np.cos(w), 1 - al])
            b, a = b / a[0], a / a[0]
        else:
            b, a = I._biquad(kind, c, q)
        y[s:e], zi = signal.lfilter(b, a, x[s:e], zi=zi)
        s = e
    return y


def _hp2(x, f):
    sos = signal.butter(2, float(np.clip(f, 10, SR * 0.45)), btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


# ------------------------------------------------------------------ the voice

def _unison(o, voices):
    """Detune offsets (fractions of the outer offset, -1..1) and per-voice pan weights for one oscillator."""
    if o.get("shape") == "supersaw" or o.get("curve") == "szabo":
        offs = I._detune_offsets(voices)                   # Szabo's uneven offsets, outer = +-1
    else:
        offs = np.array([0.0]) if voices <= 1 else np.linspace(-1, 1, voices)
    return offs


def voice(p, f, vel, dur, oscs):
    """Render one note of the polysynth core. Returns stereo (2, n)."""
    rng = _rng()
    hold = I._n(dur)
    env = I.adsr(hold, p.get("attack", 0.005), p.get("decay", 0.3), p.get("sustain_level", 0.85), p.get("release", 0.25))
    n = len(env)
    t = np.arange(n) / SR
    mods = mod_sources(p, n, hold, vel)
    pitch_c = mods.get("pitch", 0.0)
    gf = p.get("_glide_from")
    if gf:  # slide (opt-in with `glide_ms`): from the previous note's pitch, an exponential (RC-like) approach
        tau = max(float(p.get("glide_ms", 80.0)), 1.0) / 1000 / 2.3
        pitch_c = pitch_c + 1200 * np.log2(float(gf) / f) * np.exp(-t / tau)
    drift = float(p.get("drift", 0.0))
    L = np.zeros(n)
    R = np.zeros(n)
    norm2 = 0.0
    for o in oscs:
        shape = o.get("shape", "saw")
        voices = int(o.get("voices", 1))
        lvl = float(o.get("level", 1.0))
        base = f * 2 ** (float(o.get("octave", 0)) + float(o.get("semi", 0)) / 12 + float(o.get("cents", 0)) / 1200)
        offs = _unison(o, voices)
        if o.get("knob") is not None:                       # Szabo's knob: outer offset = curve(knob) x 11%
            outer = 1200 * np.log2(1 + 0.11 * szabo_detune(o["knob"]))
        else:
            outer = float(o.get("detune", 20.0 if voices > 1 else 0.0))
        det_mod = mods.get("detune", 0.0)
        if shape == "supersaw" or o.get("curve") == "szabo":
            cg, sg = szabo_mix(o.get("mix", 0.7)) if o.get("mix_curve", True) else (1.0, float(o.get("mix", 0.7)))
        else:
            cg, sg = 1.0, float(o.get("mix", 1.0))
        spread = float(o.get("spread", 0.8))
        osh = "saw" if shape == "supersaw" else shape
        order = np.argsort(np.abs(offs))
        for rank, i in enumerate(order):
            c = offs[i] * outer * (1 + det_mod)
            dr = 0.0
            if drift > 0:  # analogue drift: each voice wanders on its own, a few cents
                dr = 3.0 * drift * _drift_curve(n, 0.6, rng)
            fr = base * 2 ** ((c + pitch_c + dr) / 1200)
            pw = float(o.get("pw", 0.5)) + mods.get("pw", 0.0) if osh == "pulse" else 0.5
            x = osc(osh, fr, n, pw=pw).astype(np.float64)
            centre = rank == 0 and (voices % 2 == 1 or voices == 1)
            g = (cg if centre else sg) * lvl
            if centre:
                L += x * g
                R += x * g
                norm2 += g * g
                continue
            side = 1 if rank % 2 else -1
            pan = side * spread * (0.35 + 0.65 * abs(offs[i]))
            a = (pan + 1) * np.pi / 4
            L += x * g * np.cos(a) * np.sqrt(2)
            R += x * g * np.sin(a) * np.sqrt(2)
            norm2 += g * g
    norm = 1 / np.sqrt(max(norm2, 1e-9))
    L *= norm
    R *= norm
    # the pitch-tracking high-pass (Szabo: at the fundamental, removing what lies under it)
    if p.get("hpf_track"):
        fh = f * float(p.get("hpf_track_ratio", 1.0))
        L, R = _hp2(L, fh), _hp2(R, fh)
    # sub and noise layers (after the high-pass: the sub is meant to be below it)
    sub = float(p.get("sub", 0.0))
    if sub > 0:
        fs = f * 2 ** float(p.get("sub_octave", -1)) * 2 ** (pitch_c / 1200)
        s = osc(p.get("sub_shape", "sine"), fs, n, ph0=0.0).astype(np.float64) * sub
        L += s
        R += s
    nz = float(p.get("noise", 0.0))
    if nz > 0:
        w = rng.standard_normal((2, n))
        w = signal.sosfilt(signal.butter(2, [float(p.get("noise_hp", 6000)), min(float(p.get("noise_lp", 16000)), SR * 0.45)],
                                         btype="band", fs=SR, output="sos"), w)
        L += w[0] * nz * 0.5
        R += w[1] * nz * 0.5
    # filter: cutoff from the param, velocity, key tracking, envelope, modulation
    ftype = p.get("filter", "lp")
    if ftype != "none":
        cut0 = float(p.get("cutoff", 9000)) * (0.75 + 0.35 * vel)
        kt = float(p.get("keytrack", 0.0))
        if kt:
            cut0 *= (f / 261.63) ** kt
        cut = np.full(n, cut0)
        if float(p.get("env", 0.0)) > 0:
            if p.get("_accent"):  # accent (opt-in with `accent`): a deeper, shorter filter envelope
                ac = float(p.get("accent", 0.0))
                cut = cut + float(p["env"]) * (1 + ac) * vel * np.exp(-t / (float(p.get("fdecay", 0.25)) * (1 - 0.4 * min(ac, 1.0))))
            else:
                cut = cut + float(p["env"]) * vel * np.exp(-t / float(p.get("fdecay", 0.25)))
        if "cutoff" in mods:
            cut = cut * 2 ** mods["cutoff"]
        if drift > 0:
            cut = cut * 2 ** (0.08 * drift * _drift_curve(n, 0.4, rng))
        cut = np.clip(cut, 20, SR * 0.45)
        q = 0.707 + float(p.get("reso", 0.0)) * 4
        fs_ = float(p.get("filter_spread", 0.0))  # left and right filters a little apart (stereo motion)
        L = tv_filter(L, cut * 2 ** (-fs_ / 2), q, ftype)
        R = tv_filter(R, cut * 2 ** (fs_ / 2), q, ftype)
    amp = env.astype(np.float64)
    if "level" in mods:
        amp = amp * 10 ** (mods["level"] / 20)
    out = np.stack([L, R]) * amp * vel * float(p.get("out", 0.55))
    if p.get("_accent"):
        out = out * (1 + 0.5 * float(p.get("accent", 0.0)))
    if "pan" in mods:
        a = (np.clip(mods["pan"], -1, 1) + 1) * np.pi / 4
        out = out * np.stack([np.cos(a), np.sin(a)]) * np.sqrt(2)
    return out.astype(np.float32)


def polysynth(p, f, vel, dur):
    """General subtractive voice; `osc` lists the oscillators (default: one saw)."""
    oscs = p.get("osc") or [{"shape": "saw"}]
    if isinstance(oscs, dict):
        oscs = [oscs]
    return voice(p, f, vel, dur, oscs)


def supersaw2(p, f, vel, dur):
    """`supersaw` with "model": 2 (Szabo's behaviour on the polysynth core). `detune` (cents of the outer voice, as
    model 1) or `knob` (0-1 through Szabo's curve), `mix` through Szabo's mix curve, the pitch-tracking high-pass on by
    default, `osc2` (a second oscillator: {"shape", "octave", "semi", "level", "voices", "detune"}), `sub`, `noise`,
    `drift`, `lfo`, `env2`, `vibrato` and the filter params of model 1."""
    o1 = {"shape": "supersaw", "voices": int(p.get("voices", 7)), "mix": p.get("mix", 0.7),
          "spread": p.get("spread", 0.8), "level": 1.0}
    if p.get("knob") is not None:
        o1["knob"] = p["knob"]
    else:
        o1["detune"] = p.get("detune", 25.0)
    oscs = [o1]
    o2 = p.get("osc2")
    if o2:
        o2 = dict(o2)
        o2.setdefault("shape", "supersaw")
        o2.setdefault("level", 0.5)
        if o2["shape"] == "supersaw":
            o2.setdefault("voices", o1["voices"])
            o2.setdefault("mix", o1["mix"])
            o2.setdefault("spread", o1["spread"])
            if "knob" in o1 and "detune" not in o2:
                o2.setdefault("knob", o1["knob"])
            else:
                o2.setdefault("detune", o1.get("detune", 25.0))
        oscs.append(o2)
    q = dict(p)
    q.setdefault("hpf_track", True)
    q.setdefault("attack", 0.004)
    q.setdefault("decay", 0.4)
    q.setdefault("sustain_level", 0.9)
    q.setdefault("release", 0.3)
    q.setdefault("out", 0.65)  # the tracking high-pass takes about 1.5 dB of the fundamental: level as model 1
    return voice(q, f, vel, dur, oscs)


def air(p, f, vel, dur):
    """Air layer: detuned saws `octave` up (default +1) and pitched noise, both high-passed at `hp` (7 kHz, 12 dB/oct)
    and low-passed at `lp` (16 kHz). STEREO; `spread` its width. Tonal on purpose: a top made of the note's own
    harmonics reads as brightness, not as static."""
    rng = _rng()
    hold = I._n(dur)
    env = I.adsr(hold, p.get("attack", 0.02), p.get("decay", 0.3), p.get("sustain_level", 0.9), p.get("release", 0.3))
    n = len(env)
    t = np.arange(n) / SR
    fo = f * 2 ** float(p.get("octave", 1))
    voices = int(p.get("voices", 5))
    det = float(p.get("detune", 18.0))
    spread = float(p.get("spread", 1.0))
    L = np.zeros(n)
    R = np.zeros(n)
    offs = np.linspace(-1, 1, voices) if voices > 1 else np.array([0.0])
    for o in offs:
        x = osc("saw", fo * 2 ** (o * det / 1200), n).astype(np.float64)
        a = (o * spread + 1) * np.pi / 4
        L += x * np.cos(a) * np.sqrt(2)
        R += x * np.sin(a) * np.sqrt(2)
    L /= np.sqrt(voices)
    R /= np.sqrt(voices)
    nz = float(p.get("noise", 0.5))
    if nz > 0:  # noise gated at the note's period: breath with a pitch
        gate = np.abs(np.sin(np.pi * fo * t + rng.random() * np.pi)) ** 4
        w = rng.standard_normal((2, n)) * gate
        L = L * (1 - nz) + w[0] * nz * 1.6
        R = R * (1 - nz) + w[1] * nz * 1.6
    sos = signal.butter(2, [float(p.get("hp", 7000)), min(float(p.get("lp", 16000)), SR * 0.45)], btype="band",
                        fs=SR, output="sos")
    L, R = signal.sosfilt(sos, L), signal.sosfilt(sos, R)
    return (np.stack([L, R]) * env * vel * 0.5).astype(np.float32)


# ------------------------------------------------------------------ sub (monophonic line)

def sub_line(p, notes, total_n):
    """`sub`: a clean sine (or `shape` triangle) line, one note at a time, phase-continuous, `~` glides over glide_ms.
    attack (0.005 s), release (0.06 s), decay (0 = held; > 0 = an 808-like fall, seconds), harmonics 0-1 (adds the 2nd
    and 3rd harmonic so the line reads on small speakers), drive 0-1."""
    out = np.zeros(total_n, dtype=np.float32)
    shape = p.get("shape", "sine")
    glide_s = float(p.get("glide_ms", 60)) / 1000
    att, rel = float(p.get("attack", 0.005)), float(p.get("release", 0.06))
    dec = float(p.get("decay", 0.0))
    harm = float(p.get("harmonics", 0.0))
    prev_f, prev_ph = None, 0.0
    for i, nt in enumerate(notes):
        start = nt["t0"]
        if start >= total_n:
            break
        nxt = notes[i + 1]["t0"] if i + 1 < len(notes) else None
        next_glides = nxt is not None and notes[i + 1].get("glide")
        length = nt["n"] + I._n(rel)
        if nxt is not None:
            length = min(length, nxt - start + (0 if next_glides else I._n(0.003)))
        length = int(min(max(length, 16), total_n - start))
        t = np.arange(length) / SR
        glide = nt.get("glide") and prev_f is not None
        fr = np.full(length, nt["f"])
        if glide:
            fr = prev_f * (nt["f"] / prev_f) ** np.clip(t / glide_s, 0, 1)
        ph = (prev_ph if glide else 0.0) + np.cumsum(fr) / SR
        frac = ph % 1.0
        if shape == "triangle":
            x = 1 - 4 * np.abs(frac - 0.5)
        else:
            x = np.sin(TWO_PI * ph)
        if harm > 0:
            x = x + harm * (0.35 * np.sin(2 * TWO_PI * ph) + 0.2 * np.sin(3 * TWO_PI * ph))
        hold = min(nt["n"], length)
        env = np.ones(length)
        if not glide:
            env *= np.clip(t / max(att, 1e-4), 0, 1)
        if dec > 0:
            env *= np.exp(-t / dec)
        env[hold:] *= np.exp(-np.arange(length - hold) / max(I._n(rel) / 5, 1))
        if nxt is not None and not next_glides:
            fo = min(I._n(0.003), length)
            env[-fo:] *= np.linspace(1, 0, fo)
        j = (nxt - start) if nxt is not None else None
        prev_ph = float(ph[j - 1]) if (j is not None and 0 < j <= length) else 0.0
        prev_f = nt["f"]
        y = I.soft((x * env).astype(np.float32), float(p.get("drive", 0.0))) * nt["vel"] * 0.6
        out[start:start + length] += y.astype(np.float32)
    return out


# ------------------------------------------------------------------ kick layers (drums)

def kicksub(p, vel, ps=0.0):
    """Kick sub/body layer: a tuned sine (`note` e.g. "F1", or `tune` Hz, default 50) with a short pitch drop (`punch`
    semitones from above, default 12, over `drop` s 0.012), held for `hold` s (0.04) then a tail of `tail` s (0.12);
    `length` (0.45). The layer that owns 45-80 Hz; tune it to the track's key."""
    f0 = note_hz(p, 50) * 2 ** (ps / 12)
    length = float(p.get("length", 0.45))
    n = I._n(length)
    t = np.arange(n) / SR
    f = f0 * 2 ** (float(p.get("punch", 12)) / 12 * np.exp(-t / float(p.get("drop", 0.012))))
    x = np.sin(TWO_PI * np.cumsum(f) / SR)
    hold = float(p.get("hold", 0.04))
    env = np.where(t < hold, 1.0, np.exp(-(t - hold) / float(p.get("tail", 0.12))))
    env *= np.clip(t / 0.0007, 0, 1)
    fo = min(I._n(0.02), n)
    env[-fo:] *= np.linspace(1, 0, fo)
    y = I.soft((x * env).astype(np.float32), float(p.get("drive", 0.0)))
    return (y * vel ** 1.1).astype(np.float32)


def kickpunch(p, vel, ps=0.0):
    """Kick punch layer: a short body around `tune` (130 Hz) swept down from `sweep` x tune (3) in about 15 ms, with
    a decay of `decay` s (0.045): the 100-200 Hz knock that is kept short."""
    f0 = note_hz(p, 130) * 2 ** (ps / 12)
    dec = float(p.get("decay", 0.045))
    n = I._n(dec * 6 + 0.01)
    t = np.arange(n) / SR
    f = f0 * (1 + (float(p.get("sweep", 3.0)) - 1) * np.exp(-t / 0.015))
    x = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / dec) * np.clip(t / 0.0005, 0, 1)
    nz = I.bp(_rng().standard_normal(n).astype(np.float32), 90, 400) * np.exp(-t / (dec * 0.5)) * float(p.get("thump", 0.3))
    y = I.soft((x + nz).astype(np.float32), float(p.get("drive", 0.2)))
    return (y * vel ** 1.1).astype(np.float32)


def kickclick(p, vel, ps=0.0):
    """Kick click/top layer: a 2-5 kHz transient. A fast downward chirp (`tone` Hz, 3200, from 2.5 x) plus a band of
    noise (`noise` 0-1, 0.5) around it, gone in `decay` s (0.006)."""
    f0 = float(p.get("tone", 3200)) * 2 ** (ps / 12)
    dec = float(p.get("decay", 0.012))
    n = I._n(dec * 8 + 0.005)
    t = np.arange(n) / SR
    f = f0 * (1 + 1.5 * np.exp(-t / 0.002))
    ch = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / dec)
    nz = I.bp(_rng().standard_normal(n).astype(np.float32), f0 * 0.6, min(f0 * 2.2, SR * 0.44)) * np.exp(-t / (dec * 0.6))
    a = float(p.get("noise", 0.5))
    y = (ch * (1 - a) + nz * a * 1.4) * np.clip(t / 0.0002, 0, 1)
    return (y * vel).astype(np.float32)


# ------------------------------------------------------------------ tonal hats and cymbals

# TR-808 metal section: six square-wave oscillators (Roland TR-808 service notes; as used for its hats and cymbal)
TR808_METAL = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0])
_MH_CACHE = {}


def metalhat(p, vel, ps=0.0):
    """Hi-hat or cymbal from tones. The six square oscillators of the TR-808's metal section (x `tune`), summed and
    band-passed at `tone` (8500 Hz; the squares' dense high harmonics form an inharmonic, metallic cluster), plus
    `partials` (0-1, 0.5) high modal partials (6-15 kHz, each with its own decay: shimmer), plus `noise` (0-1, 0.12)
    as seasoning. decay s (0.05 closed; 0.3-0.8 open, `open`: true picks 0.4), `bright` 0-1 (0.5; tilt of the
    partials), `lp` (15000), `seed` (another metal). Round-robin: each hit draws new phases."""
    rng = _rng()
    dec = float(p.get("decay", 0.4 if p.get("open") else 0.05))
    n = I._n(dec * 5 + 0.02)
    t = np.arange(n) / SR
    tune = float(p.get("tune", 1.0)) * 2 ** (ps / 12)
    sq = np.zeros(n)
    for fr in TR808_METAL * tune:
        sq += np.sign(np.sin(TWO_PI * fr * t + rng.random() * TWO_PI))
    tone = float(p.get("tone", 8500))
    sos = signal.butter(2, [tone * 0.7, min(tone * 1.7, SR * 0.45)], btype="band", fs=SR, output="sos")
    metal = signal.sosfilt(sos, sq) * 0.25
    k = 24
    srng = np.random.default_rng(int(p.get("seed", 7)))   # the cymbal's own modes: fixed per `seed`
    fr = np.exp(srng.uniform(np.log(6000), np.log(15000), k)) * tune
    bright = float(p.get("bright", 0.5))
    am = (fr / 6000) ** (-1.5 + 1.5 * bright) * srng.uniform(0.4, 1.0, k)
    dc = dec * srng.uniform(0.5, 1.4, k) * (fr / 9000) ** -0.5
    part = (am[:, None] * np.sin(TWO_PI * fr[:, None] * t[None, :] + rng.uniform(0, TWO_PI, (k, 1)))
            * np.exp(-t[None, :] / dc[:, None])).sum(0)
    part *= 0.08 * float(p.get("partials", 0.5))
    nz = signal.sosfilt(signal.butter(2, tone * 0.8, btype="high", fs=SR, output="sos"), rng.standard_normal(n))
    nz *= 0.12 * float(p.get("noise", 0.12))
    x = (metal + nz) * np.exp(-t / dec) + part
    x = signal.sosfilt(signal.butter(2, min(float(p.get("lp", 15000)), SR * 0.45), fs=SR, output="sos"), x)
    x *= np.clip(t / 0.0003, 0, 1)
    if vel < 0.7:  # softer hits are darker
        x = signal.sosfilt(signal.butter(1, 6000 + 12000 * vel, fs=SR, output="sos"), x)
    return (x * vel * 1.6).astype(np.float32)
