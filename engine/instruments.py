"""Synthesized instruments. Every function returns a mono float32 array at SR.

Drums: f(params, vel, pitch_semis) -> array
Tonal: f(params, freq, vel, dur_sec) -> array (includes release tail)
"""
import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(1234)


def _t(n):
    return np.arange(n, dtype=np.float32) / SR


def _n(sec):
    return max(1, int(sec * SR))


def bp(x, lo, hi, order=2):
    hi = min(hi, SR * 0.45)
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


def hp(x, f, order=2):
    sos = signal.butter(order, min(f, SR * 0.45), btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


def lp(x, f, order=2):
    sos = signal.butter(order, min(f, SR * 0.45), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


def noise(n):
    return RNG.standard_normal(n).astype(np.float32)


def soft(x, drive):
    if drive <= 0:
        return x
    k = 1 + drive * 6
    return (np.tanh(x * k) / np.tanh(k)).astype(np.float32)


def polyblep_saw(freq, n, phase0=None):
    """freq: scalar or array of length n."""
    f = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    dt = f / SR
    ph = np.cumsum(dt) + (RNG.random() if phase0 is None else phase0)
    t = ph % 1.0
    y = 2 * t - 1
    m1 = t < dt
    x = t[m1] / dt[m1]
    y[m1] -= x + x - x * x - 1
    m2 = t > 1 - dt
    x = (t[m2] - 1) / dt[m2]
    y[m2] -= x * x + x + x + 1
    return y.astype(np.float32)


def adsr(n_hold, a, d, s, r):
    """n_hold = samples the key is held. Returns env of len n_hold + release."""
    na, nd, nr = _n(a), _n(d), _n(r)
    env = np.empty(n_hold + nr, dtype=np.float32)
    seg = np.concatenate([
        np.linspace(0, 1, na, endpoint=False),
        1 - (1 - s) * (1 - np.exp(-np.arange(nd) / max(nd / 4, 1))),
    ])
    if len(seg) >= n_hold:
        env[:n_hold] = seg[:n_hold]
    else:
        env[:len(seg)] = seg
        env[len(seg):n_hold] = s
    last = env[n_hold - 1] if n_hold > 0 else 0
    env[n_hold:] = last * np.exp(-np.arange(nr) / max(nr / 5, 1))
    return env


# ---------------------------------------------------------------- drums

def kick(p, vel, ps=0.0):
    tune = p.get("tune", 52) * 2 ** (ps / 12)
    decay = p.get("decay", 0.32)
    n = _n(decay * 4 + 0.05)
    t = _t(n)
    f = tune * (1 + p.get("punch", 1.0) * 3.2 * np.exp(-t / 0.022))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    click = hp(noise(n), 2500) * np.exp(-t / 0.0025) * p.get("click", 0.4) * vel
    x = body + click * 0.6
    x = soft(x, p.get("drive", 0.15))
    return x * vel ** 1.2


def snare(p, vel, ps=0.0):
    tone = p.get("tone", 190) * 2 ** (ps / 12)
    decay = p.get("decay", 0.16)
    n = _n(decay * 5 + 0.05)
    t = _t(n)
    body = (np.sin(2 * np.pi * tone * t) + 0.45 * np.sin(2 * np.pi * tone * 1.62 * t)) * np.exp(-t / (0.05 * p.get("body", 1.0)))
    nz = bp(noise(n), 1200, 9000) * np.exp(-t / decay)
    snap = p.get("snap", 0.7)
    x = body * (1 - snap * 0.5) * 0.9 + nz * (0.4 + snap)
    x = soft(x, p.get("drive", 0.1))
    # softer hits are darker
    if vel < 0.6:
        x = lp(x, 2500 + 9000 * vel)
    return x * vel ** 1.1 * 0.8


def clap(p, vel, ps=0.0):
    decay = p.get("decay", 0.14)
    n = _n(decay * 5 + 0.06)
    t = _t(n)
    env = np.zeros(n, dtype=np.float32)
    spread = p.get("spread", 0.009)
    for i in range(3):
        ti = i * spread * (1 + 0.2 * RNG.standard_normal())
        m = t >= ti
        env[m] += np.exp(-(t[m] - ti) / 0.004)
    m = t >= 3 * spread
    env[m] += 0.8 * np.exp(-(t[m] - 3 * spread) / decay)
    lo = p.get("tone", 1100) * 2 ** (ps / 12)
    x = bp(noise(n), lo, lo * 3.5) * env
    return soft(x, p.get("drive", 0.1)) * vel * 1.2


HAT_RATIOS = np.array([2.0, 3.0, 4.16, 5.43, 6.79, 8.21])


def hat(p, vel, ps=0.0, open_=False):
    decay = p.get("decay", 0.33 if open_ else 0.045)
    n = _n(decay * 5 + 0.02)
    t = _t(n)
    base = 40 * p.get("tune", 1.0) * 2 ** (ps / 12)
    metal = np.zeros(n, dtype=np.float32)
    for r in HAT_RATIOS:
        metal += np.sign(np.sin(2 * np.pi * base * r * t + RNG.random() * 6.28))
    x = metal * 0.15 + noise(n) * p.get("noise", 0.5)
    tone = p.get("tone", 7500)
    x = hp(bp(x, tone * 0.8, 16000), tone, 2)
    env = np.exp(-t / decay)
    x = x * env
    if vel < 0.7:
        x = lp(x, 6000 + 12000 * vel)
    return x * vel * 1.4


def openhat(p, vel, ps=0.0):
    return hat(p, vel, ps, open_=True)


def rim(p, vel, ps=0.0):
    n = _n(0.12)
    t = _t(n)
    f = p.get("tone", 1700) * 2 ** (ps / 12)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.007) + 0.6 * np.sin(2 * np.pi * f * 0.24 * t) * np.exp(-t / 0.02)
    x += bp(noise(n), 2000, 8000) * np.exp(-t / 0.004) * 0.5
    return x.astype(np.float32) * vel * 0.8


def shaker(p, vel, ps=0.0):
    n = _n(0.15)
    t = _t(n)
    env = np.minimum(t / 0.008, 1) * np.exp(-t / p.get("decay", 0.045))
    return bp(noise(n), 4000, 11000) * env * vel * 0.8


def snap(p, vel, ps=0.0):
    n = _n(0.1)
    t = _t(n)
    x = bp(noise(n), 1800, 4500) * np.exp(-t / 0.018) + np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.006) * 0.4
    return x * vel


