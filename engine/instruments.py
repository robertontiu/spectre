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


def darbuka(p, vel, ps=0.0):
    """Goblet drum. stroke: doum (deep centre), tek (bright rim), ka (muted rim), slap."""
    stroke = p.get("stroke", "tek")
    k = 2 ** (ps / 12) * p.get("tune", 1.0)
    if stroke == "doum":
        n = _n(p.get("decay", 0.22) * 7)
        t = _t(n)
        f = 105 * k * (1 + 0.35 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / p.get("decay", 0.22))
        x += 0.35 * np.sin(2 * np.pi * np.cumsum(f * 2.3) / SR) * np.exp(-t / 0.06)
        x += lp(noise(n), 900) * np.exp(-t / 0.015) * 0.3
        return soft(x.astype(np.float32), 0.1) * vel
    n = _n(0.3)
    t = _t(n)
    if stroke == "slap":
        x = bp(noise(n), 700, 5000) * np.exp(-t / 0.03) + np.sin(2 * np.pi * 330 * k * t) * np.exp(-t / 0.05) * 0.5
        return (x / (np.abs(x).max() + 1e-9)).astype(np.float32) * vel * 0.9
    dec = 0.045 if stroke == "tek" else 0.025
    x = np.zeros(n, dtype=np.float32)
    for fr, g in ((620, 1.0), (1030, 0.7), (1640, 0.45), (2350, 0.3)):
        x += (g * np.sin(2 * np.pi * fr * k * t + RNG.random() * 6) * np.exp(-t / dec)).astype(np.float32)
    x += hp(noise(n), 3000) * np.exp(-t / 0.004) * 0.6
    if stroke == "ka":
        x = lp(x, 2500)
    x = x / (np.abs(x).max() + 1e-9)
    return x * vel * (0.7 if stroke == "ka" else 0.9)


def tridksnis(p, vel, ps=0.0):
    """Trīdeksnis: a staff hung with metal plates and rings, struck on the floor or shaken:
    a scatter of bright inharmonic clinks over a short thud."""
    decay = p.get("decay", 0.22)
    n = _n(decay * 4 + 0.05)
    t = _t(n)
    x = np.zeros(n, dtype=np.float32)
    k = 2 ** (ps / 12)
    for i in range(9):
        t0 = abs(RNG.normal(0, 0.012)) + i * 0.003
        m = t >= t0
        fr = RNG.uniform(2500, 9000) * k
        x[m] += (np.sin(2 * np.pi * fr * (t[m] - t0)) * np.exp(-(t[m] - t0) / (decay * RNG.uniform(0.3, 1.0)))).astype(np.float32) * RNG.uniform(0.3, 1)
    x = hp(x, 2000) + hp(noise(n), 6000) * np.exp(-t / 0.03) * 0.5
    thud = lp(noise(n), 300) * np.exp(-t / 0.04) * p.get("thud", 0.6)
    x = x / (np.abs(x).max() + 1e-9) + thud
    return (x * vel * 0.6).astype(np.float32)


