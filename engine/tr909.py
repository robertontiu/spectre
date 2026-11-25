"""TR-909-style snare, clap and ride (docs/TRANCE.md G 7 and I 4; docs/MANUAL.md "909 drums"). Additive: used only
when a track names `snare909`, `clap909` or `ride909`; they draw from the module generator `instruments.RNG` at call
time (as engine/synth.py does), so per-track seeds give each track its own stream.

The circuits (Roland TR-909 service notes; Gordon Reid, "Synth Secrets", Sound On Sound 2002, "Practical snare drum
synthesis" and "Synthesizing claps"; the KVR thread on the 808/909 clap):
  - snare: two oscillators (a body near 180-190 Hz and a second one near twice that) whose pitch falls in the first
    ~20 ms, plus white noise through a high-pass ("snappy" = its level, "tone" = its decay), each with its own
    envelope;
  - clap: one noise source through a band-pass, gated by an envelope generator that fires a few sawtooth pulses about
    10 ms apart (the "several hands"), then a longer decaying tail through its own filter (the "reverb");
  - ride (and crash): not synthesized in the hardware but a 6-bit sample of a real cymbal in ROM, played through a
    VCA whose decay is the "ride decay" knob. Here the cymbal is made of inharmonic partials and noise, normalised
    and quantized to 6 bits (so its grain, a fixed floor under the decaying cymbal, is the 909's), then shaped by the
    VCA and the output filter.
The defaults are fitted to a recorded TR-909 (oramics/sampled, "TR-909 Detroit": measured only, never stored in the
repo or used in a track) by 1/3-octave spectrum and band envelopes; the fit and its numbers are in docs/MANUAL.md
"909 drums" and examples/production/909/ (build909.py)."""
import numpy as np
from scipy import signal

import instruments as I

SR = I.SR
TWO_PI = 2 * np.pi


def _rng():
    return I.RNG


def _sos_hp(f, order=2):
    return signal.butter(order, float(np.clip(f, 20, SR * 0.45)), btype="high", fs=SR, output="sos")


def _sos_lp(f, order=2):
    return signal.butter(order, float(np.clip(f, 20, SR * 0.45)), btype="low", fs=SR, output="sos")


# fitted defaults (examples/production/909/build909.py "fit"; [M] against the reference, see docs/MANUAL.md)
SNARE909 = dict(tune=181.0, bend=1.12, bend_ms=7.0, ratio2=1.97, level2=0.22, tone_decay=0.0196, body=1.0,
                snappy=0.34, noise_decay=0.0433, noise_hp=1990.0, noise_lp=8760.0, drive=0.15)
CLAP909 = dict(spacing_ms=10.7, bursts=4, burst_decay=0.0026, lo=775.0, hi=9800.0, tail=0.55, tail_decay=0.0685,
               tail_lo=440.0, tail_hi=2500.0, drive=0.0)
RIDE909 = dict(decay=0.28, low=0.044, mid=0.07, bell=0.116, tilt=0.85, noise=0.25, bits=6, lp=16000.0, hp=50.0, seed=909)


def snare909(p, vel, ps=0.0):
    """TR-909 snare: `tune` (181 Hz) body oscillator with a pitch fall of `bend` (1.12 = from 2.12 x tune) over
    `bend_ms` (7), a second oscillator at `ratio2` (1.97) x tune at `level2` (0.22), their decay `tone_decay` s
    (0.0196) and level `body` (1); noise: `snappy` 0-1 (0.34; its level), `noise_decay` s (0.043; the 909's "tone"
    knob), band `noise_hp` (1990 Hz, first order) to `noise_lp` (8760 Hz); `drive` (0.15)."""
    q = dict(SNARE909)
    q.update({k: v for k, v in p.items() if k in SNARE909})
    rng = _rng()
    f1 = float(q["tune"]) * 2 ** (ps / 12)
    nd = float(q["noise_decay"])
    n = I._n(max(nd, float(q["tone_decay"])) * 7 + 0.02)
    t = np.arange(n) / SR
    fb = f1 * (1 + float(q["bend"]) * np.exp(-t / (float(q["bend_ms"]) / 1000)))
    ph = TWO_PI * np.cumsum(fb) / SR + rng.random() * 0.3
    tone = np.sin(ph) + float(q["level2"]) * np.sin(float(q["ratio2"]) * ph + rng.random() * TWO_PI)
    tone *= np.exp(-t / float(q["tone_decay"])) * float(q["body"])
    nz = rng.standard_normal(n)
    nz = signal.sosfilt(_sos_lp(float(q["noise_lp"])), signal.sosfilt(_sos_hp(float(q["noise_hp"]), 1), nz))
    nz *= np.exp(-t / nd) * float(q["snappy"]) * 1.6
    x = (tone * 0.55 + nz) * np.clip(t / 0.0004, 0, 1)
    x = I.soft(x.astype(np.float32), float(q["drive"]))
    if vel < 0.6:  # softer hits are darker
        x = signal.sosfilt(_sos_lp(3000 + 9000 * vel, 1), x)
    return (x * vel ** 1.1 * 0.9).astype(np.float32)