def tom(p, vel, ps=0.0):
    f0 = p.get("tune", 110) * 2 ** (ps / 12)
    decay = p.get("decay", 0.3)
    n = _n(decay * 4)
    t = _t(n)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.04))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    x += bp(noise(n), 300, 3000) * np.exp(-t / 0.01) * 0.2
    return x.astype(np.float32) * vel


def crash(p, vel, ps=0.0):
    decay = p.get("decay", 1.6)
    n = _n(decay * 4)
    t = _t(n)
    base = 60 * p.get("tune", 1.0)
    metal = np.zeros(n, dtype=np.float32)
    for r in HAT_RATIOS * 1.13:
        metal += np.sign(np.sin(2 * np.pi * base * r * t + RNG.random() * 6))
    x = hp(metal * 0.1 + noise(n) * 0.8, p.get("tone", 4000))
    return x * np.exp(-t / decay) * vel * 0.6


def cowbell(p, vel, ps=0.0):
    n = _n(0.4)
    t = _t(n)
    k = 2 ** (ps / 12)
    x = np.sign(np.sin(2 * np.pi * 540 * k * t)) + np.sign(np.sin(2 * np.pi * 800 * k * t))
    x = bp(x.astype(np.float32), 500, 3000) * np.exp(-t / 0.08)
    return x * vel * 0.5


DRUMS = dict(kick=kick, snare=snare, clap=clap, hat=hat, openhat=openhat, rim=rim,
             shaker=shaker, snap=snap, tom=tom, crash=crash, cowbell=cowbell)

# ---------------------------------------------------------------- tonal


def ep(p, f, vel, dur):
    """FM electric piano (Rhodes-like)."""
    rel = p.get("release", 0.35)
    n = _n(dur + rel)
    t = _t(n)
    bright = p.get("bright", 1.0)
    idx = (0.6 + 2.4 * vel) * bright * np.exp(-t / 0.35) + 0.25 * bright
    mod = np.sin(2 * np.pi * f * t)
    x = np.sin(2 * np.pi * f * t + idx * mod) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
    tine = np.sin(2 * np.pi * f * 13.9 * t) * np.exp(-t / 0.012) * 0.25 * vel * bright
    tau = 1.8 * (261.0 / f) ** 0.35 * p.get("sustain", 1.0)
    env = np.exp(-t / tau)
    hold = _n(dur)
    env[hold:] *= np.exp(-np.arange(n - hold) / _n(rel / 5))
    env *= np.minimum(t / 0.002, 1)
    return ((x + tine) * env * vel ** 1.3 * 0.5).astype(np.float32)


