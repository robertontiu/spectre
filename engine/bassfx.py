"""Bass-music effects (docs/DUBSTEP.md "Engine mapping", gaps 6, 7, 10, 11, 12; docs/MANUAL.md "Bass music").
Additive: studio.py calls into this module only for these fx types, so every earlier project renders as before.
Nothing here draws random numbers.

  multiband   split at 1-3 crossovers (Linkwitz-Riley 4th order, the bands sum flat) and run an fx chain per band,
              with a gain and a width per band
  fold        wavefolder (sine fold, 4x oversampled), with a bias for even harmonics
  asym        asymmetric saturation and rectification (even harmonics; full-wave rectify adds the octave)
  hardclip    hard clipper with drive, 4x oversampled
  comb        a feedback comb filter tuned to a note or Hz, its delay optionally swept by a synced LFO
  flanger     a short swept delay with feedback, rate in note values or Hz
  resonator   a bank of tuned feedback combs (a chord): a growl rings at those pitches
  autofilter  a resonant filter swept by a synced LFO (lp / bp / hp), or opened by the signal's own envelope
  autopan     synced pan
  vowel       the formant filter (engine/bass.py) as an fx, its position fixed or swept by a synced LFO
  vocoder     a channel vocoder: the track's band envelopes (the modulator) shape a chord of saws (the carrier), so
              a growl "rings as chords" (colour bass)
LFOs here are locked to the song's grid (phase 0 at the song's start), so a wobble stays on the beat.
"""
import math

import numpy as np
from scipy import signal

SR = 44100

try:
    from numba import njit
except Exception:  # pragma: no cover
    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f

FX = ("multiband", "fold", "asym", "hardclip", "comb", "flanger", "resonator", "autofilter", "autopan", "vowel",
      "vocoder")


def _hz(note_or_hz):
    if isinstance(note_or_hz, str):
        from hand import note_to_midi, midi_to_hz
        return float(midi_to_hz(note_to_midi(note_or_hz)))
    return float(note_or_hz)


def _lfo(fx, n, bpm, default_rate="1/4", default_shape="sine"):
    """A grid-locked LFO 0..1 for an fx (rate in note values or Hz; shape as engine/bass.py)."""
    import bass as B
    hz = B.rate_hz(fx.get("rate", default_rate), bpm)
    ph = float(fx.get("phase", 0.0)) + hz * np.arange(n) / SR
    return B._wave(fx.get("shape", default_shape), ph, fx.get("steps"), np.random.default_rng(0))


def _os(st, fn, factor=4):
    up = signal.resample_poly(st.astype(np.float64), factor, 1, axis=-1)
    return signal.resample_poly(fn(up), 1, factor, axis=-1)[:, :st.shape[1]]


def _lr4(x, fc):
    lo = signal.butter(2, fc, btype="low", fs=SR, output="sos")
    hi = signal.butter(2, fc, btype="high", fs=SR, output="sos")
    return (signal.sosfilt(lo, signal.sosfilt(lo, x, axis=-1), axis=-1),
            signal.sosfilt(hi, signal.sosfilt(hi, x, axis=-1), axis=-1))


@njit(cache=True)
def _comb(x, delay, fb, damp):
    """y[n] = x[n] + fb * lp(y[n - d(n)]), d per sample (fractional), a one-pole low-pass `damp` in the loop."""
    n = len(x)
    size = 1
    mx = 0.0
    for i in range(n):
        if delay[i] > mx:
            mx = delay[i]
    while size < int(mx) + 4:
        size *= 2
    mask = size - 1
    buf = np.zeros(size)
    y = np.empty(n)
    lp = 0.0
    for i in range(n):
        d = delay[i]
        ip = int(d)
        fr = d - ip
        a = buf[(i - ip) & mask]
        b = buf[(i - ip - 1) & mask]
        v = a + (b - a) * fr
        lp = v * (1.0 - damp) + lp * damp
        out = x[i] + fb * lp
        buf[i & mask] = out
        y[i] = out
    return y


