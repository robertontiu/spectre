"""Bass music, second pass (2026-11-26): sounds fitted to recorded references (docs/MANUAL.md "Bass music, fitted";
examples/production/dubstep-v2/). Everything here is opt-in, so every earlier project renders bit-identically:

  presets      a track's `"preset": "<name>"` fills in an instrument (or a stack of layers), role and fx chain fitted to
               openly licensed reference one-shots (engine/third_party.json `refs-dubstep-*`); whatever the track sets
               itself wins (its `inst` keys over the preset's, any other key replaces the preset's).
  fx           `curve` (a minimum-phase EQ through third-octave points: the fitted tone of a preset), `transient`
               (attack / sustain shaping from two envelope followers), `widen` (mono-compatible width above a
               frequency: a delayed, high-passed copy of the mid added to the side; for mono sources).
  transitions  `"fx_model": 2` in a project: the section `enter`/`exit` effects (impact, downlifter, riser, rise,
               reverse) become stereo and full-bodied, fitted to reference impacts, risers and downlifters.

The numbers each preset was fitted to, and the method, are in examples/production/dubstep-v2/README.md.
"""
import copy

import numpy as np
from scipy import signal

SR = 44100
FX = ("curve", "transient", "widen")

THIRD = (25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
         3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000)


def _db(x):
    return 10 ** (np.asarray(x, dtype=np.float64) / 20)


# ------------------------------------------------------------------ fx