def clap909(p, vel, ps=0.0):
    """TR-909 clap: `bursts` (4) noise pulses `spacing_ms` (10.7) apart, each a sawtooth decay of `burst_decay` s
    (0.0026), band-passed `lo` (775 Hz) to `hi` (9800 Hz); then the tail ("reverb"): level `tail` (0.55), decay
    `tail_decay` s (0.0685), band `tail_lo` (440) to `tail_hi` (2500 Hz), starting with the last burst; `drive`."""
    q = dict(CLAP909)
    q.update({k: v for k, v in p.items() if k in CLAP909})
    rng = _rng()
    k = max(1, int(q["bursts"]))
    sp = float(q["spacing_ms"]) / 1000
    td = float(q["tail_decay"])
    n = I._n(sp * k + td * 7 + 0.02)
    t = np.arange(n) / SR
    sc = 2 ** (ps / 12)
    env = np.zeros(n)
    for i in range(k):
        t0 = i * sp * (1 + 0.04 * (rng.random() * 2 - 1))
        m = t >= t0
        env[m] += np.exp(-(t[m] - t0) / float(q["burst_decay"])) * (1.0 if i < k - 1 else 1.0)
    burst = signal.sosfilt(signal.butter(2, [float(q["lo"]) * sc, min(float(q["hi"]) * sc, SR * 0.45)], btype="band",
                                         fs=SR, output="sos"), rng.standard_normal(n)) * env
    t_last = (k - 1) * sp
    m = t >= t_last
    tenv = np.zeros(n)
    tenv[m] = np.exp(-(t[m] - t_last) / td)
    tail = signal.sosfilt(signal.butter(2, [float(q["tail_lo"]) * sc, float(q["tail_hi"]) * sc], btype="band", fs=SR,
                                        output="sos"), rng.standard_normal(n)) * tenv * float(q["tail"])
    x = (burst + tail * 1.8) * np.clip(t / 0.0003, 0, 1)
    x = I.soft(x.astype(np.float32), float(q["drive"]))
    return (x * vel * 1.1).astype(np.float32)


_RIDE_CACHE = {}


def _ride_raw(q):
    """The cymbal 'in ROM': partials and noise with its natural decay, normalised and quantized to `bits`."""
    key = tuple(sorted((k, float(v)) for k, v in q.items() if k not in ("decay", "lp", "hp")))
    if key in _RIDE_CACHE:
        return _RIDE_CACHE[key]
    srng = np.random.default_rng(int(q["seed"]))
    n = I._n(1.6)
    t = np.arange(n) / SR
    x = np.zeros(n)
    # low cluster (the cymbal's lowest modes, 400-600 Hz), the bell (1.3-1.6 kHz), the wash (2.5-15 kHz)
    groups = [(380, 620, 6, float(q["low"]), 0.9), (650, 2500, 24, float(q["mid"]), 0.7),
              (1300, 1650, 6, float(q["bell"]), 0.8), (2500, 15000, 90, 1.0, 0.55)]
    for lo, hi, k, amp, dec in groups:
        fr = np.exp(srng.uniform(np.log(lo), np.log(hi), k))
        a = srng.uniform(0.4, 1.0, k) * (fr / 4000) ** (2 * float(q["tilt"]) - 1) if lo >= 2500 else \
            srng.uniform(0.5, 1.0, k)
        a = a / np.sqrt((a ** 2).sum()) * amp
        dc = dec * srng.uniform(0.6, 1.3, k) * (fr / 3000) ** -0.25
        ph = srng.uniform(0, TWO_PI, k)
        for j in range(k):
            x += a[j] * np.sin(TWO_PI * fr[j] * t + ph[j]) * np.exp(-t / dc[j])
    nz = signal.sosfilt(signal.butter(2, [3000, 16000], btype="band", fs=SR, output="sos"), srng.standard_normal(n))
    x += nz * float(q["noise"]) * 0.25 * np.exp(-t / 0.45)
    x *= np.clip(t / 0.0005, 0, 1)
    x /= np.abs(x).max()
    lv = 2 ** (int(q["bits"]) - 1)
    x = np.round(x * lv) / lv            # the 6-bit ROM
    _RIDE_CACHE[key] = x
    return x


def ride909(p, vel, ps=0.0):
    """TR-909 ride: a cymbal sample made of partials and noise (`low` 0.044, `mid` 0.07, `bell` 0.116: the levels of
    the lowest modes, the 0.65-2.5 kHz modes and the bell; `tilt` 0-1 0.85: the wash's brightness; `noise` 0.25),
    quantized to `bits` (6, as the 909's ROM; 8 for a cleaner one), through the VCA (`decay` s, 0.28: the time
    constant of the ride decay knob) and the output filters `hp` (50 Hz) and `lp` (16000 Hz); `seed` another cymbal. `ps` (rolls) shifts the playback rate as the
    909's tune does."""
    q = dict(RIDE909)
    q.update({k: v for k, v in p.items() if k in RIDE909})
    raw = _ride_raw(q)
    if ps:
        r = 2 ** (ps / 12)
        idx = np.arange(0, len(raw) - 1, r)
        raw = np.interp(idx, np.arange(len(raw)), raw)
    n = min(len(raw), I._n(float(q["decay"]) * 9 + 0.05))
    t = np.arange(n) / SR
    x = raw[:n] * np.exp(-t / float(q["decay"]))
    fo = min(I._n(0.01), n)
    x[-fo:] *= np.linspace(1, 0, fo)
    x = signal.sosfilt(_sos_lp(float(q["lp"])), signal.sosfilt(_sos_hp(float(q["hp"])), x))
    if vel < 0.7:
        x = signal.sosfilt(_sos_lp(5000 + 12000 * vel, 1), x)
    return (x * vel * 0.9).astype(np.float32)