DRUMS = dict(tridksnis=tridksnis, darbuka=darbuka, kick=kick, snare=snare, clap=clap, hat=hat, openhat=openhat, rim=rim,
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


def oud(p, f, vel, dur):
    """Fretless lute: two detuned plucked courses, a dark wooden body, quick decay."""
    n = _n(min(dur + 1.2, 3.5))
    damp = p.get("damp", 0.993)
    y = np.zeros(n, dtype=np.float32)
    for det in (-0.0015, 0.0015):
        N = max(2, int(SR / (f * (1 + det))))
        exc = np.zeros(n, dtype=np.float32)
        exc[:N] = lp(noise(N), 2500 + 5000 * vel * p.get("bright", 0.6))
        a = np.zeros(N + 2)
        a[0], a[N], a[N + 1] = 1, -0.5 * damp, -0.5 * damp
        y += signal.lfilter([1.0], a, exc).astype(np.float32)
    body = bp(y, 180, 420) * 0.9 + bp(y, 800, 1500) * 0.5 + y * 0.35
    t = _t(n)
    pick = hp(noise(n), 2500) * np.exp(-t / 0.003) * 0.15 * vel
    x = body + pick
    hold = _n(dur)
    if hold < n:
        x[hold:] *= np.exp(-np.arange(n - hold) / _n(0.06))
    return (x * vel * 0.5).astype(np.float32)


def cimbalom(p, f, vel, dur):
    """Hammered dulcimer (țambal): three detuned strings per course, a hard hammer, long ring.
    Repeated 32nds = the classic tremolo roll. damp shortens the ring (0 = free, 1 = damped)."""
    damp = p.get("damp", 0.2)
    ring = 2.8 * (220.0 / f) ** 0.4 * (1 - 0.85 * damp)
    n = _n(min(max(dur + 0.3, ring * 2.5), 6))
    t = _t(n)
    x = np.zeros(n, dtype=np.float32)
    hard = p.get("hard", 0.6)
    B = 0.00025
    for k in range(1, 12):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > SR * 0.45:
            break
        amp = (1 / k ** (1.4 - 0.6 * hard * vel))
        tau = ring / (1 + 0.45 * (k - 1))
        for det in (-0.0018, 0.0, 0.0021):
            x += (amp / 3 * np.sin(2 * np.pi * fk * (1 + det) * t + RNG.random() * 6) * np.exp(-t / tau)).astype(np.float32)
    x += hp(noise(n), 2500) * np.exp(-t / 0.0025) * 0.25 * hard * vel
    x *= np.minimum(t / 0.0008, 1)
    if damp > 0.6 and _n(dur) < n:
        h = _n(dur)
        x[h:] *= np.exp(-np.arange(n - h) / _n(0.08))
    return (x * vel * 0.45).astype(np.float32)


def lira(p, f, vel, dur):
    """Hurdy-gurdy (lira): a rosined wheel bows the strings, so the tone is steady and nasal,
    with the wheel's slight wobble and an optional rhythmic buzz. Play long notes for drones."""
    rel = p.get("release", 0.15)
    hold = _n(dur)
    env = adsr(hold, p.get("attack", 0.05), 0.1, 0.95, rel)
    n = len(env)
    t = _t(n)
    wob = 1 + 0.003 * np.sin(2 * np.pi * 0.35 * t + RNG.random() * 6)
    raw = polyblep_saw(f * wob, n)
    x = np.zeros(n, dtype=np.float32)
    for fc, g in ((330, 0.8), (700, 0.7), (1500, 1.0), (3000, 0.6)):
        x += bp(raw, fc * 0.8, fc * 1.25) * g
    buzz = p.get("buzz", 0.0)
    if buzz > 0:
        rate = p.get("buzz_rate", 8.0)
        gate = (np.sin(2 * np.pi * rate * t) > 0.3).astype(np.float32)
        x += hp(np.sign(raw) * gate, 1500) * buzz * 0.4
    x += hp(noise(n), 4000) * 0.02
    return soft(x * env, 0.2) * vel * 0.5


def kokle(p, f, vel, dur):
    """Latvian box zither: plucked metal strings that ring long and bright over a light
    wooden box, with a soft shimmer of sympathetic strings. ring 0-1 sets the sustain."""
    ring = p.get("ring", 0.7)
    n = _n(min(max(dur + 0.4, 1.2 + 3.0 * ring), 6))
    N = max(2, int(SR / f))
    exc = np.zeros(n, dtype=np.float32)
    exc[:N] = hp(noise(N), 200) * (0.5 + 0.5 * vel)
    damp = 0.9965 + 0.0032 * ring
    a = np.zeros(N + 2)
    a[0], a[N], a[N + 1] = 1, -0.5 * damp, -0.5 * damp
    y = signal.lfilter([1.0], a, exc).astype(np.float32)
    y = y * 0.7 + bp(y, 250, 600) * 0.5 + bp(y, 1800, 4200) * p.get("bright", 0.6) * 0.6
    t = _t(n)
    shimmer = (np.sin(2 * np.pi * f * 2.003 * t) + 0.6 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t / (0.8 + ring)) * 0.04
    y = y + (shimmer * np.minimum(t / 0.15, 1)).astype(np.float32)
    if p.get("damped") and _n(dur) < n:
        h = _n(dur)
        y[h:] *= np.exp(-np.arange(n - h) / _n(0.05))
    return (y * vel * 0.55).astype(np.float32)


TONAL = dict(kokle=kokle, lira=lira, cimbalom=cimbalom, oud=oud, ep=ep, piano=piano, pad=pad, strings=strings, choir=choir, bell=bell,
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
        elif kind in ("ney", "nai", "fiddle", "trembita", "dudas"):
            # phase-continuous voices so glides and ornaments are seamless
            vrate, vdepth, vdelay = {"ney": (5.0, 0.18, 0.15), "nai": (4.6, 0.12, 0.2), "fiddle": (5.8, 0.22, 0.12),
                                     "trembita": (4.2, 0.05, 0.4), "dudas": (5.0, 0.0, 9.0)}[kind]
            vdepth = p.get("vibrato", vdepth)
            vib = 2 ** (vdepth * np.sin(2 * np.pi * vrate * t) * np.clip((t - vdelay) / 0.35, 0, 1) / 12)
            ff = f * vib
            if kind == "fiddle" and not glide:
                ff = ff * 2 ** (-0.3 * np.exp(-t / 0.035) / 12)  # finger scoop into the note
            ph = (prev_phase if (glide and prev_phase is not None) else 0.0) + 2 * np.pi * np.cumsum(ff) / SR
            j = (nxt - start) if nxt is not None else None
            prev_phase = float(ph[j - 1]) if (j is not None and 0 < j <= length) else None
            if kind == "ney":
                tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
                air = bp(noise(length), 1200, 5000) * p.get("breath", 0.35) * (0.6 + 0.4 * np.abs(np.sin(ph * 0.5)))
                atk = p.get("attack", 0.06)
            elif kind == "nai":
                tone = np.sin(ph) + 0.06 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
                air = bp(noise(length), 2000, 9000) * p.get("breath", 0.25)
                chiff = bp(noise(length), 1500, 6000) * np.exp(-t / 0.02) * (0 if glide else 1.6)
                air = air + chiff
                atk = p.get("attack", 0.025)
            elif kind == "dudas":
                # bagpipe chanter: constant pressure, no dynamics, bright nasal reed
                ph01 = np.mod(ph / (2 * np.pi), 1.0)
                reed = np.where(ph01 < p.get("pulse", 0.32), 1.0, -0.45).astype(np.float32)
                reed = lp(reed, 7000)
                tone = np.zeros(length, dtype=np.float32)
                for fc, g in ((900, 1.0), (1900, 0.8), (3100, 0.45)):
                    tone += bp(reed, fc * 0.75, fc * 1.3) * g
                tone = tone + lp(reed, 600) * 0.5
                if p.get("drone"):
                    dph = 2 * np.pi * p["drone"] * t
                    dr = np.where(np.mod(dph / (2 * np.pi), 1) < 0.4, 1.0, -0.6).astype(np.float32)
                    tone = tone + lp(dr, 1200) * p.get("drone_level", 0.45)
                air = hp(noise(length), 5000) * 0.05
                atk = p.get("attack", 0.015)
            elif kind == "trembita":
                # long wooden horn: lip-buzzed natural harmonics, gets brassier as it swells
                swell = np.ones_like(t) if glide else np.clip(t / p.get("attack", 0.18), 0, 1)
                tone = np.zeros(length, dtype=np.float32)
                bright = p.get("bright", 0.6) * (0.5 + 0.5 * vel)
                for k in range(1, 14):
                    if k * nt["f"] > SR * 0.4:
                        break
                    w = (1 / k ** (1.6 - 0.9 * bright)) * (swell ** (0.3 * k))
                    tone += (w * np.sin(k * ph)).astype(np.float32)
                tone = soft(lp(tone, 900 + 2500 * bright), p.get("blare", 0.3))
                air = bp(noise(length), 300, 2000) * p.get("breath", 0.12)
                atk = p.get("attack", 0.18)
            else:  # fiddle: bowed string through a wooden body
                raw = np.mod(ph / (2 * np.pi), 1.0) * 2 - 1
                body = np.zeros(length, dtype=np.float32)
                for fc, g in ((290, 1.0), (520, 0.8), (1150, 0.6), (2600, 0.7), (3600, 0.35)):
                    body += bp(raw.astype(np.float32), fc * 0.8, fc * 1.25) * g
                tone = body * 0.9
                bowmod = 1 + 0.08 * np.sin(2 * np.pi * 7.3 * t + RNG.random() * 6)
                tone = tone * bowmod
                air = hp(noise(length), 3000) * p.get("bow_noise", 0.12)
                atk = p.get("attack", 0.035)
                tone = soft(tone.astype(np.float32), p.get("grit", 0.15))
            env = adsr(min(nt["n"], length), atk, 0.2, 0.85, p.get("release", 0.12))[:length]
            if len(env) < length:
                env = np.pad(env, (0, length - len(env)))
            if glide:
                env = np.maximum(env, np.minimum(1, 0.85 + 0 * env))
                env[min(nt["n"], length):] *= np.exp(-np.arange(length - min(nt["n"], length)) / _n(0.1))
            x = (tone * 0.5 + air * 0.25) * env * vel
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
        if not (kind in ("808", "ney", "nai", "fiddle", "trembita", "dudas") and glide):
            fade = min(64, length)
            x[:fade] *= np.linspace(0, 1, fade)
        out[start:start + length] += x.astype(np.float32)
        prev_f = nt["f"]
    return out


MONO = {"808", "bass", "lead", "ney", "nai", "fiddle", "trembita", "dudas"}

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


# ================================================================ trance and pop rock (added for sessions 007-008)
# Everything below is additive: existing instruments and their random-number consumption are untouched.

def _biquad(kind, fc, q=0.707, gain_db=0.0):
    """RBJ-cookbook biquad coefficients (b, a): kind = lp, hp, peak."""
    fc = float(np.clip(fc, 10, SR * 0.45))
    w = 2 * np.pi * fc / SR
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * q)
    if kind == "lp":
        b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
        a = np.array([1 + al, -2 * cw, 1 - al])
    elif kind == "hp":
        b = np.array([(1 + cw) / 2, -(1 + cw), (1 + cw) / 2])
        a = np.array([1 + al, -2 * cw, 1 - al])
    else:  # peak
        A = 10 ** (gain_db / 40)
        b = np.array([1 + al * A, -2 * cw, 1 - al * A])
        a = np.array([1 + al / A, -2 * cw, 1 - al / A])
    return b / a[0], a / a[0]


def peq(x, fc, gain_db, q=1.0):
    b, a = _biquad("peak", fc, q, gain_db)
    return signal.lfilter(b, a, x).astype(np.float32)


def env_lp(x, cut, q=0.707, B=256):
    """Low-pass whose cutoff follows the array `cut` (Hz per sample). Block-wise; once the cutoff has
    settled it finishes the rest in one call, so a filter envelope costs little."""
    n = len(x)
    y = np.empty(n, dtype=np.float32)
    zi = np.zeros(2)
    s = 0
    while s < n:
        c = float(cut[s])
        e = n if abs(float(cut[-1]) - c) < 0.02 * c else min(n, s + B)
        b, a = _biquad("lp", c, q)
        y[s:e], zi = signal.lfilter(b, a, x[s:e], zi=zi)
        s = e
    return y


# Szabo (2010), "How to Emulate the Super Saw": the JP-8000's measured, deliberately uneven detune offsets
SZABO = np.array([-0.11002313, -0.06288439, -0.01952356, 0.0, 0.01991221, 0.06216538, 0.10745242])


def _detune_offsets(voices):
    if voices <= 1:
        return np.array([0.0])
    return np.interp(np.linspace(0, 6, voices), np.arange(7), SZABO / 0.11)


def supersaw(p, f, vel, dur):
    """Trance supersaw: `voices` free-running saws with the JP-8000's uneven detune, side voices spread
    across the stereo field. Returns STEREO. With sustain_level 0 and a short decay it is a pluck; with
    env > 0 the filter opens on each note (fdecay)."""
    voices = int(p.get("voices", 7))
    det = p.get("detune", 25.0)
    mix = p.get("mix", 0.7)
    spread = p.get("spread", 0.8)
    hold = _n(dur)
    env = adsr(hold, p.get("attack", 0.004), p.get("decay", 0.4), p.get("sustain_level", 0.9), p.get("release", 0.3))
    n = len(env)
    offs = _detune_offsets(voices)
    order = np.argsort(np.abs(offs))
    L = np.zeros(n, dtype=np.float32)
    R = np.zeros(n, dtype=np.float32)
    for rank, i in enumerate(order):
        o = offs[i]
        x = polyblep_saw(f * 2 ** (o * det / 1200), n)
        if rank == 0:
            L += x
            R += x
            continue
        side = 1 if rank % 2 else -1
        pan = side * spread * (0.35 + 0.65 * abs(o))
        a = (pan + 1) * np.pi / 4
        L += x * mix * np.cos(a) * np.sqrt(2)
        R += x * mix * np.sin(a) * np.sqrt(2)
    norm = 1 / np.sqrt(1 + mix * mix * (voices - 1))
    cut0 = p.get("cutoff", 9000) * (0.75 + 0.35 * vel)
    envhz = p.get("env", 0.0)
    q = 0.707 + p.get("reso", 0.0) * 4
    if envhz > 0:
        t = _t(n)
        cut = cut0 + envhz * vel * np.exp(-t / p.get("fdecay", 0.25))
        L, R = env_lp(L, cut, q), env_lp(R, cut, q)
    else:
        b, a = _biquad("lp", cut0, q)
        L, R = signal.lfilter(b, a, L), signal.lfilter(b, a, R)
    return (np.stack([L, R]) * env * norm * vel * 0.55).astype(np.float32)


def trancebass(p, f, vel, dur):
    """Offbeat / rolling trance bass: two slightly detuned saws through a low-pass with a fast filter
    envelope (the 'pluck' of each note) over a clean sine sub. Short notes; sidechain it to the kick."""
    hold = _n(dur)
    env = adsr(hold, 0.002, p.get("decay", 0.18), p.get("sustain_level", 0.6), p.get("release", 0.03))
    n = len(env)
    t = _t(n)
    saw = _saw_stack(f, n, 2, p.get("detune", 7))
    cut = p.get("cutoff", 260) + p.get("env", 2200) * vel * np.exp(-t / p.get("fdecay", 0.07))
    x = env_lp(saw, cut, 0.707 + p.get("reso", 0.15) * 4)
    sub = np.sin(2 * np.pi * f * t) * p.get("sub", 0.8)
    x = soft((x * 0.8 + sub) * env, p.get("drive", 0.25))
    return (x * vel * 0.55).astype(np.float32)


def clubkick(p, vel, ps=0.0):
    """Four-on-the-floor club kick (909 lineage): a two-stage pitch drop (click sweep + body drop), a short
    hold, then a fast tail that ends cleanly so an offbeat or rolling bass can live between kicks."""
    tune = p.get("tune", 50) * 2 ** (ps / 12)
    length = p.get("length", 0.32)
    n = _n(length)
    t = _t(n)
    punch = p.get("punch", 1.0)
    f = tune * (1 + punch * (5.0 * np.exp(-t / 0.0035) + 1.4 * np.exp(-t / 0.028)))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR)
    hold = p.get("hold", 0.045)
    env = np.where(t < hold, 1.0, np.exp(-(t - hold) / p.get("tail", 0.085)))
    fo = min(_n(0.03), n)
    env[-fo:] *= np.linspace(1, 0, fo)
    click = hp(noise(n), 2500) * np.exp(-t / 0.0012) * p.get("click", 0.5)
    top = bp(noise(n), 3500, 12000) * np.exp(-t / 0.010) * p.get("top", 0.2)
    x = body * env + click * 0.8 + top
    x = soft(x.astype(np.float32), p.get("drive", 0.35))
    return (x * vel ** 1.1).astype(np.float32)