def piano(p, f, vel, dur):
    """Soft additive piano with inharmonic partials; 'felt' darkens it."""
    rel = p.get("release", 0.25)
    n = _n(min(dur + rel, 6.0))
    t = _t(n)
    felt = p.get("felt", 0.5)
    B = 0.0004
    tau0 = 3.2 * (261.0 / f) ** 0.5
    x = np.zeros(n, dtype=np.float32)
    nyq = SR * 0.45
    for k in range(1, 14):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > nyq:
            break
        amp = (1 / k ** (1.1 + felt)) * (vel ** (0.4 * (k - 1) * (0.5 + felt)) if k > 1 else 1)
        tau = tau0 / (1 + 0.35 * k)
        for det in (-0.0006, 0.0006):
            x += (amp * 0.5 * np.sin(2 * np.pi * fk * (1 + det) * t + RNG.random()) * np.exp(-t / tau)).astype(np.float32)
    ham = lp(noise(n), 1500 + 3000 * vel) * np.exp(-t / 0.006) * 0.08 * vel
    x += ham
    hold = _n(dur)
    if hold < n:
        x[hold:] *= np.exp(-np.arange(n - hold) / _n(rel / 4))
    x *= np.minimum(t / 0.002, 1)
    return x * vel ** 1.2 * 0.45


def _saw_stack(f, n, voices, detune_cents, vib=None):
    x = np.zeros(n, dtype=np.float32)
    for i in range(voices):
        c = 0 if voices == 1 else (i / (voices - 1) - 0.5) * 2 * detune_cents
        fr = f * 2 ** (c / 1200)
        if vib is not None:
            fr = fr * vib
        x += polyblep_saw(fr, n)
    return x / np.sqrt(voices)


def pad(p, f, vel, dur):
    a, r = p.get("attack", 0.5), p.get("release", 1.2)
    hold = _n(dur)
    env = adsr(hold, a, 0.5, p.get("sustain_level", 0.85), r)
    n = len(env)
    x = _saw_stack(f, n, p.get("voices", 5), p.get("detune", 14))
    x = lp(x, p.get("cutoff", 2200) * (0.7 + 0.6 * vel), 2)
    return x * env * vel * 0.35


def strings(p, f, vel, dur):
    a, r = p.get("attack", 0.35), p.get("release", 0.8)
    hold = _n(dur)
    env = adsr(hold, a, 0.3, 0.9, r)
    n = len(env)
    t = _t(n)
    vib = 2 ** (p.get("vibrato", 0.12) * np.sin(2 * np.pi * 5.2 * t) * np.minimum(t / 0.6, 1) / 12)
    x = _saw_stack(f, n, 4, p.get("detune", 9), vib)
    x = lp(x, p.get("cutoff", 3500), 2) + bp(noise(n), 2000, 7000) * 0.02
    return x * env * vel * 0.35


VOWELS = {"ah": [(700, 1.0), (1220, 0.5), (2600, 0.25)],
          "oo": [(300, 1.0), (870, 0.35), (2240, 0.1)],
          "ee": [(270, 0.9), (2290, 0.45), (3010, 0.3)],
          "oh": [(450, 1.0), (800, 0.5), (2830, 0.15)]}


def choir(p, f, vel, dur):
    a, r = p.get("attack", 0.45), p.get("release", 1.0)
    hold = _n(dur)
    env = adsr(hold, a, 0.3, 0.9, r)
    n = len(env)
    t = _t(n)
    vib = 2 ** (0.1 * np.sin(2 * np.pi * 5.0 * t + RNG.random() * 6) / 12)
    src = _saw_stack(f, n, 3, 12, vib)
    x = np.zeros(n, dtype=np.float32)
    for fr, g in VOWELS.get(p.get("vowel", "ah"), VOWELS["ah"]):
        x += bp(src, fr * 0.85, fr * 1.15) * g
    return x * env * vel * 0.9


def bell(p, f, vel, dur):
    decay = p.get("decay", 2.2)
    n = _n(min(max(dur, decay * 2.5), 7))
    t = _t(n)
    ratio = p.get("ratio", 3.5)
    idx = (1.5 + 3 * vel) * np.exp(-t / 0.6)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t))
    x += 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / (decay * 0.3))
    env = np.exp(-t / decay) * np.minimum(t / 0.001, 1)
    return (x * env * vel * 0.4).astype(np.float32)


