"""Techno sounds fitted to recordings (2026-11-26; docs/TECHNO.md "Engine mapping" gaps 1-7; docs/MANUAL.md "Techno,
fitted"; fits and numbers in examples/production/techno/). Everything here is opt-in, so every earlier project renders
bit-identically: the drums run only when a track names them, the rumble only when a project has a `rumble` return or a
track with a `"rumble"` key, the presets (engine/techno_presets.json) only when a track names one, free-running
patterns only when a pattern says `"free": true`.

  drums      `kick909`, `hat909`, `openhat909`, `tom909`, `rim909`: the TR-909's kick, hats, toms and rimshot, fitted
             to a recorded TR-909 (oramics/sampled "TR-909 Detroit", as engine/tr909.py) and checked against other
             909 recordings from Freesound (CC0 / CC BY, measured only); `conga`, `bongo`: hand drums with open, slap,
             mute and bass strokes (modal membranes), the open stroke fitted to Freesound recordings.
  rumble     a return `"type": "rumble"`: the kick into a long reverb (100% wet), then distortion, then a steep
             low-pass, mono, ducked on every hit of the key track (its events, not a level follower), its level set
             against the dry kick; a track's `"rumble": true | {...}` sets the return and the send up in one step.
             Fitted to recorded kick-and-rumble loops.

Each drum takes the module generator `instruments.RNG` at call time (as engine/tr909.py), so per-track seeds give each
track its own stream; the cymbal "ROM" of the hats and the rumble's reverb use fixed seeds of their own.
"""
import copy

import numpy as np
from scipy import signal

import instruments as I
from hand import note_to_midi, midi_to_hz

SR = I.SR
TWO_PI = 2 * np.pi


def _note_hz(s):
    return float(midi_to_hz(note_to_midi(s))) if isinstance(s, str) else float(midi_to_hz(s))


def _rng():
    return I.RNG


def _sos(kind, f, order=2):
    if kind == "band":
        lo, hi = f
        return signal.butter(order, [float(np.clip(lo, 10, SR * 0.44)), float(np.clip(hi, lo * 1.05, SR * 0.45))],
                             btype="band", fs=SR, output="sos")
    return signal.butter(order, float(np.clip(f, 10, SR * 0.45)), btype=kind, fs=SR, output="sos")


def _q(defaults, p):
    q = dict(defaults)
    q.update({k: v for k, v in p.items() if k in defaults})
    return q


def _fade_end(x, ms=5):
    k = min(len(x), I._n(ms / 1000))
    if k > 1:
        x[-k:] *= np.linspace(1, 0, k)
    return x


# ------------------------------------------------------------------ TR-909 kick
# The circuit (Roland TR-909 service notes; Gordon Reid, "Synth Secrets: practical bass drum synthesis", Sound On Sound
# 2002): a VCO whose triangle is shaped toward a sine, its pitch swept down by an envelope (fast, then a slower settle),
# a VCA with the DECAY knob; the ATTACK knob adds a short pulse and a burst of filtered noise (the click). Defaults fitted
# to the recorded TR-909 kick (examples/production/techno/fit909.py).
KICK909 = dict(tune=51.5, bend=2.62, bend_ms=3.74, bend2=0.69, bend2_ms=30.6, decay=0.143, hold=0.011, shape=0.86,
               attack=0.59, click_hz=3560.0, click_ms=2.38, noise=0.19, noise_ms=2.18, drive=0.0, length=0.9)