# ---------------------------------------------------------------- acoustic rock kit

def _modes(freqs, amps, decays, n, chunk=24):
    """Sum of decaying sinusoids (modal synthesis) with random phases."""
    t = _t(n)
    out = np.zeros(n, dtype=np.float32)
    ph = RNG.random(len(freqs)) * 2 * np.pi
    for s in range(0, len(freqs), chunk):
        fr = np.asarray(freqs[s:s + chunk], dtype=np.float32)[:, None]
        am = np.asarray(amps[s:s + chunk], dtype=np.float32)[:, None]
        dc = np.asarray(decays[s:s + chunk], dtype=np.float32)[:, None]
        out += (am * np.sin(2 * np.pi * fr * t[None, :] + ph[s:s + chunk, None].astype(np.float32))
                * np.exp(-t[None, :] / dc)).sum(0)
    return out


MEMBRANE = np.array([1.0, 1.594, 2.136, 2.296, 2.653, 2.918, 3.156, 3.501])  # circular membrane mode ratios


def kitkick(p, vel, ps=0.0):
    """Rock kick (miked bass drum): a damped head with a small pitch bend, shell resonance and a hard
    beater click. beater 0-1 = felt to plastic click; decay ~0.15-0.4 (pillow-damped to open)."""
    tune = p.get("tune", 58) * 2 ** (ps / 12)
    decay = p.get("decay", 0.2)
    n = _n(decay * 4 + 0.06)
    t = _t(n)
    f = tune * (1 + 0.55 * vel * np.exp(-t / 0.010) + 0.10 * np.exp(-t / 0.06))
    ph = 2 * np.pi * np.cumsum(f) / SR
    head = (np.sin(ph) * np.exp(-t / decay) + 0.22 * np.sin(ph * 1.594 + 1) * np.exp(-t / (decay * 0.3))
            + 0.10 * np.sin(ph * 2.136 + 2) * np.exp(-t / (decay * 0.18)))
    shell = bp(noise(n), 80, 220) * np.exp(-t / 0.05) * 0.5 * p.get("shell", 1.0)
    beater = p.get("beater", 0.6)
    click = (bp(noise(n), 1800, 7000) * np.exp(-t / 0.0022) * 1.2 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.0015) * 0.5)
    click = click * beater * (0.4 + 0.6 * vel)
    x = head + shell + click
    x = soft(x.astype(np.float32), p.get("drive", 0.15))
    return (x * vel ** 1.15 * 0.95).astype(np.float32)


def kitsnare(p, vel, ps=0.0):
    """Rock snare: a tuned batter head (membrane modes) plus the wires' rattle, which follows the head,
    and the stick. wires 0-1, rim 0-1 (rimshot crack), tune ~170-260 Hz, decay (wire ring)."""
    tone = p.get("tune", 195) * 2 ** (ps / 12)
    dec = p.get("decay", 0.2)
    n = _n(max(0.5, dec * 4))
    t = _t(n)
    fr = tone * MEMBRANE[:6] * (1 + 0.025 * vel * np.exp(-0.0))  # slight sharpening on hard hits
    am = np.array([1.0, 0.65, 0.5, 0.35, 0.28, 0.2])
    dc = np.array([0.09, 0.06, 0.045, 0.04, 0.03, 0.025]) * p.get("body", 1.0)
    head = _modes(fr, am, dc, n)
    head_env = np.exp(-t / 0.05)
    wires = bp(noise(n), 1500, 8500, 2) * (np.minimum(t / 0.002, 1) * np.exp(-t / (dec * (0.6 + 0.4 * vel))))
    wires = wires + bp(noise(n), 400, 1800) * np.exp(-t / 0.04) * 0.25
    rim = p.get("rim", 0.3)
    stick = (hp(noise(n), 2000) * np.exp(-t / 0.0015) * 0.8
             + rim * (np.sin(2 * np.pi * 920 * t) + 0.7 * np.sin(2 * np.pi * 1630 * t)) * np.exp(-t / 0.018) * 0.6)
    x = head * (0.8 - 0.2 * rim) + wires * p.get("wires", 0.75) * (0.7 + 0.5 * vel) + stick * (0.5 + 0.5 * vel)
    x = x * (1 + 0.3 * head_env)
    x = soft(x.astype(np.float32), p.get("drive", 0.12))
    if vel < 0.7:  # soft hits (ghosts) are darker
        x = lp(x, 3000 + 12000 * vel)
    return (x * vel ** 1.1 * 0.55).astype(np.float32)


def kittom(p, vel, ps=0.0):
    """Rock tom: membrane modes that drop slightly in pitch as the head relaxes, plus the stick.
    tune ~ 80 (floor) .. 200 Hz (rack); decay 0.3-0.8."""
    f0 = p.get("tune", 110) * 2 ** (ps / 12)
    decay = p.get("decay", 0.5)
    n = _n(decay * 4)
    t = _t(n)
    bend = 1 + 0.12 * vel * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f0 * bend) / SR
    x = np.zeros(n, dtype=np.float32)
    for r, g, d in zip(MEMBRANE[:5], (1.0, 0.45, 0.3, 0.22, 0.15), (1.0, 0.5, 0.35, 0.3, 0.25)):
        x += (g * np.sin(ph * r + RNG.random() * 6) * np.exp(-t / (decay * d))).astype(np.float32)
    x += bp(noise(n), 600, 6000) * np.exp(-t / 0.004) * 0.35 * (0.5 + vel)
    x += bp(noise(n), 150, 900) * np.exp(-t / 0.03) * 0.15
    return (soft(x, 0.1) * vel ** 1.1 * 0.7).astype(np.float32)


def _cymbal_partials(n_part, lo, hi, tilt):
    fr = np.exp(RNG.uniform(np.log(lo), np.log(hi), n_part))
    am = (fr / lo) ** (-tilt) * RNG.uniform(0.4, 1.0, n_part)
    return fr, am


def kithat(p, vel, ps=0.0):
    """Hi-hat (two plates): open 0 = closed, ~0.4 = half-open sizzle, 1 = open. pedal true = the foot 'chick'.
    Use one track per articulation; give the open track "choke_by": "<closed track>"."""
    k = 2 ** (ps / 12) * p.get("tune", 1.0)
    if p.get("pedal"):
        n = _n(0.12)
        t = _t(n)
        x = bp(noise(n), 700, 5000) * np.exp(-t / 0.012) + bp(noise(n), 5000, 12000) * np.exp(-t / 0.02) * 0.4
        return (x * vel * 0.8).astype(np.float32)
    op = float(p.get("open", 0.0))
    decay = p.get("decay", 0.03 + 1.1 * op ** 1.6)
    n = _n(min(decay * 4 + 0.03, 4.0))
    t = _t(n)
    fr, am = _cymbal_partials(48, 2800 * k, 15500, 0.35)
    metal = _modes(fr, am, RNG.uniform(0.5, 1.0, 48) * decay, n) * 0.06
    nz = hp(noise(n), 5500) * np.exp(-t / decay)
    if op > 0.2:  # loose plates rattle against each other
        nz = nz * (1 + 0.35 * op * np.sin(2 * np.pi * 23 * t + RNG.random() * 6))
    tip = bp(noise(n), 3000, 9000) * np.exp(-t / 0.0025) * 0.8
    x = (metal + nz * 0.6) * (1 - 0.35 * op) + tip * (0.6 + 0.4 * vel)
    x = hp(x, p.get("tone", 3500))
    if vel < 0.7:
        x = lp(x, 7000 + 12000 * vel)
    return (x * vel * 0.9).astype(np.float32)


