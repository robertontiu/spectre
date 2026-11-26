"""Psytrance additions (docs/PSYTRANCE.md "Engine mapping"; docs/MANUAL.md "Psytrance"): `sleighbells`, a modal
model of a strap of jingle bells, and `zap`, the pitch-dive (or pitch-rise) laser of psy sound design. Additive: used
only when a track names them; both are drums (one hit, no pitch from the pattern) and draw from the module generator
`instruments.RNG` at call time, so per-track seeds give each track its own stream.

Sleigh bells. A strap of small closed bells (crotal bells), each a thin brass shell with a loose pellet: shaking the
strap makes the pellets strike their shells many times, out of step, over a few hundred milliseconds; each strike
rings the shell's few modes, which decay in under a second. Here: `bells` shells, each with three modes at the ratios
measured on the reference (about 2.6, 6.6 and 10.5 kHz for a medium strap: 1 : 2.55 : 4.05), each mode a two-pole
resonator driven by its shell's impulse train; the impacts fall densest at the start of the shake and thin out
across `shake` seconds; a pellet click (high-passed noise, 1-2 ms) on each impact. Fitted to VSCO-2 CE (Versilian
Studios Chamber Orchestra 2, Community Edition, CC0; sleigh bells "Sleighbells_Hit" and "sleighbell1/2_hit", 13
samples; measured only, kept in ~/.cache/spectre/refs/psytrance/sleighbells/, never in the repo); the fit is in
docs/MANUAL.md "Psytrance" and examples/production/psytrance/measure_sleighbells.py.

Zap. A sine whose frequency falls (or rises) exponentially from `start` to `end` Hz over `time` seconds, with an
optional FM bite (`fm` index, `ratio`) and a decay: the "laser", "pew" and pitch-dive effects of psy and of
electronic music since the 1970s synthesizer drums (a falling pitch envelope on an oscillator)."""
import numpy as np
from scipy import signal

import instruments as I

SR = I.SR
TWO_PI = 2 * np.pi

# defaults fitted to the VSCO-2 CE straps (docs/MANUAL.md "Psytrance"): mode ratios to the shell's first mode, their
# levels (linear, at the strike) and their T60 in seconds
SLEIGH = dict(bells=12, size=1.0, spread=0.05, shake=0.45, hits=10, decay=1.0, click=0.35, damp=0.0, tone=0.7)
_MODES = ((1.0, 0.9, 0.6), (1.7, 0.1, 0.35), (2.55, 1.0, 0.75), (4.05, 0.8, 0.5), (6.3, 0.22, 0.35))
_F1 = 2600.0


def _rng():
    return I.RNG


def _reson(x, f, t60):
    """A two-pole resonator at f Hz whose impulse response (a unit impulse in) starts at amplitude about 1 and decays by
    60 dB in t60 s."""
    r = np.exp(-6.91 / (max(t60, 0.01) * SR))
    w = TWO_PI * f / SR
    return signal.lfilter([np.sin(w)], [1.0, -2 * r * np.cos(w), r * r], x)