def kick909(p, vel, ps=0.0):
    """TR-909 kick: `tune` (52 Hz: where the pitch settles; or `note`), a fast pitch fall of `bend` (x tune above it) over
    `bend_ms` and a slower one of `bend2` over `bend2_ms`; amplitude held `hold` s then falling with `decay` s (the
    909's DECAY knob); `shape` (the triangle-to-sine shaper: 0 sine, 2 rounder triangle); `attack` 0-1 (the click:
    a pulse at `click_hz` lasting `click_ms` plus `noise` of `noise_ms`); `drive`; `length` s."""
    q = _q(KICK909, p)
    rng = _rng()
    f0 = (_note_hz(p["note"]) if "note" in p else float(q["tune"])) * 2 ** (ps / 12)
    dec = float(q["decay"])
    n = I._n(min(float(q["length"]), float(q["hold"]) + dec * 7 + 0.01))
    t = np.arange(n) / SR
    f = f0 * (1 + float(q["bend"]) * np.exp(-t / (float(q["bend_ms"]) / 1000))
              + float(q["bend2"]) * np.exp(-t / (float(q["bend2_ms"]) / 1000)))
    ph = TWO_PI * np.cumsum(f) / SR
    s = float(q["shape"])
    x = np.sin(ph)
    if s > 0:  # toward the 909's rounded triangle: odd harmonics in, peaks flattened
        tri = 2 / np.pi * np.arcsin(np.clip(np.sin(ph), -1, 1))
        x = (1 - min(s, 2) / 2) * x + (min(s, 2) / 2) * tri
    hold = float(q["hold"])
    env = np.where(t < hold, 1.0, np.exp(-(t - hold) / dec)) * np.clip(t / 0.0004, 0, 1)
    body = x * env
    a = float(q["attack"])
    if a > 0:  # the ATTACK knob
        cm = float(q["click_ms"]) / 1000
        pulse = np.sin(TWO_PI * float(q["click_hz"]) * t) * np.exp(-t / max(cm, 1e-4))
        nz = signal.sosfilt(_sos("band", (1200, 9000)), rng.standard_normal(n)) * np.exp(-t / (float(q["noise_ms"]) / 1000))
        body = body + a * (pulse * 0.6 + float(q["noise"]) * nz)
    y = I.soft(body.astype(np.float32), float(q["drive"]))
    return (_fade_end(y) * vel ** 1.1 * 0.95).astype(np.float32)


# ------------------------------------------------------------------ TR-909 hats (closed, open)
# In the hardware the hats are 6-bit samples of real cymbals in ROM, played through a VCA (the decay knobs) and the
# output filter. Here, as `ride909`: a metallic cymbal made of inharmonic partials and noise, normalised and quantized
# to `bits`, then the VCA and the filters. Defaults fitted to the recorded TR-909 hats.
HAT909 = dict(low=1.07, decay=0.0215, hold=0.0031, mid=0.69, high=1.05, top=0.23, noise=0.49, tilt=0.18, bits=6,
              hp=11800.0, lp=16000.0, body=0.77, body_hp=45.0, seed=9091)
OHAT909 = dict(low=2.13, decay=0.073, hold=0.042, mid=1.19, high=0.97, top=0.13, noise=0.58, tilt=0.8, bits=6, hp=4160.0,
               lp=16000.0, body=0.46, body_hp=46.0, seed=9092)
_HAT_CACHE = {}