_WASH = {}


def _wash(key, n, lo, hi, decay, tilt, n_part, variants=4):
    """Dense cymbal wash: band-split noise where each band has its own decay (highs die first) plus
    inharmonic partials for the metallic pitch. Cached in a few variants per sound (it is costly and the
    velocity layers only change level and brightness)."""
    lst = _WASH.setdefault(key, [])
    if len(lst) >= variants:
        i = _WASH.setdefault(("_i",) + key, [0])
        i[0] += 1
        return lst[i[0] % variants]
    t = _t(n)
    nz = noise(n)
    edges = np.geomspace(lo, min(hi, SR * 0.44), 19)
    x = np.zeros(n, dtype=np.float32)
    for e0, e1 in zip(edges[:-1], edges[1:]):
        fc = np.sqrt(e0 * e1)
        band = bp(nz, e0, e1, 2)
        tau = decay * (fc / 1000) ** -0.35
        x += band * ((fc / 1000) ** (-tilt) * (0.55 * np.exp(-t / (0.12 * tau)) + 0.45 * np.exp(-t / tau))).astype(np.float32)
    fr, am = _cymbal_partials(n_part, lo, hi, tilt)
    dc = decay * RNG.uniform(0.3, 1.0, n_part) * (fr / 1000) ** -0.3
    x = x * 0.5 + _modes(fr, am, dc, n) * (0.6 / np.sqrt(n_part)) * (0.4 + 0.6 * np.exp(-t / (0.3 * decay)))
    lst.append(x)
    return x


def kitride(p, vel, ps=0.0):
    """Ride cymbal: a defined stick 'ping' over a long wash. bell 0-1 plays on the bell (louder,
    pitched, cuts through a loud chorus); decay ~2-5 s."""
    k = 2 ** (ps / 12) * p.get("tune", 1.0)
    decay = p.get("decay", 3.0)
    n = _n(min(decay * 1.6, 6))
    t = _t(n)
    wash = _wash(("ride", decay, k), n, 350 * k, 15000, decay, 0.35, 120) * 0.35
    ping = (bp(noise(n), 3000, 9000) * np.exp(-t / 0.04) * 0.6 + bp(noise(n), 7000, 15000) * np.exp(-t / 0.007) * 0.6
            + _modes(5200 * k * np.array([1.0, 1.37, 1.73]), [0.5, 0.35, 0.25], [0.25, 0.2, 0.15], n) * 0.4)
    bell = p.get("bell", 0.0)
    if bell > 0:
        bf = 680 * k * np.array([1.0, 1.51, 2.09, 2.76, 3.55])
        ping = ping + _modes(bf, [1, 0.8, 0.6, 0.4, 0.3], [1.2, 0.9, 0.7, 0.5, 0.4], n) * 0.35 * bell
    x = hp(wash * (0.5 + 0.5 * vel) + ping * (0.5 + 0.5 * vel), 300)
    if vel < 0.7:
        x = lp(x, 6000 + 14000 * vel)
    return (x * vel * 0.7).astype(np.float32)


def kitcrash(p, vel, ps=0.0):
    """Crash cymbal: a broadband bloom with body from ~300 Hz up (the old `crash` is a thin hiss above
    4 kHz). decay ~1.5-3.5 s; tone tilts it darker (<1) or brighter (>1)."""
    k = 2 ** (ps / 12) * p.get("tune", 1.0)
    decay = p.get("decay", 2.4)
    tone = p.get("tone", 1.0)
    n = _n(min(decay * 1.8, 6))
    t = _t(n)
    wash = _wash(("crash", decay, k, tone), n, 300 * k, 16000, decay, 0.25 / tone, 160)
    bloom = np.minimum(t / 0.008, 1)
    hit = bp(noise(n), 1500, 12000) * np.exp(-t / 0.012) * 0.7
    x = wash * bloom + hit * vel
    x = hp(x, 250)
    if vel < 0.7:
        x = lp(x, 6000 + 14000 * vel)
    return (x * vel * 0.65).astype(np.float32)


# ---------------------------------------------------------------- guitars and bass (string models)

def ks_string(f, n, t60, exc, s=0.5):
    """Karplus-Strong string with a fractional (all-pass tuned) delay, so chords stay in tune at any pitch.
    t60 = seconds to decay 60 dB (independent of pitch); s = loop low-pass (0.5 dark .. 0.15 bright)."""
    P = SR / f
    N = max(2, int(P - s - 0.1))
    d = P - s - N
    C = (1 - d) / (1 + d)
    g = 10 ** (-3 / (max(t60, 0.01) * f))
    a = np.zeros(N + 3)
    a[0], a[1] = 1.0, C
    a[N] -= g * (1 - s) * C
    a[N + 1] -= g * ((1 - s) + s * C)
    a[N + 2] -= g * s
    return signal.lfilter([1.0, C], a, exc[:n] if len(exc) >= n else np.pad(exc, (0, n - len(exc)))).astype(np.float32)


def _pick(f, n, vel, bright, pos):
    """Pick excitation: a short noise burst, brighter for harder picking, comb-filtered by the pick position."""
    P = SR / f
    L = max(4, int(P))
    e = noise(L) * np.hanning(L).astype(np.float32)
    e = lp(e, 1200 + 9000 * bright * (0.4 + 0.6 * vel))
    D = max(1, int(P * pos))
    e2 = e.copy()
    e2[D:] -= e[:-D]
    out = np.zeros(n, dtype=np.float32)
    out[:min(n, L)] = e2[:min(n, L)]
    return out


def _guitar_note(p, f, vel, dur, clean):
    mute = float(p.get("mute", 0.0))
    rel = 0.06 if mute < 0.5 else 0.03
    n = _n(dur + rel)
    t60 = p.get("sustain", 4.0 if not clean else 2.5) * (220 / f) ** 0.3
    t60 = t60 * (1 - mute) + 0.14 * mute
    s = 0.5 - 0.3 * p.get("bright", 0.6) * (1 - mute)
    exc = _pick(f, n, vel, p.get("bright", 0.6) * (1 - 0.7 * mute), p.get("pick_pos", 0.12))
    y = ks_string(f, n, t60, exc, s)
    pu = p.get("pickup", 0.1 if not clean else 0.22)  # bridge pickup ~0.1 (bite) .. neck ~0.25 (round)
    D = max(1, int(SR / f * pu))
    y = y - np.concatenate([np.zeros(D, dtype=np.float32), y[:-D]]) * 0.5
    if mute > 0:
        y = lp(y, 5000 - 3800 * mute)
    h = _n(dur)
    if h < n:
        y[h:] *= np.exp(-np.arange(n - h) / _n(rel / 4))
    return (y * vel * 0.6).astype(np.float32)


def eguitar(p, f, vel, dur):
    """Electric guitar string (the amp is applied to the whole track afterwards, so chords distort
    together like a real amp). Use chord voicings "power" or "guitar"."""
    return _guitar_note(p, f, vel, dur, clean=False)


def cleanguitar(p, f, vel, dur):
    """Clean electric guitar string (neck pickup); the track gets a clean amp and stereo chorus."""
    return _guitar_note(p, f, vel, dur, clean=True)


def _cab(x, dark=0.5):
    """4x12-style cabinet: no lows below ~80 Hz, a low resonance, a 400 Hz dip, presence, steep top roll-off."""
    x = hp(x, 80, 2)
    x = peq(x, 110, 4.0, 1.0)
    x = peq(x, 220, 2.0, 0.8)
    x = peq(x, 450, -3.0, 1.2)
    x = peq(x, 250, 2.5, 0.7)
    x = peq(x, 2400, 2.5, 1.2)
    x = lp(lp(x, 5200 - 2200 * dark, 2), 6500 - 2000 * dark, 2)
    return x


def guitar_amp(p, x):
    """Amp for a summed `eguitar` track: tight pre-EQ, two clipping stages, tone stack, cabinet."""
    drive = float(p.get("drive", 0.7))
    x = hp(x, 110, 2)
    x = x + bp(x, 500, 1500) * (0.25 * drive)  # overdrive mid hump before the clipping
    g = 10 ** ((6 + 40 * drive) / 20)
    y = np.tanh(g * x + 0.08) - np.tanh(0.08)
    y = lp(y, 7000)
    y = np.tanh(y * (1 + 3 * drive)) / np.tanh(1 + 3 * drive)
    y = peq(y, 750, -3 * p.get("scoop", 0.3), 0.8)
    y = _cab(y, p.get("dark", 0.4))
    return (y * 0.5).astype(np.float32)


def chorus_stereo(x, rate=0.8, depth_ms=2.2, base_ms=7.0, mix=0.5):
    n = len(x)
    t = np.arange(n) / SR
    idx = np.arange(n, dtype=np.float64)
    outs = []
    for phs in (0.0, np.pi):
        d = (base_ms + depth_ms * np.sin(2 * np.pi * rate * t + phs)) / 1000 * SR
        wet = np.interp(idx - d, idx, x, left=0.0)
        outs.append(x * (1 - mix * 0.5) + wet * mix)
    return np.stack(outs).astype(np.float32)