def _minphase_fir(points, nfft=8192):
    """A minimum-phase FIR whose magnitude follows `points` {hz: dB} (log-frequency interpolation, flat outside)."""
    hz = np.array(sorted(float(k) for k in points))
    g = np.array([float(points[k]) for k in sorted(points, key=float)])
    f = np.fft.rfftfreq(nfft, 1 / SR)
    lf = np.log2(np.maximum(f, 1.0))
    mag_db = np.interp(lf, np.log2(hz), g)
    logmag = np.log(_db(mag_db))
    cep = np.fft.irfft(logmag, nfft)               # real cepstrum of the magnitude
    fold = np.zeros(nfft)
    fold[0] = cep[0]
    fold[1:nfft // 2] = 2 * cep[1:nfft // 2]
    fold[nfft // 2] = cep[nfft // 2]
    h = np.fft.irfft(np.exp(np.fft.rfft(fold)), nfft)
    L = nfft // 2
    return h[:L] * np.hanning(2 * L)[L:]


_FIR_CACHE = {}


def curve(st, fx):
    """fx: points {hz: dB} (third-octave gains; the fitted tone of a preset), gain_db (0)."""
    pts = fx.get("points") or {}
    if not pts:
        return st
    key = tuple(sorted((float(k), float(v)) for k, v in pts.items()))
    if key not in _FIR_CACHE:
        _FIR_CACHE[key] = _minphase_fir(dict(key))
    h = _FIR_CACHE[key]
    y = signal.oaconvolve(st.astype(np.float64), h[None, :], axes=-1)[:, :st.shape[1]]
    return (y * _db(float(fx.get("gain_db", 0.0)))).astype(np.float32)


def _env_db(x, att_ms, rel_ms):
    import mixbus as MB
    return MB.follower_db(x, att_ms, rel_ms, D=8)


def transient(st, fx):
    """fx: attack_db (+6; gain on the onsets), sustain_db (0; gain on what follows), fast_ms (1), slow_ms (25),
    release_ms (60), range_db (12: the fast-over-slow difference that counts as fully attack or fully sustain).
    A level-independent transient designer: a fast and a slow follower of the same signal; where the fast one leads,
    the attack gain applies, where it trails, the sustain gain."""
    x = st.astype(np.float64)
    m = np.abs(x).max(0)
    fast = _env_db(m, float(fx.get("fast_ms", 1.0)), float(fx.get("release_ms", 60.0)))
    slow = _env_db(m, float(fx.get("slow_ms", 25.0)), float(fx.get("release_ms", 60.0)))
    d = fast - slow
    rng = float(fx.get("range_db", 12.0))
    att = np.clip(d / rng, 0, 1)
    sus = np.clip(-d / rng, 0, 1)
    on = fast > fast.max() - 70                    # leave silence alone
    g = (float(fx.get("attack_db", 6.0)) * att + float(fx.get("sustain_db", 0.0)) * sus) * on
    return (x * _db(g)[None, :]).astype(np.float32)


def widen(st, fx):
    """fx: from_hz (300; nothing below gets width), amount 0-1 (0.5; side added, relative to the mid), delay_ms (11),
    second_ms (17: a second tap of the opposite sign, so the side has no single comb). Mono-compatible: L+R is
    unchanged."""
    x = st.astype(np.float64)
    m = 0.5 * (x[0] + x[1])
    s = 0.5 * (x[0] - x[1])
    hpf = signal.butter(2, float(fx.get("from_hz", 300.0)), btype="high", fs=SR, output="sos")
    h = signal.sosfilt(hpf, m)
    d1, d2 = int(float(fx.get("delay_ms", 11.0)) / 1000 * SR), int(float(fx.get("second_ms", 17.0)) / 1000 * SR)
    side = np.zeros_like(h)
    side[d1:] += h[:len(h) - d1]
    side[d2:] -= 0.6 * h[:len(h) - d2]
    s = s + float(fx.get("amount", 0.5)) * side
    return np.stack([m + s, m - s]).astype(np.float32)


def apply(st, fx):
    k = fx["type"]
    if k == "curve":
        return curve(st, fx)
    if k == "transient":
        return transient(st, fx)
    if k == "widen":
        return widen(st, fx)
    raise ValueError(f"unknown fx '{k}'")


# ------------------------------------------------------------------ transitions ("fx_model": 2)
# Fitted to the reference impacts, risers and downlifters (examples/production/dubstep-v2/README.md, "Transitions"):
# all stereo (the references' side sits 1-7 dB under the mid above 150 Hz; the old ones are mono), and with a body in
# 60-500 Hz (the old impact is a 40 Hz sine with a little noise: 0 dB in the sub, -28 to -40 dB in 60-500 Hz, against
# the references' -6 / -5 / -10 dB).

def _rng():
    import instruments as I
    return I.RNG


def _noise(n):
    return _rng().standard_normal(n)


def _bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR * 0.45)], btype="band", fs=SR, output="sos"), x)


def _stereo(m, amount, from_hz=200.0):
    st = np.stack([m, m])
    return widen(st.astype(np.float32), {"amount": amount, "from_hz": from_hz}).astype(np.float64)


def _decor_tail(x, sec, amount):
    """A short stereo diffusion: two different noise-burst convolutions (a small room) mixed in."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    out = []
    for _ in range(2):
        ir = _noise(n) * np.exp(-t / (sec / 6.9))
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
        out.append(signal.oaconvolve(x, ir)[:len(x)])
    return np.stack(out) * amount


def impact(vel=1.0):
    """A drop's first-beat hit: a pitched boom (170 -> 50 Hz over about 0.25 s, so it spends its energy in 50-150 Hz,
    low band down 20 dB in about 0.2 s), a short body of band-passed noise (100-600 Hz) diffused into a wide room, a
    faint top (1-8 kHz) with the room's 0.8 s tail; soft-clipped to a crest about 12 dB."""
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 50 * (1 + 2.4 * np.exp(-t / 0.08))
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.10) * np.clip(t / 0.002, 0, 1)
    body = _bp(_noise(n), 100, 700) * np.exp(-t / 0.08) * 0.45
    top = _bp(_noise(n), 1000, 8000) * np.exp(-t / 0.25) * 0.012
    mono = boom + body + top
    room_in = signal.sosfilt(signal.butter(2, 450, fs=SR, output="sos"), body) + top
    st = np.stack([mono, mono]) + _decor_tail(room_in, 1.6, 4.5)
    st = np.tanh(st * 1.4) / np.tanh(1.4)
    return (st * vel).astype(np.float32)