def apply(st, fx, bpm, run_chain):
    """st (2, n); fx a dict whose type is in FX; run_chain(x, fx_list) runs a nested fx chain (multiband bands)."""
    k = fx["type"]
    n = st.shape[1]
    x = st.astype(np.float64)
    mix = float(fx.get("mix", 1.0))
    if k == "multiband":
        split = sorted(float(v) for v in fx.get("split", [150.0, 2500.0]))
        if not 1 <= len(split) <= 3:
            raise ValueError("multiband: `split` takes 1-3 crossover frequencies")
        bands, rest = [], x
        for fc in split:
            lo, rest = _lr4(rest, fc)
            bands.append(lo)
        bands.append(rest)
        chains = fx.get("bands") or []
        gains = fx.get("gains_db") or [0.0] * len(bands)
        widths = fx.get("widths") or [None] * len(bands)
        y = np.zeros_like(x)
        for i, b in enumerate(bands):
            if i < len(chains) and chains[i]:
                b = run_chain(b.astype(np.float32), chains[i]).astype(np.float64)
            if i < len(widths) and widths[i] is not None:
                m = 0.5 * (b[0] + b[1])
                s = 0.5 * (b[0] - b[1]) * float(widths[i])
                b = np.stack([m + s, m - s])
            y += b * 10 ** (float(gains[i] if i < len(gains) else 0.0) / 20)
        return y.astype(np.float32)
    if k == "fold":
        g = 1 + 8 * float(np.clip(fx.get("amount", 0.5), 0, 1))
        bias = float(fx.get("bias", 0.0))
        y = _os(x, lambda u: np.sin(np.pi / 2 * g * (u + bias)) - np.sin(np.pi / 2 * g * bias))
    elif k == "asym":
        a = float(np.clip(fx.get("amount", 0.5), 0, 1))
        kk = 1 + 9 * a
        bias = float(fx.get("bias", 0.3))
        rect = float(np.clip(fx.get("rectify", 0.0), 0, 1))

        def f(u):
            v = (np.tanh(kk * (u + bias)) - np.tanh(kk * bias)) / np.tanh(kk)
            return v * (1 - rect) + (np.abs(v) - np.mean(np.abs(v), axis=-1, keepdims=True)) * rect
        y = _os(x, f)
    elif k == "hardclip":
        g = 10 ** (float(fx.get("drive_db", 6.0)) / 20)
        c = 10 ** (float(fx.get("ceiling_db", -1.0)) / 20)
        y = _os(x, lambda u: np.clip(u * g, -c, c))
    elif k in ("comb", "flanger"):
        if k == "comb":
            base = SR / _hz(fx.get("note", fx.get("hz", 110.0)))
            depth = float(fx.get("depth", 0.0)) * base
            fb = float(np.clip(fx.get("feedback", 0.85), -0.99, 0.99))
            damp = float(np.clip(fx.get("damp", 0.2), 0, 0.95))
        else:
            base = float(fx.get("base_ms", 2.5)) / 1000 * SR
            depth = float(fx.get("depth_ms", 2.0)) / 1000 * SR
            fb = float(np.clip(fx.get("feedback", 0.6), -0.99, 0.99))
            damp = 0.0
            mix = float(fx.get("mix", 0.5))
        dl = base + (depth * (_lfo(fx, n, bpm, "1/2" if k == "flanger" else "1/4") - 0.5) if depth else 0.0)
        dl = np.maximum(np.broadcast_to(np.asarray(dl, dtype=np.float64), (n,)), 1.0).copy()
        y = np.stack([_comb(np.ascontiguousarray(c), dl, fb, damp) for c in x]) * (1 - abs(fb)) ** 0.5
    elif k == "resonator":
        notes = fx.get("notes") or ["A2"]
        fb = float(np.clip(fx.get("feedback", 0.97), 0, 0.999))
        damp = float(np.clip(fx.get("damp", 0.3), 0, 0.95))
        y = np.zeros_like(x)
        for nt in notes:
            d = np.full(n, SR / _hz(nt))
            y += np.stack([_comb(np.ascontiguousarray(c), d, fb, damp) for c in x])
        r_in = np.sqrt(np.mean(x ** 2))
        r_out = np.sqrt(np.mean(y ** 2))
        if r_out > 0:
            y *= r_in / r_out             # the ringing comes back at the level of what went in
        mix = float(fx.get("mix", 0.5))
    elif k == "autofilter":
        import bass as B
        lo, hi = float(fx.get("lo", 200.0)), float(fx.get("hi", 4000.0))
        if fx.get("follow"):          # the signal's own envelope opens the filter
            from scipy.ndimage import uniform_filter1d
            e = np.sqrt(uniform_filter1d(x.mean(0) ** 2, int(0.01 * SR)))
            w = np.clip(e / (np.percentile(e, 99) + 1e-9), 0, 1) ** float(fx.get("curve", 0.6))
        else:
            w = _lfo(fx, n, bpm, "1/8")
        cut = lo * (hi / lo) ** w
        qv = np.full(n, 0.707 + 9 * float(np.clip(fx.get("reso", 0.3), 0, 1)))
        mode = {"lp": 0, "bp": 1, "hp": 2}[fx.get("mode", "lp")]
        y = np.stack([B.svf(np.ascontiguousarray(c), cut, qv, mode) for c in x])
    elif k == "autopan":
        w = 2 * _lfo(fx, n, bpm, "1/4") - 1
        a = (np.clip(w * float(fx.get("depth", 0.8)), -1, 1) + 1) * np.pi / 4
        m = 0.5 * (x[0] + x[1])
        y = np.stack([m * np.cos(a), m * np.sin(a)]) * np.sqrt(2)
    elif k == "vowel":
        import bass as B
        p0 = B.vowel_pos(fx.get("vowel", "ah"))
        pos = np.full(n, p0)
        if fx.get("rate") is not None:
            pos = pos + float(fx.get("depth", 2.0)) * _lfo(fx, n, bpm, "1/4")
        y = np.stack([B.formant(np.ascontiguousarray(c), pos, float(fx.get("q", 1.0)), float(fx.get("shift", 1.0)))
                      for c in x])
    elif k == "vocoder":
        import bass as B
        from hand import note_to_midi, midi_to_hz
        nb = int(fx.get("bands", 20))
        lo, hi = float(fx.get("lo", 120.0)), float(fx.get("hi", 8000.0))
        cf = lo * (hi / lo) ** (np.arange(nb) / max(nb - 1, 1))
        qb = float(fx.get("q", 6.0))
        t = np.arange(n) / SR
        car = np.zeros(n)
        for nt in fx.get("notes") or ["A2"]:
            f0 = float(midi_to_hz(note_to_midi(nt))) if isinstance(nt, str) else float(nt)
            for o, g in ((0, 1.0), (1, 0.5)):    # the note and its octave: saws, naive but low-passed by the bands
                ph = (f0 * 2 ** o * t + 0.37 * o) % 1.0
                car += g * (2 * ph - 1)
        car += float(fx.get("noise", 0.05)) * np.random.default_rng(11).standard_normal(n)
        att = int(float(fx.get("smooth_ms", 12.0)) / 1000 * SR)
        y = np.zeros_like(x)
        qv = np.full(n, qb)
        cbands = [B.svf(car, np.full(n, c), qv, 1) for c in cf]
        for ch in range(2):
            mod = np.ascontiguousarray(x[ch])
            acc = np.zeros(n)
            for c, cb in zip(cf, cbands):
                band = B.svf(mod, np.full(n, c), qv, 1)
                env = np.sqrt(np.convolve(band ** 2, np.ones(att) / att, mode="same"))
                acc += cb * env
            y[ch] = acc
        r_in = np.sqrt(np.mean(x ** 2))
        r_out = np.sqrt(np.mean(y ** 2))
        if r_out > 0:
            y *= r_in / r_out
        mix = float(fx.get("mix", 0.7))
    else:
        raise ValueError(f"unknown bass fx '{k}'")
    return (x * (1 - mix) + y * mix).astype(np.float32)


def gate_wet(wet, key, cfg):
    """Gated reverb: the return's output passes only while its input is loud (within `threshold_db` of its own peak,
    -30) and for `hold_ms` (120) after, closing over `release_ms` (30)."""
    from scipy.ndimage import maximum_filter1d
    e = np.abs(key).max(0)
    w = int(0.002 * SR)
    e = maximum_filter1d(e, w)
    thr = e.max() * 10 ** (float(cfg.get("threshold_db", -30.0)) / 20)
    op = (e > thr).astype(np.float64)
    hold = int(float(cfg.get("hold_ms", 120.0)) / 1000 * SR)
    op = (np.convolve(op, np.ones(hold + 1))[:len(op)] > 0).astype(np.float64)   # open for `hold` after the input
    rel = np.exp(-1 / max(float(cfg.get("release_ms", 30.0)) / 1000 * SR, 1))
    g = signal.lfilter([1 - rel], [1, -rel], op)
    g = np.maximum(g, op)
    return (wet * g[None, :]).astype(np.float32)