def clean_amp(p, x):
    """Clean amp for a summed `cleanguitar` track: slight tube compression, a bright cab, stereo chorus."""
    x = hp(x, 90, 2)
    y = np.tanh(x * (1.5 + 4 * p.get("drive", 0.1))) / np.tanh(1.5 + 4 * p.get("drive", 0.1))
    y = peq(y, 3000, 2.0, 0.9)
    y = peq(y, 220, 3.0, 0.7)
    y = lp(y, 9000, 2)
    ch = p.get("chorus", 0.5)
    if ch > 0:
        return chorus_stereo(y, p.get("chorus_rate", 0.8), 2.5 * ch + 0.5, 7.0, 0.3 + 0.4 * ch) * 0.6
    return (y * 0.6).astype(np.float32)


def ebass(p, f, vel, dur):
    """Electric bass guitar: a long-sustaining string, picked (pick 1) or fingered (pick 0), with a little
    fundamental reinforcement like a DI. mute 0-1 = palm-muted. Play roots in 8ths that follow the kick."""
    mute = float(p.get("mute", 0.0))
    rel = 0.04
    n = _n(dur + rel)
    pick = p.get("pick", 0.7)
    t60 = p.get("sustain", 2.5) * (1 - 0.85 * mute)
    exc = _pick(f, n, vel, 0.25 + 0.6 * pick, 0.18 - 0.08 * pick)
    y = ks_string(f, n, t60, exc, 0.5 - 0.2 * pick)
    t = _t(n)
    y = y / (np.abs(y[:_n(0.05)]).max() + 1e-6) * 0.6
    y += np.sin(2 * np.pi * f * t) * np.exp(-t / (t60 * 0.5)) * 0.15 * np.minimum(t / 0.004, 1)
    if mute > 0:
        y = lp(y, 2500 - 1700 * mute)
    h = _n(dur)
    if h < n:
        y[h:] *= np.exp(-np.arange(n - h) / _n(rel / 4))
    return (y * vel * 0.75).astype(np.float32)


def bass_amp(p, x):
    y = hp(x, 35, 2)
    dr = p.get("drive", 0.2)
    y = np.tanh(y * (1 + 4 * dr)) / np.tanh(1 + 4 * dr)
    y = peq(y, 180, 4.0, 0.7)  # the growl of the 2nd/3rd harmonics that carries a bass on small speakers
    y = lp(y, p.get("tone", 3500), 2)
    return y.astype(np.float32)


# ---------------------------------------------------------------- vocal-like lead

FORMANTS = {  # (F1..F5 Hz, bandwidths Hz); Csound formant tables (after Peterson & Barney era measurements)
    "soprano": {"ah": ([800, 1150, 2900, 3900, 4950], [80, 90, 120, 130, 140]),
                "eh": ([350, 2000, 2800, 3600, 4950], [60, 100, 120, 150, 200]),
                "ee": ([270, 2140, 2950, 3900, 4950], [60, 90, 100, 120, 120]),
                "oh": ([450, 800, 2830, 3800, 4950], [40, 80, 100, 120, 120]),
                "oo": ([325, 700, 2700, 3800, 4950], [50, 60, 170, 180, 200])},
    "alto": {"ah": ([800, 1150, 2800, 3500, 4950], [80, 90, 120, 130, 140]),
             "eh": ([400, 1600, 2700, 3300, 4950], [60, 80, 120, 150, 200]),
             "ee": ([350, 1700, 2700, 3700, 4950], [50, 100, 120, 150, 200]),
             "oh": ([450, 800, 2830, 3500, 4950], [70, 80, 100, 130, 135]),
             "oo": ([325, 700, 2530, 3500, 4950], [50, 60, 170, 180, 200])},
    "tenor": {"ah": ([650, 1080, 2650, 2900, 3250], [80, 90, 120, 130, 140]),
              "eh": ([400, 1700, 2600, 3200, 3580], [70, 80, 100, 120, 120]),
              "ee": ([290, 1870, 2800, 3250, 3540], [40, 90, 100, 120, 120]),
              "oh": ([400, 800, 2600, 2800, 3000], [40, 80, 100, 120, 120]),
              "oo": ([350, 600, 2700, 2900, 3300], [40, 60, 100, 120, 120])},
}


def _vowel(voice, name):
    tab = FORMANTS.get(voice, FORMANTS["alto"])
    F, B = tab.get(name, tab["ah"])
    return np.array(F, dtype=np.float64), np.array(B, dtype=np.float64)


def _tract(freqs, F, B, widen=1.4):
    """Cascade vocal-tract magnitude at the given frequencies (array) for formants F, bandwidths B."""
    h = np.ones_like(freqs)
    for Fi, Bi in zip(F, B * widen):
        r = freqs / Fi
        h = h / np.sqrt((1 - r * r) ** 2 + (freqs * Bi / (Fi * Fi)) ** 2)
    return h


def vox_line(p, notes, total_n):
    """Wordless solo voice ('ooh'/'ah'): additive glottal source shaped by a 5-formant vocal tract that stays
    put while the pitch moves, so glides and vibrato sound sung. Monophonic, legato with `~` glides."""
    out = np.zeros(total_n, dtype=np.float32)
    voice = p.get("voice", "alto")
    Fa, Ba = _vowel(voice, p.get("vowel", "ah"))
    Fb, Bb = _vowel(voice, p.get("vowel2", p.get("vowel", "ah")))
    morph = p.get("morph", 0.6)
    vdepth, vrate, vdelay = p.get("vibrato", 0.3), p.get("vib_rate", 5.3), p.get("vib_delay", 0.22)
    glide_s = p.get("glide_ms", 90) / 1000
    breath = p.get("breath", 0.25)
    bright = p.get("bright", 0.6)
    ring = p.get("ring", 0.5)
    prev_f, prev_phase = None, None
    D = 64
    for i, nt in enumerate(notes):
        start = nt["t0"]
        if start >= total_n:
            break
        nxt = notes[i + 1]["t0"] if i + 1 < len(notes) else None
        next_glides = nxt is not None and notes[i + 1].get("glide")
        rel = p.get("release", 0.14)
        length = nt["n"] + _n(rel)
        if nxt is not None:
            length = min(length, nxt - start + (0 if next_glides else _n(0.006)))
        length = int(min(max(length, 32), total_n - start))
        t = _t(length).astype(np.float64)
        glide = bool(nt.get("glide")) and prev_f is not None
        f = np.full(length, nt["f"])
        if glide:
            f = prev_f * (nt["f"] / prev_f) ** np.clip(t / glide_s, 0, 1)
        else:  # singers scoop up into a fresh note
            f = f * 2 ** (-p.get("scoop", 0.5) * np.exp(-t / 0.045) / 12)
        vib = vdepth * np.sin(2 * np.pi * vrate * t + RNG.random() * 6) * np.clip((t - vdelay) / 0.35, 0, 1)
        drift = np.interp(t, np.linspace(0, t[-1] + 1e-3, 6), RNG.normal(0, 0.06, 6))
        f = f * 2 ** ((vib + drift) / 12)
        ph = (prev_phase if (glide and prev_phase is not None) else 0.0) + 2 * np.pi * np.cumsum(f) / SR
        K = int(min(9500, SR * 0.42) / max(f.min(), 40))
        K = max(1, min(K, 60))
        td = t[::D]
        w = np.clip(td / max(morph, 1e-3), 0, 1)[:, None] if p.get("vowel2") else np.zeros((len(td), 1))
        Fd = Fa[None, :] * (1 - w) + Fb[None, :] * w
        Bd = Ba[None, :] * (1 - w) + Bb[None, :] * w
        fd = f[::D]
        tilt = 1.15 - 0.6 * bright * nt["vel"]
        x = np.zeros(length)
        amps = np.zeros((K, len(td)))
        for k in range(1, K + 1):
            fk = k * fd
            h = np.ones(len(td))
            for j in range(5):
                r = fk / Fd[:, j]
                h = h / np.sqrt((1 - r * r) ** 2 + (fk * Bd[:, j] * 1.4 / (Fd[:, j] ** 2)) ** 2)
            sf_ = 1 + ring * 4 * np.exp(-((fk - 2900) / 700) ** 2)  # singer's formant (the ring that carries)
            amps[k - 1] = h * sf_ * k ** -tilt * (fk < 9500)
        norm = np.sqrt((amps[:, :8] ** 2).sum(0)).mean() + 1e-9 if amps.shape[1] else 1.0
        idx = np.arange(length) / D
        for k in range(1, K + 1):
            a = np.interp(idx, np.arange(len(td)), amps[k - 1])
            x += a * np.sin(k * ph)
        x = x / norm
        air = noise(length)
        F0 = Fa
        air = (bp(air, F0[0] * 0.8, F0[0] * 1.25) + bp(air, F0[1] * 0.85, F0[1] * 1.2) * 0.7
               + bp(air, 2500, 7000) * 0.5) * breath * 0.5
        env = adsr(min(nt["n"], length), p.get("attack", 0.06), 0.25, p.get("sustain_level", 0.85), rel)[:length]
        if len(env) < length:
            env = np.pad(env, (0, length - len(env)))
        if glide:
            env = np.maximum(env, 0.85 * (np.arange(length) < nt["n"]))
            h0 = min(nt["n"], length)
            env[h0:] = 0.85 * np.exp(-np.arange(length - h0) / _n(rel / 5))
        shimmer = 1 + 0.04 * np.sin(2 * np.pi * 3.1 * t + RNG.random() * 6)
        y = (x * 0.5 * shimmer + air) * env * nt["vel"]
        if not glide:
            fade = min(64, length)
            y[:fade] *= np.linspace(0, 1, fade)
        if nxt is not None and not next_glides:
            fo = min(_n(0.006), length)
            y[-fo:] *= np.linspace(1, 0, fo)
        out[start:start + length] += y.astype(np.float32)
        j = (nxt - start) if nxt is not None else None
        prev_phase = float(ph[j - 1]) if (j is not None and 0 < j <= length) else None
        prev_f = nt["f"]
    return out