def _hat_raw(q):
    key = tuple(sorted((k, float(v)) for k, v in q.items() if k in ("low", "mid", "high", "top", "noise", "tilt", "bits", "seed")))
    if key in _HAT_CACHE:
        return _HAT_CACHE[key]
    srng = np.random.default_rng(int(q["seed"]))
    n = I._n(1.2)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for lo, hi, k, amp, dec in ((300, 2500, 24, float(q.get("low", 0.0)), 0.12), (2500, 6000, 18, float(q["mid"]), 0.35), (6000, 11000, 36, float(q["high"]), 0.3),
                                (11000, 17000, 30, float(q["top"]), 0.22)):
        fr = np.exp(srng.uniform(np.log(lo), np.log(hi), k))
        if amp <= 0:
            continue
        a = srng.uniform(0.4, 1.0, k) * (fr / 8000) ** (2 * float(q["tilt"]) - 1)
        a = a / np.sqrt((a ** 2).sum()) * amp
        dc = dec * srng.uniform(0.5, 1.4, k)
        ph = srng.uniform(0, TWO_PI, k)
        for j in range(k):
            x += a[j] * np.sin(TWO_PI * fr[j] * t + ph[j]) * np.exp(-t / dc[j])
    nz = signal.sosfilt(_sos("band", (3000, 17000)), srng.standard_normal(n))
    x += nz / (np.sqrt(np.mean(nz[:SR // 10] ** 2)) + 1e-12) * float(q["noise"]) * 0.25 * np.exp(-t / 0.4)
    x *= np.clip(t / 0.0003, 0, 1)
    x /= np.abs(x).max()
    lv = 2 ** (int(q["bits"]) - 1)
    x = np.round(x * lv) / lv
    _HAT_CACHE[key] = x
    return x


def _hat(q, vel, ps):
    raw = _hat_raw(q)
    if ps:
        idx = np.arange(0, len(raw) - 1, 2 ** (ps / 12))
        raw = np.interp(idx, np.arange(len(raw)), raw)
    dec, hold = float(q["decay"]), float(q["hold"])
    n = min(len(raw), I._n(hold + dec * 8 + 0.01))
    t = np.arange(n) / SR
    x = raw[:n] * np.where(t < hold, 1.0, np.exp(-(t - hold) / dec))
    y = signal.sosfilt(_sos("high", float(q["hp"])), x)
    if float(q.get("body", 0)) > 0:  # the sample's full band (the 6-bit grain and the stick) under the filtered top
        y = y + float(q["body"]) * signal.sosfilt(_sos("high", float(q["body_hp"])), x)
    x = signal.sosfilt(_sos("low", min(float(q["lp"]), SR * 0.45)), y)
    if vel < 0.7:  # softer hits are darker
        x = signal.sosfilt(_sos("low", 5000 + 12000 * vel, 1), x)
    return (_fade_end(x) * vel * 0.9).astype(np.float32)


def hat909(p, vel, ps=0.0):
    """TR-909 closed hat: a 6-bit cymbal (`low` 0.3-2.5 kHz, `mid` 2.5-6 kHz, `high` 6-11 kHz, `top` 11-17 kHz partial levels, `noise`,
    `tilt` 0-1 brightness, `bits` 6; `seed` another cymbal) through the VCA (`hold` s, then `decay` s) and the output
    filters `hp`, `lp`, plus `body` of the sample's whole band above `body_hp` (the grain and the stick under the top). `ps` (rolls) shifts the playback rate like the 909's tune."""
    return _hat(_q(HAT909, p), vel, ps)


def openhat909(p, vel, ps=0.0):
    """TR-909 open hat: as `hat909` with its own sample and a longer VCA (`hold` 0.042 s, `decay` 0.073 s: the OH DECAY knob; 0.15-0.4
    for a long open hat; vary it per section with `auto`). Use `"choke_by": "<closed hat track>"` so the closed hat
    cuts it, as on the machine."""
    return _hat(_q(OHAT909, p), vel, ps)


# ------------------------------------------------------------------ TR-909 toms and rimshot
TOM909 = dict(tune=None, pitch="low", bend=0.63, bend_ms=30.7, decay=0.083, hold=0.0185, noise=0.3, noise_ms=15.4,
              noise_lp=5940.0, shape=0.65, drive=0.1)
TOM909_TUNE = {"low": 75.8, "mid": 93.0, "high": 114.3}


def tom909(p, vel, ps=0.0):
    """TR-909 tom: `pitch` "low" | "mid" | "high" (75.8, 93, 114.3 Hz: low and high fitted, mid between) or `tune` Hz (or `note`), a pitch fall of `bend`
    (x tune) over `bend_ms`, `decay` s after `hold`, a noise skin of `noise` lasting `noise_ms` low-passed at `noise_lp`,
    `shape` (sine to rounded triangle), `drive`."""
    q = _q(TOM909, p)
    rng = _rng()
    f0 = _note_hz(p["note"]) if "note" in p else float(q["tune"] or TOM909_TUNE.get(q["pitch"], 88.0))
    f0 *= 2 ** (ps / 12)
    dec = float(q["decay"])
    n = I._n(float(q["hold"]) + dec * 7 + 0.02)
    t = np.arange(n) / SR
    f = f0 * (1 + float(q["bend"]) * np.exp(-t / (float(q["bend_ms"]) / 1000)))
    ph = TWO_PI * np.cumsum(f) / SR + rng.random() * 0.2
    s = min(float(q["shape"]), 2.0)
    x = (1 - s / 2) * np.sin(ph) + (s / 2) * 2 / np.pi * np.arcsin(np.clip(np.sin(ph), -1, 1))
    hold = float(q["hold"])
    x *= np.where(t < hold, 1.0, np.exp(-(t - hold) / dec)) * np.clip(t / 0.0005, 0, 1)
    nz = signal.sosfilt(_sos("low", float(q["noise_lp"])), rng.standard_normal(n)) * np.exp(-t / (float(q["noise_ms"]) / 1000))
    x = x + float(q["noise"]) * nz
    y = I.soft(x.astype(np.float32), float(q["drive"]))
    return (_fade_end(y) * vel ** 1.1 * 0.9).astype(np.float32)


RIM909 = dict(f1=318.0, f2=789.0, f3=2017.0, l1=1.0, l2=0.35, l3=0.31, d1=0.0081, d2=0.0049, d3=0.0039, click=0.41,
              drive=1.57, hp=217.0)


def rim909(p, vel, ps=0.0):
    """TR-909 rimshot: three bridged-T resonators (`f1` `f2` `f3` Hz, levels `l1` `l2` `l3`, decays `d1` `d2` `d3` s)
    struck by one pulse, a `click` of noise, overdriven (`drive`; the 909's rim is famously gritty), high-passed `hp`."""
    q = _q(RIM909, p)
    rng = _rng()
    k = 2 ** (ps / 12)
    n = I._n(max(float(q["d1"]), float(q["d2"]), float(q["d3"])) * 8 + 0.01)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for i in "123":
        x += float(q["l" + i]) * np.sin(TWO_PI * float(q["f" + i]) * k * t) * np.exp(-t / float(q["d" + i]))
    x += float(q["click"]) * signal.sosfilt(_sos("high", 2000), rng.standard_normal(n)) * np.exp(-t / 0.0015)
    x *= np.clip(t / 0.0002, 0, 1)
    x = signal.sosfilt(_sos("high", float(q["hp"])), x)
    x = x / (np.abs(x).max() + 1e-12)
    y = I.soft(x.astype(np.float32), float(q["drive"]))
    return (_fade_end(y, 2) * vel * 0.9).astype(np.float32)


# ------------------------------------------------------------------ hand drums: conga, bongo
# A struck membrane as a few damped modes (the circular membrane's ratios, pulled toward harmony by the drum's air and
# shell as in real congas: Rossing, "The Science of Percussion Instruments", 2000, ch. 3), with a pitch that falls a
# little as the head's tension relaxes after the stroke, plus the hand's slap noise. Strokes (Sanabria; the standard
# conga technique): open (the tone rings), slap (a short, high crack), mute (the hand stays on the head: short, dull),
# bass (heel in the centre: low thump). The open stroke's defaults are fitted to recordings
# (examples/production/techno/fithand.py); the others are set from it by hand [H].
MEMBRANE = (1.0, 1.52, 1.98, 2.44, 2.9, 3.3)
CONGA = dict(tune=231.0, decay=0.064, modes=0.9, bright=0.41, bend=0.064, bend_ms=54.0, slap=0.63, slap_hz=5630.0,
             drive=0.35, stroke="open")
BONGO = dict(tune=480.0, decay=0.052, modes=0.78, bright=0.7, bend=0.1, bend_ms=5.5, slap=0.1, slap_hz=3790.0,
             drive=0.64, stroke="open")
STROKES = {"open": dict(dec=1.0, modes=1.0, slap=1.0, f=1.0, low=0.0),
           "slap": dict(dec=0.35, modes=1.6, slap=3.5, f=1.0, low=0.0),
           "mute": dict(dec=0.3, modes=0.5, slap=0.6, f=1.0, low=0.0),
           "bass": dict(dec=0.6, modes=0.3, slap=0.3, f=0.45, low=1.0)}


def _hand(q, vel, ps):
    rng = _rng()
    st = STROKES.get(q.get("stroke", "open"))
    if st is None:
        raise ValueError(f"hand drum stroke must be one of {', '.join(STROKES)}")
    f0 = float(q["tune"]) * 2 ** (ps / 12) * st["f"]
    dec = float(q["decay"]) * st["dec"]
    n = I._n(dec * 7 + 0.03)
    t = np.arange(n) / SR
    bend = 1 + float(q["bend"]) * np.exp(-t / (float(q["bend_ms"]) / 1000))
    x = np.zeros(n)
    m = float(q["modes"]) * st["modes"]
    for i, r in enumerate(MEMBRANE):
        a = 1.0 if i == 0 else m * (float(q["bright"]) ** (i - 1)) / (1 + 0.3 * i)
        d = dec / (1 + 0.8 * i)
        x += a * np.sin(TWO_PI * np.cumsum(f0 * r * bend) / SR + rng.random() * TWO_PI) * np.exp(-t / d)
    sl = float(q["slap"]) * st["slap"]
    if sl > 0:
        sh = float(q["slap_hz"])
        x += sl * signal.sosfilt(_sos("band", (sh * 0.4, min(sh * 3, 16000))), rng.standard_normal(n)) * np.exp(-t / 0.006)
    if st["low"]:
        x += st["low"] * np.sin(TWO_PI * f0 * 0.5 * t) * np.exp(-t / (dec * 0.8))
    x *= np.clip(t / 0.0004, 0, 1)
    x = x / (np.abs(x).max() + 1e-12)
    y = I.soft(x.astype(np.float32), float(q["drive"]))
    if vel < 0.6:
        y = signal.sosfilt(_sos("low", 2500 + 9000 * vel, 1), y).astype(np.float32)
    return (_fade_end(y) * vel ** 1.1 * 0.9).astype(np.float32)


def conga(p, vel, ps=0.0):
    """Conga: `stroke` "open" | "slap" | "mute" | "bass", `tune` Hz (231: a conga; about 300 a quinto, 180 a tumba; or
    `note`), `decay` s (the open tone), `modes` (level of the upper modes), `bright` (how fast they fall off), `bend` /
    `bend_ms` (the pitch falling as the head relaxes), `slap` (the hand's noise, at `slap_hz`), `drive`."""
    q = _q(CONGA, p)
    if "note" in p:
        q["tune"] = _note_hz(p["note"])
    return _hand(q, vel, ps)


def bongo(p, vel, ps=0.0):
    """Bongo: as `conga`, smaller and higher (`tune` 480 Hz: the macho; about 330 the hembra), shorter (`decay` 0.052)."""
    q = _q(BONGO, p)
    if "note" in p:
        q["tune"] = _note_hz(p["note"])
    return _hand(q, vel, ps)


DRUMS = dict(kick909=kick909, hat909=hat909, openhat909=openhat909, tom909=tom909, rim909=rim909, conga=conga,
             bongo=bongo)
GAIN = {"kick909": -1, "hat909": -12, "openhat909": -14, "tom909": -6, "rim909": -9, "conga": -7, "bongo": -8}


# ------------------------------------------------------------------ the rumble
# Every source builds it the same way (docs/TECHNO.md "Sound design"): the kick into a reverb, 100% wet (Futureproof:
# 3-5 s), then distortion, then a low-pass (MusicRadar 96.6 Hz; Bonedo about 250; Computer Music 800 at 48 dB/oct;
# Futureproof and MusicRadar 2023 150-200), mono, high-passed 20-30 Hz, sidechained to the dry kick so it ducks on every
# hit and swells between them; the chain about 8 dB under the dry kick (Bonedo). Defaults fitted to recorded
# kick-and-rumble loops (examples/production/techno/fitrumble.py): a short, hard-driven tail that is silent at each
# hit and swells back over the beat, low-passed near 390 Hz, 9.5 dB under the kick.
RUMBLE = dict(decay=0.67, predelay_ms=0.0, damp_hz=1800.0, drive_db=24.0, bias=0.15, lpf=390.0, slope=48, hpf=28.0,
              notch_hz=0.0, duck_db=60.0, attack_ms=2.0, release=1.43, curve=0.92, level_db=-9.5, seed=31)
# the low-pass by the sources (docs/TECHNO.md "Sound design", the rumble row): `tone` names one; "hard" is the fit
RUMBLE_LPF = {"sub": 96.6, "deep": 150.0, "warm": 250.0, "hard": 390.0, "grit": 800.0}
_IR_CACHE = {}


def _reverb_ir(decay, damp_hz, seed):
    """A mono reverb tail: exponentially decaying noise (T60 = `decay` s), its highs dying faster (a first-order
    low-pass at `damp_hz` on the noise and a second, time-varying darkening)."""
    key = (round(decay, 4), round(damp_hz, 1), int(seed))
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    srng = np.random.default_rng(int(seed))
    n = I._n(decay * 1.1)
    t = np.arange(n) / SR
    nz = srng.standard_normal(n)
    lo = signal.sosfilt(_sos("low", damp_hz * 0.25, 1), nz)
    hi = signal.sosfilt(_sos("low", damp_hz, 1), nz)
    w = np.exp(-t / (decay / 3.0))             # the highs leave first
    ir = (hi * w + lo * (1 - w) * 2.0) * np.exp(-t * 6.91 / decay)
    ir[:I._n(0.002)] *= np.linspace(0, 1, I._n(0.002))
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    _IR_CACHE[key] = ir
    return ir


def hit_duck(times, total_n, beat, q):
    """Gain (n,) that drops to -`duck_db` at each hit (`attack_ms` early) and swells back over `release` beats with the
    exponent `curve` (>1: stays down longer, then swells; the pump)."""
    g = np.ones(total_n)
    floor = 10 ** (-float(q["duck_db"]) / 20)
    rel = max(float(q["release"]) * beat, 0.01)
    k = np.arange(int(rel * SR) + 1) / SR
    rise = floor + (1 - floor) * (k / rel) ** float(q["curve"])
    att = int(float(q["attack_ms"]) / 1000 * SR)
    for tt in sorted(times):
        i = int(tt * SR) - att
        if i >= total_n or i + len(rise) + att <= 0:
            continue
        a0 = max(i, 0)
        if att > 0:
            seg = np.linspace(1, floor, att)
            lo = max(0, -i)
            g[a0:i + att] = np.minimum(g[a0:i + att], seg[lo:lo + max(0, min(i + att, total_n) - a0)])
        j = i + att
        if j < total_n:
            lo = max(0, -j)
            m = min(len(rise) - lo, total_n - max(j, 0))
            if m > 0:
                g[max(j, 0):max(j, 0) + m] = np.minimum(g[max(j, 0):max(j, 0) + m], rise[lo:lo + m])
    return g


def rumble(x, cfg, beat, times):
    """The rumble return: `x` (2, n) the summed sends (the kick), `times` the key track's hit times (s). cfg: `decay` s
    (0.67: the reverb's T60), `predelay_ms`, `damp_hz` (1800); `drive_db` (24) and `bias` (0.15: asymmetry, even
    harmonics) of the distortion after the reverb; `lpf` Hz (390) or a `tone`: "sub" 96.6 (MusicRadar), "deep" 150
    (Futureproof, MusicRadar 2023), "warm" 250 (Bonedo), "hard" 390 (the fit), "grit" 800 (Computer Music); `slope`
    dB/oct (48; 12-96), `hpf` (28 Hz), `notch_hz` (0 = off; 135 is MusicRadar's boxy note); the duck on each hit:
    `duck_db` (60: silent at the hit), `attack_ms` (2), `release` (1.43 beats: the swell back), `curve` (0.92; above 1
    it stays down longer, then swells); `level_db` (-9.5: the rumble's RMS against the dry kick's while both play).
    Defaults fitted to the recorded loops (examples/production/techno/README.md). Mono out."""
    q = _q(RUMBLE, cfg)
    if "lpf" not in cfg and cfg.get("tone"):
        if cfg["tone"] not in RUMBLE_LPF:
            raise ValueError(f"rumble tone must be one of {', '.join(RUMBLE_LPF)}")
        q["lpf"] = RUMBLE_LPF[cfg["tone"]]
    m = x.mean(0).astype(np.float64)
    if not np.any(m):
        return np.zeros_like(x)
    pd = int(float(q["predelay_ms"]) / 1000 * SR)
    if pd > 0:
        m = np.concatenate([np.zeros(pd), m[:-pd]])
    ir = _reverb_ir(float(q["decay"]), float(q["damp_hz"]), int(q["seed"]))
    wet = signal.oaconvolve(m, ir)[:len(m)]
    wet /= np.abs(wet).max() + 1e-12
    g = 10 ** (float(q["drive_db"]) / 20)
    b = float(q["bias"])
    wet = (np.tanh(g * wet + b) - np.tanh(b)) / (1 + abs(np.tanh(b)))
    order = int(np.clip(round(float(q["slope"]) / 6), 1, 16))
    sos = signal.butter(order, float(q["lpf"]), btype="low", fs=SR, output="sos")
    wet = signal.sosfiltfilt(sos, wet) if order > 8 else signal.sosfilt(sos, wet)
    if float(q["hpf"]) > 0:
        wet = signal.sosfilt(_sos("high", float(q["hpf"]), 2), wet)
    if float(q.get("notch_hz") or 0) > 0:
        bb, aa = signal.iirnotch(float(q["notch_hz"]), 4.0, fs=SR)
        wet = signal.lfilter(bb, aa, wet)
    wet *= hit_duck(times, len(wet), beat, q)
    act = np.abs(m) > np.abs(m).max() * 1e-3
    if act.any():
        a, z = np.argmax(act), len(act) - np.argmax(act[::-1])
        r_in = np.sqrt(np.mean(m[a:z] ** 2))
        r_out = np.sqrt(np.mean(wet[a:z] ** 2)) + 1e-12
        wet *= r_in / r_out * 10 ** (float(q["level_db"]) / 20)
    return np.stack([wet, wet]).astype(np.float32)


def apply_rumble(P):
    """A track with `"rumble": true` (or a dict of the return's settings, plus `"name"`, default "rumble") gets a
    `rumble` return keyed by its own hits and a send of 1.0 to it; P itself when no track asks."""
    want = [(k, tr) for k, tr in P.get("tracks", {}).items() if isinstance(tr, dict) and tr.get("rumble") not in (None, False)]
    if not want:
        return P
    P = dict(P, tracks=dict(P["tracks"]), mix=copy.deepcopy(P.get("mix") or {}))
    rets = P["mix"].setdefault("returns", {})
    for k, tr in want:
        cfg = dict(tr["rumble"]) if isinstance(tr["rumble"], dict) else {}
        name = cfg.pop("name", "rumble")
        if name in rets and rets[name].get("type") != "rumble":
            raise ValueError(f'track "{k}": "rumble" would replace the return "{name}"; give it another "name"')
        rets[name] = dict(dict(type="rumble", key=k), **cfg)
        tr = dict(tr)
        tr["sends"] = dict(tr.get("sends") or {}, **{name: 1.0})
        P["tracks"][k] = tr
    return P


# ------------------------------------------------------------------ free-running patterns
def free_phase(pat, bar_i):
    """Bars into a free-running pattern's cycle at song bar `bar_i` (0-based): the pattern runs on the song's clock, as
    if it had played from bar 1, so a 3-step or 5-step loop keeps drifting against the 4/4 across sections."""
    pb = float(pat.get("bars", 1))
    if pb <= 0:
        return 0.0
    ph = round(bar_i % pb, 9)
    return 0.0 if abs(ph - pb) < 1e-9 else ph