def downlifter(sec):
    """Falling noise and a falling tone: noise swept 8 kHz -> 150 Hz with a body under it (a sine falling two octaves
    from 160 Hz), stereo; decays over the length."""
    import instruments as I
    n = int(sec * SR)
    t = np.arange(n) / SR
    nz = I.sweep_noise(n, 8000, 150).astype(np.float64)
    f = 260 * 2 ** (-2 * t / max(sec, 1e-3))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    env = np.exp(-t / (sec * 0.45)) * np.clip(t / 0.004, 0, 1)
    m = (nz + tone) * env
    return (_stereo(m, 1.0, 150) * 0.8).astype(np.float32)


def riser(sec):
    """Noise swept 300 Hz -> 9 kHz plus a rising detuned-saw body (the old `rise` voice, half level), stereo, a
    squared swell."""
    import instruments as I
    n = int(sec * SR)
    t = np.arange(n) / SR
    nz = I.sweep_noise(n, 300, 9000).astype(np.float64)
    body = I.pitch_riser(sec).astype(np.float64)
    low = _bp(_noise(n), 60, 400) * 0.25
    m = (nz * 0.5 + body * 1.0 + low) * (t / sec) ** 2
    return (_stereo(m, 0.55, 200) * 1.2).astype(np.float32)


def pitch_riser(sec):
    import instruments as I
    return (_stereo(I.pitch_riser(sec).astype(np.float64), 0.8, 200)).astype(np.float32)


def reverse_cymbal(sec):
    import instruments as I
    return (_stereo(I.reverse_cymbal(sec).astype(np.float64), 0.8, 500)).astype(np.float32)


# ------------------------------------------------------------------ presets

def _load_presets():
    import json
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "bass_presets.json")) as fh:
        out = {k: v for k, v in json.load(fh)["presets"].items()}
    tp = os.path.join(here, "techno_presets.json")  # the techno presets (engine/techno.py, 2026-11-26)
    if os.path.exists(tp):
        with open(tp) as fh:
            for k, v in json.load(fh)["presets"].items():
                if k in out:
                    raise ValueError(f"preset '{k}' is in both bass_presets.json and techno_presets.json")
                out[k] = v
    return out


PRESETS = _load_presets()


def apply_presets(P):
    """A copy of P in which every track with a `"preset"` has the preset's keys filled in (the track's own `inst` keys
    over the preset's `inst`, any other key of the track replaces the preset's); P itself when no track names one."""
    if not any(isinstance(tr, dict) and tr.get("preset") for tr in P.get("tracks", {}).values()):
        return P
    tracks = {}
    for name, tr in P["tracks"].items():
        pr = tr.get("preset")
        if not pr:
            tracks[name] = tr
            continue
        if pr not in PRESETS:
            raise ValueError(f"track '{name}': unknown preset '{pr}' ({', '.join(sorted(PRESETS))})")
        out = copy.deepcopy(PRESETS[pr]["track"])
        for k, v in tr.items():
            if k == "preset":
                continue
            if k == "inst" and isinstance(out.get("inst"), dict) and isinstance(v, dict):
                out["inst"] = dict(out["inst"], **copy.deepcopy(v))
            elif (k == "inst" and out.get("layers") and not out.get("inst") and isinstance(v, dict)
                  and "type" not in v):  # a stacked preset: the keys tune its first layer (the body), e.g. a note
                out["layers"][0]["inst"] = dict(out["layers"][0]["inst"], **copy.deepcopy(v))
            else:
                out[k] = copy.deepcopy(v)
        tracks[name] = out
    return dict(P, tracks=tracks)