_mono_voice_base = mono_voice


def mono_voice(kind, p, notes, total_n):  # noqa: F811  (extends the original with "vox")
    if kind == "vox":
        return vox_line(p, notes, total_n)
    return _mono_voice_base(kind, p, notes, total_n)


def pitch_riser(sec):
    """Build-up riser: detuned saws sweeping up three octaves through an opening filter, plus noise."""
    n = _n(sec)
    t = _t(n)
    u = t / sec
    f = 110 * 2 ** (3 * u ** 1.6)
    x = np.zeros(n, dtype=np.float32)
    for c in (-18, -6, 6, 18):
        x += polyblep_saw(f * 2 ** (c / 1200), n)
    x = env_lp(hp(x, 150), 400 + 9000 * u ** 2)
    x = x * 0.25 + sweep_noise(n, 500, 10000) * 0.6
    return (x * u ** 2).astype(np.float32)


DRUMS.update(clubkick=clubkick, kitkick=kitkick, kitsnare=kitsnare, kittom=kittom, kithat=kithat, kitride=kitride,
             kitcrash=kitcrash)
TONAL.update(supersaw=supersaw, trancebass=trancebass, eguitar=eguitar, cleanguitar=cleanguitar, ebass=ebass)
MONO.add("vox")
# whole-track processors applied to the summed track before gain/pan (an amp that sees the whole chord)
POST = {"eguitar": guitar_amp, "cleanguitar": clean_amp, "ebass": bass_amp}
# drums that cycle through `rr` slightly different hits (round robin), so repeated notes aren't identical
ROUND_ROBIN = {"kitkick", "kitsnare", "kittom", "kithat", "kitride", "kitcrash"}




# ---------------------------------------------------------------- handclap (a truer clap)
# Additive block: the old `clap` above is untouched and its random-number use unchanged; handclap draws from its
# own generator (seeded per hit from its params, velocity, pitch and variant number), so adding it changes
# nothing in projects that don't use it and a track's claps don't depend on any other track.
#
# Model (sources in docs/MANUAL.md and docs/TRANCE.md):
# - one hand clap is a ~5 ms burst: an air pulse squeezed out between the hands, coloured by the cavity between
#   them, a second-order resonance whose centre and bandwidth depend on how the hands meet (Repp 1987; Peltola,
#   Erkut, Cook & Valimaki 2007, Table 1: 0.5-1.6 kHz, bandwidths 90-375 Hz, i.e. Q 4-8, so it never rings),
#   plus the broadband slap of skin on skin;
# - a "clap" in a record is several hands slightly out of time (the TR-808 retriggers its noise envelope several
#   times about 10 ms apart, then a longer envelope is its "reverberation"; TR-808 service notes, CP/MA circuit);
# - each hand gets its own noise and its own resonance, so the bursts never sum into a comb filter (a delayed
#   copy of the same burst would: the metallic sound); the room is decorrelated noise with a fade-in, no
#   delay lines, highs dying first.
_HC_CALLS = {}
# Peltola et al. 2007, Table 1: (centre Hz, sd, -3 dB bandwidth Hz, sd, gain) per hand configuration.
# P = palms parallel (P1 flat .. P3 fingers to palm), A = angled; A1+ cupped (domed, lowest), A1- flatter.
HC_MODES = {"P1": (1364, 333, 188, 54, 27.2), "P2": (774, 448, 139, 7, 13.8), "P3": (1562, 257, 375, 94, 19.5),
            "A1": (775, 39, 137, 15, 22.2), "A2": (1355, 57, 222, 53, 24.0), "A3": (1452, 12, 183, 40, 13.8),
            "A1+": (500, 178, 91, 27, 33.8), "A1-": (984, 396, 137, 36, 11.3)}
HC_HANDS = {"flat": ("P1", "P3", "A2", "A3"), "cupped": ("A1+", "A1", "P2"),
            "mixed": ("P1", "P2", "P3", "A1", "A2", "A3", "A1+", "A1-")}


_HC_WARNED = set()


def _hc_warn(msg):
    if msg not in _HC_WARNED:
        _HC_WARNED.add(msg)
        import sys
        print("warning: " + msg, file=sys.stderr)


def _tame_peaks(x, red_db, look=0.0015):
    """Lookahead peak limiter for one hit: lowers the needle peaks of the bursts by up to red_db with a gain that
    moves over ~1.5 ms (a clipper on a clap, minus the distortion)."""
    if red_db <= 0:
        return x
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    k = max(3, int(look * SR))
    env = maximum_filter1d(np.abs(x), size=2 * k + 1)  # centred window = lookahead
    thr = np.abs(x).max() * 10 ** (-red_db / 20)
    g = np.minimum(1.0, thr / (env + 1e-12))
    g = uniform_filter1d(maximum_filter1d(1 - g, size=k), size=k)  # smooth the reduction, never shorten it
    return (x * (1 - g)).astype(np.float32)


def _bp_res(x, fc, bw):
    """RBJ band-pass (0 dB peak) at fc with -3 dB bandwidth bw Hz: the hand cavity's resonance."""
    fc = float(np.clip(fc, 250, 4000))
    q = fc / max(bw, 40.0)
    w = 2 * np.pi * fc / SR
    al = np.sin(w) / (2 * q)
    b = np.array([al, 0, -al]) / (1 + al)
    a = np.array([1 + al, -2 * np.cos(w), 1 - al]) / (1 + al)
    return signal.lfilter(b, a, x).astype(np.float32)