def musicbox(p, f, vel, dur):
    n = _n(2.5)
    t = _t(n)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9) + 0.35 * np.sin(2 * np.pi * f * 4.02 * t) * np.exp(-t / 0.12)
    x += 0.15 * np.sin(2 * np.pi * f * 6.1 * t) * np.exp(-t / 0.05)
    return (x * np.minimum(t / 0.0008, 1) * vel * 0.4).astype(np.float32)


def pluck(p, f, vel, dur):
    """Karplus-Strong plucked string."""
    n = _n(min(dur + 1.5, 4))
    N = max(2, int(SR / f))
    damp = p.get("damp", 0.996)
    exc = np.zeros(n, dtype=np.float32)
    burst = lp(noise(N), 2000 + 8000 * vel * p.get("bright", 0.6))
    exc[:N] = burst
    a = np.zeros(N + 2)
    a[0] = 1
    a[N] = -0.5 * damp
    a[N + 1] = -0.5 * damp
    y = signal.lfilter([1.0], a, exc).astype(np.float32)
    hold = _n(dur)
    if hold < n:
        y[hold:] *= np.exp(-np.arange(n - hold) / _n(0.08))
    return y * vel * 0.6


def organ(p, f, vel, dur):
    hold = _n(dur)
    env = adsr(hold, 0.01, 0.05, 1.0, 0.08)
    n = len(env)
    t = _t(n)
    bars = p.get("drawbars", [1, 0.6, 0.4, 0.25])
    x = sum(b * np.sin(2 * np.pi * f * (k + 1) * t) for k, b in enumerate(bars))
    return (x * env * vel * 0.25).astype(np.float32)


def sine(p, f, vel, dur):
    hold = _n(dur)
    env = adsr(hold, p.get("attack", 0.01), 0.1, 0.9, p.get("release", 0.2))
    n = len(env)
    t = _t(n)
    return (np.sin(2 * np.pi * f * t) * env * vel * 0.5).astype(np.float32)


TONAL = dict(ep=ep, piano=piano, pad=pad, strings=strings, choir=choir, bell=bell,
             musicbox=musicbox, pluck=pluck, organ=organ, sine=sine)

# ------------------------------------------------- monophonic (glide) voices


def mono_voice(kind, p, notes, total_n):
    """notes: list of dict(t0 sample, n samples held, f, vel, glide bool). Renders a
    continuous monophonic line (808 / bass / lead) where each note cuts the previous."""
    out = np.zeros(total_n, dtype=np.float32)
    prev_f = None
    prev_level = 0.0
    prev_phase = None
    glide_s = p.get("glide_ms", 70) / 1000
    for i, nt in enumerate(notes):
        start = nt["t0"]
        nxt = notes[i + 1]["t0"] if i + 1 < len(notes) else None
        if kind == "808":
            decay = p.get("decay", 1.2)
            tail = _n(decay * 3)
        else:
            tail = _n(p.get("release", 0.12))
        next_glides = i + 1 < len(notes) and notes[i + 1].get("glide")
        length = nt["n"] + tail
        if nxt is not None:
            length = min(length, nxt - start + (0 if next_glides else _n(0.004)))
        length = max(length, 16)
        if start >= total_n:
            break
        length = min(length, total_n - start)
        t = _t(length)
        f = np.full(length, nt["f"], dtype=np.float64)
        glide = nt.get("glide") and prev_f is not None
        if glide:
            g = np.clip(t / glide_s, 0, 1)
            f = prev_f * (nt["f"] / prev_f) ** g
        vel = nt["vel"]
        if kind == "808":
            if not glide:
                f = f * (1 + p.get("punch", 0.6) * 1.5 * np.exp(-t / 0.018))
            ph0 = prev_phase if (glide and prev_phase is not None) else 0.0
            ph = ph0 + 2 * np.pi * np.cumsum(f) / SR
            x = np.sin(ph) + p.get("tone", 0.15) * np.sin(2 * ph)
            decay = p.get("decay", 1.2)
            hold = nt["n"]
            lvl0 = max(prev_level, 0.35) if glide else 1.0
            env = lvl0 * np.exp(-t / decay)
            if hold < length:
                env[hold:] *= np.exp(-np.arange(length - hold) / _n(p.get("release", 0.08)))
            if not glide:
                env *= np.minimum(t / 0.0015, 1)
            j = (nxt - start) if nxt is not None else None
            if j is not None and 0 < j <= length:
                prev_level, prev_phase = float(env[j - 1]) if j > 0 else 0.0, float(ph[j - 1]) if j > 0 else 0.0
            else:
                prev_level, prev_phase = 0.0, None
            if nxt is not None and not next_glides:
                fo = min(_n(0.004), length)
                env[-fo:] *= np.linspace(1, 0, fo)
            x = soft(x * env, p.get("drive", 0.25)) * vel
        else:  # bass / lead synth
            vib = 1.0
            if kind == "lead":
                vib = 2 ** (p.get("vibrato", 0.15) * np.sin(2 * np.pi * 5.5 * t) * np.minimum(t / 0.3, 1) / 12)
            ff = f * vib
            saw = polyblep_saw(ff, length)
            if kind == "bass":
                x = saw * 0.5 + np.sin(2 * np.pi * np.cumsum(ff) / SR) * p.get("sub", 0.8)
                cut = p.get("cutoff", 600)
            else:
                sq = np.sign(saw + 0.0001) * 0.3 * p.get("square", 0.3)
                x = saw + sq
                cut = p.get("cutoff", 2500)
            env = adsr(min(nt["n"], length), p.get("attack", 0.005), 0.15, p.get("sustain_level", 0.8), p.get("release", 0.12))[:length]
            if len(env) < length:
                env = np.pad(env, (0, length - len(env)))
            x = lp(x, cut * (0.6 + 0.6 * vel), 2) * env * vel * 0.5
            x = soft(x, p.get("drive", 0.0))
        # click-free join (808 glides are phase-continuous and need no fade)
        if not (kind == "808" and glide):
            fade = min(64, length)
            x[:fade] *= np.linspace(0, 1, fade)
        out[start:start + length] += x.astype(np.float32)
        prev_f = nt["f"]
    return out