def sleighbells(p, vel, ps=0.0):
    """Sleigh bells: one shake of a strap. `bells` (12) shells, `size` (1.0: scales the pitch of every shell; 1.15 a
    smaller, brighter strap, 0.85 a bigger one), `spread` (0.05: the shells' spread in pitch), `shake` (0.45 s: the
    span of the pellets' strikes; 0.12-0.2 for a tight 16th-note jingle, 0.6-1.0 for a long shake), `hits` (26:
    strikes across the shake), `decay` (1.0: scales the ring), `click` (0.35: the pellet's click), `damp` (0: 1 grips
    the strap right after the shake, a short dry jingle), `tone` (0.7: 0 duller, 1 brighter: the top mode's level).
    `ps` shifts the pitch (semitones)."""
    q = dict(SLEIGH)
    q.update({k: v for k, v in p.items() if k in SLEIGH})
    rng = _rng()
    shake = max(0.02, float(q["shake"]))
    dec = max(0.1, float(q["decay"]))
    damp = float(np.clip(q["damp"], 0, 1))
    ring = 1.2 * dec * (1 - 0.8 * damp)
    n = I._n(shake + ring + 0.02)
    t_end = shake + ring
    nb = max(1, int(q["bells"]))
    nh = max(1, int(round(float(q["hits"]) * (0.6 + 0.6 * vel))))
    # strike times: dense at the start, thinning out (the strap's swing loses energy); amplitudes fall with it
    u = np.sort(rng.random(nh))
    times = np.concatenate([[0.0], shake * u[1:] ** 1.7])
    amps = np.exp(-times / (0.45 * shake)) * (0.4 + 0.6 * rng.random(nh))
    amps[0] = 1.0
    f_scale = float(q["size"]) * 2 ** (ps / 12)
    tone = float(np.clip(q["tone"], 0, 1))
    out = np.zeros(n)
    for b in range(nb):
        x = np.zeros(n)
        for t0, a in zip(times, amps):  # each strike sets about a third of the shells ringing
            if rng.random() < 0.35 or (t0 == 0.0 and b % 3 == 0):
                i = int(t0 * SR + rng.random() * 0.002 * SR)
                if i < n:
                    x[i] += a * (0.5 + 0.5 * rng.random())
        if not x.any():
            continue
        f1 = _F1 * f_scale * (1 + float(q["spread"]) * rng.standard_normal())
        for ratio, lev, t60 in _MODES:
            f = f1 * ratio * (1 + 0.004 * rng.standard_normal())
            if f > SR * 0.45:
                continue
            g = lev * (0.55 + 0.9 * tone if ratio > 4 else 1.0)
            out += g * _reson(x, f, t60 * dec)
    # the pellet clicks: a short high-passed noise burst on every strike
    clk = np.zeros(n)
    for t0, a in zip(times, amps):
        i = int(t0 * SR)
        m = min(I._n(0.004), n - i)
        if m > 0:
            clk[i:i + m] += a * rng.standard_normal(m) * np.exp(-np.arange(m) / (0.001 * SR))
    clk = signal.sosfilt(signal.butter(2, 3500, "high", fs=SR, output="sos"), clk)
    out += float(q["click"]) * 6.0 * clk
    t = np.arange(n) / SR
    if damp > 0:  # a hand grips the strap: the ring stops soon after the shake
        out *= np.where(t < shake, 1.0, np.exp(-(t - shake) / (0.02 + 0.3 * (1 - damp))))
    fo = min(I._n(0.02), n)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = signal.sosfilt(signal.butter(2, 1500, "high", fs=SR, output="sos"), out)
    pk = np.max(np.abs(out)) or 1.0
    if vel < 0.7:  # a softer shake is a duller one
        out = signal.sosfilt(signal.butter(1, 6000 + 10000 * vel, "low", fs=SR, output="sos"), out)
    return (out / pk * 0.8 * vel).astype(np.float32)


ZAP = dict(start=3000.0, end=80.0, time=0.25, curve=1.0, fm=0.0, ratio=2.0, decay=0.3, drive=0.0, tail=0.05)


def zap(p, vel, ps=0.0):
    """A pitch-dive zap: a sine from `start` Hz (3000) to `end` Hz (80) over `time` s (0.25), exponential in pitch
    (`curve` 1; above 1 the drop comes faster at first, below 1 it lingers high), amplitude decaying with time constant
    `decay` s (0.3) and faded out over `tail` s (0.05) after `time`; `fm` 0-5 (0: a pure laser; 1-3 a metallic,
    squelchy bite) at `ratio` x the moving frequency (2.0); `drive` 0-1 saturation. With `start` < `end` it rises
    (a reverse zap, the "up" laser). `ps` shifts both ends (semitones)."""
    q = dict(ZAP)
    q.update({k: v for k, v in p.items() if k in ZAP})
    k = 2 ** (ps / 12)
    f0, f1 = float(q["start"]) * k, float(q["end"]) * k
    tt = max(0.01, float(q["time"]))
    tail = max(0.005, float(q["tail"]))
    n = I._n(tt + tail)
    t = np.arange(n) / SR
    x = np.clip(t / tt, 0, 1) ** float(q["curve"])
    f = f0 * (f1 / f0) ** x
    ph = TWO_PI * np.cumsum(f) / SR
    idx = float(q["fm"])
    y = np.sin(ph + idx * np.sin(float(q["ratio"]) * ph)) if idx > 0 else np.sin(ph)
    env = np.exp(-t / max(0.01, float(q["decay"]))) * np.clip(t / 0.001, 0, 1)
    env *= np.where(t < tt, 1.0, np.clip(1 - (t - tt) / tail, 0, 1))
    y = I.soft((y * env).astype(np.float32), float(q["drive"]))
    return (y * 0.9 * vel).astype(np.float32)