def handclap(p, vel, ps=0.0):
    """A truer hand clap: `clappers` hands (default 4) hitting `spread_ms` (default 9) apart, each a ~5 ms noise
    burst through its own hand-cavity resonance (`hands`: mixed / flat / cupped; `tone` scales the resonances),
    plus the skin slap (`bright` 0-1), a soft low body (`body` 0-1) and a short room (`room` 0-1, `decay` s =
    the tail's time constant, highs fade first). Every call draws new hands, timings and noise; it is a
    round-robin drum (`rr`, default 4), so repeated hits differ;
    `seed` picks another set of hands. limit_db (6) tames the bursts' needle peaks with a lookahead limiter.
    `model` 2 (default) is fitted to recorded claps (see _handclap2); `model` 1 is the first version (session 007 v029)."""
    import json, zlib
    model = int(p.get("model", 2))
    # `model` is left out of the key so {"model": 1} reproduces the hits rendered before model 2 existed
    pkey = json.dumps({k: v for k, v in p.items() if k != "model"}, sort_keys=True, default=str)
    ck = (pkey, round(vel * 1000), round(ps * 100))
    c = _HC_CALLS[ck] = _HC_CALLS.get(ck, -1) + 1  # the c-th variant of this hit: new hands every call
    rng = np.random.default_rng([int(p.get("seed", 0)) & 0xFFFFFFFF, zlib.crc32(pkey.encode()), ck[1], ck[2] + 10000, c])
    if model != 1:
        return _handclap2(p, vel, ps, rng)
    k = 2 ** (ps / 12) * p.get("tone", 1.0)
    clappers = max(1, int(p.get("clappers", 4)))
    spread_ms = float(p.get("spread_ms", 9.0))
    if not 2.0 <= spread_ms <= 30.0:  # hands of one clap land a few ms apart; more is separate hits
        _hc_warn(f"handclap: spread_ms={spread_ms:g} is outside 2-30 ms (the gap between hands); clamped")
        spread_ms = float(np.clip(spread_ms, 2.0, 30.0))
    spread = spread_ms / 1000
    hands = p.get("hands", "mixed")
    modes = HC_HANDS.get(hands, HC_HANDS["mixed"]) if isinstance(hands, str) else tuple(hands)
    bright = p.get("bright", 0.35)
    body = p.get("body", 0.15)
    room = p.get("room", 0.35)
    decay = float(p.get("decay", 0.05))
    if not 0.01 <= decay <= 0.4:
        _hc_warn(f"handclap: decay={decay:g} s is outside 0.01-0.4 s (the room tail's time constant); clamped")
        decay = float(np.clip(decay, 0.01, 0.4))
    # onsets: the first hand at 0, the others spread_ms apart on average (0.5x-1.5x), each with its own level
    gaps = spread * rng.uniform(0.5, 1.5, clappers - 1)
    onsets = np.concatenate([[0.0], np.cumsum(gaps)])
    last = onsets[-1]
    n = _n(last + 0.03 + decay * 7)
    t = _t(n)
    hands_x = np.zeros(n, dtype=np.float32)
    nb = _n(0.012)  # one hand: 12 ms is enough for burst + resonance to die 60 dB
    tb = _t(nb)
    for i, t0 in enumerate(onsets):
        f, df, bw, dbw, g = HC_MODES[modes[rng.integers(len(modes))]]
        fc = max(350.0, rng.normal(f, df * 0.5)) * k
        bwi = max(60.0, rng.normal(bw, dbw * 0.5)) * k
        tau = rng.uniform(0.0008, 0.0015)
        env = np.minimum(tb / 0.0003, 1) * np.exp(-tb / tau)
        e = rng.standard_normal(nb).astype(np.float32) * env.astype(np.float32)
        res = _bp_res(e, fc, bwi) * np.sqrt(g / 24.0) * 2.2
        slap = lp(hp(e, 1500), 6500) * bright * (0.5 + 0.5 * vel)
        lvl = rng.uniform(0.6, 1.0) if i else rng.uniform(0.8, 1.0)
        a = int(t0 * SR)
        m = min(nb, n - a)
        hands_x[a:a + m] += ((res + slap) * lvl)[:m]
    # loudness-normalise the hands (variants stay equally loud; the peak varies a little, as real hits do)
    act = hands_x[:int((last + 0.006) * SR) + 1]
    hands_x /= np.sqrt(np.mean(act ** 2)) + 1e-9
    x = hands_x * 0.45
    if body > 0:  # the soft flesh thump under the first hands
        th = lp(rng.standard_normal(n).astype(np.float32), 380) * np.exp(-t / 0.007) * np.minimum(t / 0.001, 1)
        x += th * body * 0.35
    if room > 0:  # short room: decorrelated noise, fades in over the hands, highs die first
        nz = rng.standard_normal(n).astype(np.float32)
        lo_b, hi_b = bp(nz, 500, 2500), bp(nz, 2500, 7000)
        tr = np.clip((t - 0.003) / (last + 0.008), 0, 1) ** 1.5
        dt = np.maximum(t - 0.003, 0)
        tail = lo_b * np.exp(-dt / decay) + hi_b * 0.6 * np.exp(-dt / (decay * 0.55))
        x += tail * tr * room * 0.22
    x = _tame_peaks(x, float(np.clip(p.get("limit_db", 6.0), 0, 12)))
    fo = min(_n(0.01), n)
    x[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    x = soft(x.astype(np.float32), p.get("drive", 0.0))
    return (x * vel ** 1.1).astype(np.float32)


# Model 2 (default since 2026-11-24): fitted to recorded hand claps. Measured against real claps (four tight claps and
# one looser group-like clap, 1/3-octave spectra and 5 ms envelopes; docs/TRANCE.md "Claps in trance"), model 1 decayed
# 40 dB in ~19 ms where real claps take 70-115 ms (soloed it read as "a clock ticking"), was ~5 dB too bright at
# 3-8 kHz and had almost no low body. Model 2 keeps the hands of model 1 (Peltola cavity resonances, a little narrower)
# and adds what the recordings show: the hands bunch in the first ~20 ms with later ones quieter, a dense tail that
# starts with the first hand and decays with a ~34 ms time constant at about -11 dB at 30 ms, a soft 100-400 Hz flesh
# thump and a roll-off above ~10 kHz. Constants from a fit to the recordings' mean (_HC2).
_HC2 = dict(tone=1.14, hand_tau=0.39, ring=2.5, res_g=1.36, slap=0.43, slap_lp=7000.0, body=2.2, body_lp=286.0,
            body_tau=0.039, room=8.5, tail_att=0.007, tail_lo=258.0, tail_c=1788.0, tail_hi=1.0, lp_hz=11400.0,
            hand_fall=0.022)


def _handclap2(p, vel, ps, rng):
    C = _HC2
    k = 2 ** (ps / 12) * p.get("tone", 1.0) * C["tone"]
    clappers = max(1, int(p.get("clappers", 4)))
    spread_ms = float(p.get("spread_ms", 9.0))
    if not 2.0 <= spread_ms <= 30.0:
        _hc_warn(f"handclap: spread_ms={spread_ms:g} is outside 2-30 ms (the gap between hands); clamped")
        spread_ms = float(np.clip(spread_ms, 2.0, 30.0))
    hands = p.get("hands", "mixed")
    modes = HC_HANDS.get(hands, HC_HANDS["mixed"]) if isinstance(hands, str) else tuple(hands)
    bright = p.get("bright", 0.35)
    body = p.get("body", 0.5)
    room = p.get("room", 0.35)
    decay = float(p.get("decay", 0.034))
    if not 0.01 <= decay <= 0.4:
        _hc_warn(f"handclap: decay={decay:g} s is outside 0.01-0.4 s (the room tail's time constant); clamped")
        decay = float(np.clip(decay, 0.01, 0.4))
    gaps = spread_ms / 1000 * rng.uniform(0.5, 1.5, clappers - 1)
    onsets = np.concatenate([[0.0], np.cumsum(gaps)])
    last = onsets[-1]
    n = _n(last + 0.03 + decay * 7)
    t = _t(n)
    hands_x = np.zeros(n, dtype=np.float32)
    nb = _n(0.02)
    tb = _t(nb)
    for i, t0 in enumerate(onsets):
        f, df, bw, dbw, g = HC_MODES[modes[rng.integers(len(modes))]]
        fc = max(350.0, rng.normal(f, df * 0.5)) * k
        bwi = max(60.0, rng.normal(bw, dbw * 0.5)) * k / C["ring"]
        tau = rng.uniform(0.0008, 0.0015) * C["hand_tau"]
        env = np.minimum(tb / 0.0003, 1) * np.exp(-tb / tau)
        e = rng.standard_normal(nb).astype(np.float32) * env.astype(np.float32)
        res = _bp_res(e, fc, bwi) * np.sqrt(g / 24.0) * 2.2 * C["res_g"] * np.sqrt(C["ring"])
        slap = lp(hp(e, 1500), C["slap_lp"]) * bright * C["slap"] * (0.55 + 0.55 * vel)
        lvl = (rng.uniform(0.6, 1.0) if i else rng.uniform(0.8, 1.0)) * np.exp(-t0 / C["hand_fall"])
        a = int(t0 * SR)
        m = min(nb, n - a)
        hands_x[a:a + m] += ((res + slap) * lvl)[:m]
    act = hands_x[:int((last + 0.006) * SR) + 1]
    hands_x /= np.sqrt(np.mean(act ** 2)) + 1e-9
    x = hands_x * 0.45
    if body > 0:  # the flesh thump: low noise under the hands
        th = lp(rng.standard_normal(n).astype(np.float32), C["body_lp"]) * np.exp(-t / C["body_tau"]) * np.minimum(t / 0.001, 1)
        x += th * body * C["body"] * 0.35
    if room > 0:  # the dense tail: starts with the first hand, highs die first
        nz = rng.standard_normal(n).astype(np.float32)
        lo_b, hi_b = bp(nz, C["tail_lo"], C["tail_c"] * 1.7), bp(nz, C["tail_c"] * 1.7, 7000)
        tr = 1 - np.exp(-np.maximum(t - 0.001, 0) / C["tail_att"])
        dt = np.maximum(t - 0.002, 0)
        tail = lo_b * np.exp(-dt / decay) + hi_b * C["tail_hi"] * np.exp(-dt / (decay * 0.5))
        x += tail * tr * room * C["room"] * 0.22
    x = lp(x, C["lp_hz"], 2)
    x = _tame_peaks(x, float(np.clip(p.get("limit_db", 6.0), 0, 12)))
    fo = min(_n(0.01), n)
    x[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    x = soft(x.astype(np.float32), p.get("drive", 0.0))
    return (x * vel ** 1.1).astype(np.float32)


DRUMS["handclap"] = handclap
ROUND_ROBIN = ROUND_ROBIN | {"handclap"}


# ---------------------------------------------------------------- singer (a voice that sings words)
# Additive block: lives in engine/singer.py (eSpeak NG + WORLD; imported only when a project uses it, so projects
# without a singer don't need either). It draws from its own random generators, so it changes nothing elsewhere.
_mono_voice_vox = mono_voice


def mono_voice(kind, p, notes, total_n):  # noqa: F811  (extends the chain with "singer")
    if kind == "singer":
        import singer as _singer
        return _singer.sing(p, notes, total_n)
    if kind == "vox2":  # the improved wordless voice (pure synthesis; also in engine/singer.py)
        import singer as _singer
        return _singer.vox2_line(p, notes, total_n)
    return _mono_voice_vox(kind, p, notes, total_n)


MONO.update({"singer", "vox2"})


# ---------------------------------------------------------------- lăutar band: violin, acoustic guitar, tobă
# Additive block (2026-11-24, for the joc țigănesc session; docs/JOC_TIGANESC.md). Each new sound draws from its own
# seeded generators, never from the module RNG, so projects that don't use them render exactly as before.
_mono_voice_singer = mono_voice


def mono_voice(kind, p, notes, total_n):  # noqa: F811  (extends the chain with "violin")
    if kind == "violin":
        import violin as _violin
        return _violin.violin_line(p, notes, total_n)
    return _mono_voice_singer(kind, p, notes, total_n)


def _violin_body(p, x):
    import violin as _violin
    return _violin.body(p, x)


MONO.add("violin")
POST["violin"] = _violin_body

_AG_RNG = {}


def _rng(name, seed):
    key = (name, int(seed))
    if key not in _AG_RNG:
        _AG_RNG[key] = np.random.default_rng(int(seed))
    return _AG_RNG[key]


def acguitar(p, f, vel, dur):
    """Acoustic guitar string (nylon by default, `strings: "steel"`), plucked or strummed; the wooden body is applied
    to the whole track afterwards (`acoustic_body`). chop 0-1 damps each chord right after its length (the
    afterbeat "țiitură" chop); scrape 0-1 is the pick or nail noise on the strings."""
    rng = _rng("acguitar", p.get("seed", 3))
    steel = p.get("strings", "nylon") == "steel"
    chop = float(p.get("chop", 0.0))
    rel = 0.07 * (1 - chop) + 0.012 * chop
    n = _n(dur + rel)
    t60 = p.get("sustain", 3.2 if steel else 2.0) * (220 / f) ** 0.4
    bright = float(p.get("bright", 0.55 if steel else 0.4))
    s = (0.42 if steel else 0.5) - 0.25 * bright
    L = max(4, int(SR / f))
    e = rng.standard_normal(L).astype(np.float32) * np.hanning(L).astype(np.float32)
    e = signal.sosfilt(signal.butter(2, min(900 + 8000 * bright * (0.4 + 0.6 * vel), SR * 0.45), fs=SR, output="sos"),
                       e).astype(np.float32)
    D = max(1, int(L * p.get("pluck_pos", 0.16)))
    e2 = e.copy()
    e2[D:] -= e[:-D]
    exc = np.zeros(n, dtype=np.float32)
    exc[:min(n, L)] = e2[:min(n, L)]
    y = ks_string(f, n, t60, exc, s)
    tt = _t(n)
    sc = float(p.get("scrape", 0.3))
    if sc > 0:  # the pick or nail across the string
        nz = rng.standard_normal(n).astype(np.float32)
        nz = signal.sosfilt(signal.butter(2, [1800, 7000], btype="band", fs=SR, output="sos"), nz).astype(np.float32)
        y = y + nz * np.exp(-tt / 0.012) * 0.25 * sc * vel
    h = _n(dur)
    if h < n:
        y[h:] *= np.exp(-np.arange(n - h) / _n(rel / 4))
    if chop > 0 and h < n:  # the palm landing on the strings
        m = min(n - h, _n(0.02))
        nz = rng.standard_normal(m).astype(np.float32)
        nz = signal.sosfilt(signal.butter(2, [150, 1500], btype="band", fs=SR, output="sos"), nz).astype(np.float32)
        y[h:h + m] += nz * np.exp(-np.arange(m) / _n(0.004)) * 0.08 * chop * vel
    return (y * vel * 0.6).astype(np.float32)


_AC_BODY = {}


def acoustic_body(p, x):
    """POST processor for `acguitar`: a modal guitar body (air mode ~100 Hz, top-plate modes ~200 and ~400 Hz,
    dense modes above; Fletcher & Rossing 1998, ch. 9), a DC block and a gentle top roll-off. mic 0-1 moves the
    microphone from the soundhole (warm, boomy) to the 12th fret (brighter, thinner)."""
    steel = p.get("strings", "nylon") == "steel"
    mic = float(p.get("mic", 0.5))
    key = (steel, round(mic, 3), int(p.get("body", 0)))
    if key not in _AC_BODY:
        rng = np.random.default_rng(200 + int(p.get("body", 0)))
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        modes = [(98 if steel else 95, 2 - 4 * mic, 14), (195 if steel else 185, 3 - 2 * mic, 20),
                 (235, -4, 22), (390 if steel else 370, -2, 25), (550, -6, 30)]
        fr = 650.0
        while fr < 8000:
            fr *= 2 ** rng.uniform(0.05, 0.13)
            lvl = -9 + rng.normal(0, 3) - 7 * max(0.0, np.log2(fr / (3500 if steel else 2500))) + 2 * mic * (fr > 1500)
            modes.append((fr, lvl, rng.uniform(20, 45)))
        ir = np.zeros(n)
        for f_, lv, q in modes:
            ir += 10 ** (lv / 20) * np.exp(-np.pi * f_ * t / q) * np.sin(2 * np.pi * f_ * t + rng.uniform(0, 6.28))
        ir[0] += 0.6
        ir /= np.sqrt((ir ** 2).sum()) * 4
        _AC_BODY[key] = ir.astype(np.float32)
    y = signal.oaconvolve(x, _AC_BODY[key])[:len(x)]
    y = signal.sosfilt(signal.butter(2, 70, btype="high", fs=SR, output="sos"), y)
    y = signal.sosfilt(signal.butter(2, 12000 if steel else 10000, fs=SR, output="sos"), y)
    return y.astype(np.float32)


def toba(p, vel, ps=0.0):
    """Tobă mare: the big double-headed bass drum of the lăutar fanfare and the village band, with a cymbal (cinel,
    talger) mounted on top that the same player strikes with a rod. stroke: boom (felt mallet on the head), cinel
    (the cymbal alone), both (the two together, the accented beat), rim (the mallet on the hoop, a dry knock).
    tune Hz (60), decay s (0.2; the head's time constant), cinel_decay s (0.35; lower = held by the hand), bright 0-1 (the cymbal's colour)."""
    stroke = p.get("stroke", "boom")
    rng = _rng("toba", p.get("seed", 5))
    out = None
    if stroke in ("boom", "both"):
        tune = p.get("tune", 60) * 2 ** (ps / 12)
        decay = p.get("decay", 0.2)
        n = _n(decay * 4 + 0.05)
        t = _t(n)
        f = tune * (1 + 0.25 * vel * np.exp(-t / 0.02))
        ph = 2 * np.pi * np.cumsum(f) / SR
        head = np.zeros(n, dtype=np.float32)
        for r, g, d in zip(MEMBRANE[:6], (1.0, 0.5, 0.35, 0.25, 0.18, 0.12), (1.0, 0.45, 0.3, 0.25, 0.2, 0.15)):
            head += (g * np.sin(ph * r + rng.uniform(0, 6.28)) * np.exp(-t / (decay * d))).astype(np.float32)
        thud = rng.standard_normal(n).astype(np.float32)
        thud = signal.sosfilt(signal.butter(2, [60, 700], btype="band", fs=SR, output="sos"), thud).astype(np.float32)
        head += thud * np.exp(-t / 0.018) * 0.6
        head *= np.minimum(t / 0.0015, 1)  # the felt mallet: no click
        out = soft(head, 0.1) * 0.9
    if stroke == "rim":
        n = _n(0.2)
        t = _t(n)
        x = rng.standard_normal(n).astype(np.float32)
        x = signal.sosfilt(signal.butter(2, [500, 4000], btype="band", fs=SR, output="sos"), x).astype(np.float32)
        out = (x * np.exp(-t / 0.012) + 0.4 * np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.03)).astype(np.float32)
    if stroke in ("cinel", "both"):
        dec = p.get("cinel_decay", 0.35)
        n = _n(dec * 4 + 0.05)
        t = _t(n)
        bright = float(p.get("bright", 0.5))
        k = 60
        fr = np.exp(rng.uniform(np.log(450), np.log(11000), k))
        am = (fr / 450) ** (-0.6 + 0.4 * bright) * rng.uniform(0.4, 1.0, k)
        dc = dec * (fr / 2000) ** -0.35 * rng.uniform(0.6, 1.2, k)
        cym = np.zeros(n, dtype=np.float32)
        for j in range(0, k, 20):
            cym += (am[j:j + 20, None] * np.sin(2 * np.pi * fr[j:j + 20, None] * t[None, :]
                                                 + rng.uniform(0, 6.28, (min(20, k - j), 1)))
                    * np.exp(-t[None, :] / dc[j:j + 20, None])).sum(0).astype(np.float32)
        nz = rng.standard_normal(n).astype(np.float32)
        nz = signal.sosfilt(signal.butter(2, 3000, btype="high", fs=SR, output="sos"), nz).astype(np.float32)
        cym += nz * np.exp(-t / (dec * 0.4)) * 0.5
        cym = cym / (np.abs(cym).max() + 1e-9) * (0.55 if stroke == "both" else 0.75)
        if out is None:
            out = cym
        else:
            m = max(len(out), len(cym))
            out = np.pad(out, (0, m - len(out))) + np.pad(cym, (0, m - len(cym)))
    if out is None:
        raise ValueError(f"toba: unknown stroke '{stroke}' (boom, cinel, both, rim)")
    return (out * vel ** 1.1).astype(np.float32)


TONAL["acguitar"] = acguitar
POST["acguitar"] = acoustic_body
DRUMS["toba"] = toba
ROUND_ROBIN = ROUND_ROBIN | {"toba"}