MONO = {"808", "bass", "lead"}

# ------------------------------------------------- textures and transition fx


def vinyl(p, n):
    t = _t(n)
    hiss = lp(hp(noise(n), 800), 9000) * 0.02
    crackle = np.zeros(n, dtype=np.float32)
    k = RNG.random(n) < (p.get("density", 6) / SR)
    crackle[k] = RNG.uniform(-1, 1, k.sum()) * RNG.random(k.sum()) ** 3
    crackle = hp(crackle, 1500) * 0.8
    rumble = lp(noise(n), 60) * 0.05 * (1 + 0.5 * np.sin(2 * np.pi * 0.55 * t))
    return (hiss + crackle + rumble).astype(np.float32)


def tape(p, n):
    return lp(hp(noise(n), 2000), 12000) * 0.012


def rain(p, n):
    x = lp(hp(noise(n), 1000), 8000) * 0.03
    k = RNG.random(n) < 40 / SR
    drops = np.zeros(n, dtype=np.float32)
    drops[k] = RNG.random(k.sum())
    drops = bp(drops, 2000, 7000) * 0.6
    return (x + drops).astype(np.float32)


TEXTURES = dict(vinyl=vinyl, tape=tape, rain=rain)


def sweep_noise(n, f0, f1, kind="band", q=0.35):
    """Noise through a filter whose centre moves exponentially from f0 to f1."""
    x = noise(n)
    out = np.zeros(n, dtype=np.float32)
    B = 512
    zi = None
    for s in range(0, n, B):
        fr = f0 * (f1 / f0) ** (s / max(n, 1))
        if kind == "band":
            lo, hi = fr * (1 - q), min(fr * (1 + q), SR * 0.45)
            sos = signal.butter(2, [max(lo, 20), hi], btype="band", fs=SR, output="sos")
        else:
            sos = signal.butter(2, min(fr, SR * 0.45), btype="low", fs=SR, output="sos")
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = signal.sosfilt(sos, x[s:s + B], zi=zi)
        out[s:s + B] = y
    return out


def riser(sec):
    n = _n(sec)
    t = _t(n)
    x = sweep_noise(n, 300, 9000) * (t / sec) ** 2
    return x * 1.2


def reverse_cymbal(sec):
    c = crash({"decay": sec * 0.5}, 1.0)[:_n(sec)]
    return c[::-1].copy() * 1.2


def impact(vel=1.0):
    n = _n(2.5)
    t = _t(n)
    boom = np.sin(2 * np.pi * np.cumsum(40 * (1 + 1.5 * np.exp(-t / 0.05))) / SR) * np.exp(-t / 0.7)
    nz = lp(noise(n), 3000) * np.exp(-t / 0.25) * 0.4
    return soft((boom + nz).astype(np.float32), 0.2) * vel


def downlifter(sec):
    n = _n(sec)
    t = _t(n)
    return sweep_noise(n, 8000, 200) * np.exp(-t / (sec * 0.5)) * 0.8
