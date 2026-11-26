"""chamber: the struck and bowed colours of the chamber score, each modelled on measured recordings.

Added 2026-11-24 for the chamber-score session (docs/CHAMBER_SCORE.md). Every value here was measured from
reference recordings (University of Iowa MIS, Versilian VSCO-2-CE and VCSL, a celesta pack on Freesound; the
measurements and their sources are in docs/MANUAL.md "Chamber score instruments"). The references are only analysed,
never shipped. Each sound draws from its own seeded generator, never from the shared module RNG of instruments.py,
so projects that don't use these instruments render exactly as before.

  celesta        struck steel plates over wooden resonators: an almost pure fundamental that rings 4-6 s, a soft
                 felt-hammer onset, the plate's own overtones 35-45 dB down and gone within a second, a damper
  glockenspiel   steel bars struck by a mallet: strongly inharmonic modes at the ratios measured per register,
                 a long-ringing fundamental (T60 5-11 s), `hardness` from yarn to brass
  vibraphone     aluminium bars over tube resonators, a motor that turns discs in the tubes (tremolo), a pedal
  cello, viola   the violin's bowed waveguide string (engine/violin.py) with a cello or viola body fitted to
                 recordings, in their registers
  strings_section several bowed players per line, each its own string, body, intonation, vibrato and timing, spread
                 across the stage; legato swells and pizzicato
"""
import numpy as np
from scipy import signal

SR = 44100


def _tt(n):
    return np.arange(n) / SR


def _nn(sec):
    return int(sec * SR)


def _rng(*key):
    """A deterministic generator per sound (never the shared module RNG)."""
    h = 0
    for k in key:
        h = (h * 1000003 + int(round(float(k) * 1000))) % (2 ** 32)
    return np.random.default_rng(h)


def _t60_env(t, t60):
    return np.exp(-6.907755 * t / max(t60, 1e-3))


def _end_fade(x, ms=40.0):
    k = min(len(x), _nn(ms / 1000))
    if k > 1:
        x[-k:] *= np.cos(np.linspace(0, np.pi / 2, k)) ** 2
    return x


def _lp(x, f, order=2):
    f = min(f, SR * 0.45)
    return signal.sosfilt(signal.butter(order, f, fs=SR, output="sos"), x)


def _bp(x, lo, hi, order=2):
    hi = min(hi, SR * 0.45)
    return signal.sosfilt(signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


# ---------------------------------------------------------------- celesta
# Measured on 12 notes of a celesta (pjcohen, Freesound pack 23108, A#2-F#6, CC BY 4.0): after 30 ms the fundamental
# stands 35-55 dB over everything else; its T60 is about 5.4 s x (349 Hz / f)^0.2 (6.2-7.6 s low, 3.6-4.5 s at the top);
# the plate's first overtone at 2.71-2.76 x f1 and the second at 6.2 (low notes) to 5.36 (F5 and up), each about
# 40 dB down at 30 ms with T60 0.6-0.9 s; low notes add modes near 7.1-7.7 and 14.5-14.85; the 2nd and 3rd harmonics
# sit about 50 dB down; the onset rises over 3-15 ms (the felt hammer and the resonator), longer for low notes; above
# 8 kHz there is almost nothing (-70 to -90 dB of the total in the first second).


def celesta(p, f, vel, dur):
    hammer = float(p.get("hammer", 0.5))
    pedal = bool(p.get("pedal", False))
    rel = float(p.get("release", 0.15))
    t1 = 5.4 * (349.0 / f) ** 0.2 * float(p.get("decay", 1.0))
    ring = min(t1, float(p.get("ring", 8.0)))
    n = _nn(ring if pedal else min(dur + rel, ring))
    n = max(n, _nn(0.05))
    t = _tt(n)
    rng = _rng(f, vel, 11)
    tau_r = float(np.clip(9.0 * (349.0 / f) ** 0.25, 4.0, 14.0)) / 1000 * (1.3 - 0.6 * hammer)
    rise = (1 - np.exp(-t / tau_r)) ** 2  # measured: about -20 dB at 2 ms, -9 dB at 10 ms, full by 20-40 ms
    x = np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * _t60_env(t, t1)
    # weak 2nd and 3rd harmonics (resonator and plate nonlinearity)
    hi = float(np.clip(np.log2(f / 700.0), 0, 1))  # the top octave carries more 3rd harmonic (measured -37 dB at F#6)
    for k, lv in ((2, -50), (3, -55 + 15 * hi)):
        if k * f < SR * 0.45:
            x += 10 ** (lv / 20) * np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28)) * _t60_env(t, 0.7 * t1)
    # the plate's own modes: about 40 dB down after 30 ms, much stronger in the first few ms
    lo = float(np.clip((np.log2(f) - np.log2(250)) / (np.log2(700) - np.log2(250)), 0, 1))
    modes = [(2.74, -40, 0.8), (6.2 + (5.36 - 6.2) * lo, -39, 0.75)]
    if f < 320:
        modes += [(7.4, -40, 0.8), (14.7, -32, 0.5)]
    hb = 10 ** ((hammer - 0.5) * 12 / 20)  # a harder hammer lifts the overtones
    for r, lv, t60 in modes:
        fr = r * f
        if fr > SR * 0.45:
            continue
        g = 10 ** (lv / 20) * hb * (0.6 + 0.6 * vel)
        burst = 1 + 14 * np.exp(-t / 0.004)  # the strike: the overtones flare for a few ms
        x += g * burst * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * _t60_env(t, t60)
    # the plate's dense high modes: weak, 2-8 kHz, gone in a few tenths of a second (measured 2-4 kHz about -30 dB and
    # 4-8 kHz about -50 dB under the fundamental in the first 100 ms, T60 0.3-0.8 s)
    for j in range(12):
        fr = float(np.exp(rng.uniform(np.log(2000), np.log(8000))))
        if fr < 1.6 * f or fr > SR * 0.45:
            continue
        lv = -42 - 14 * (np.log2(fr / 2000) / 2) + (hammer - 0.5) * 10
        x += 10 ** (lv / 20) * (1 + 3 * np.exp(-t / 0.006)) * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) \
            * _t60_env(t, rng.uniform(0.3, 0.8))
    # the felt hammer: a short soft knock
    k = min(n, _nn(0.03))
    nz = rng.standard_normal(k)
    nz = _lp(nz, 1500 + 4500 * hammer * vel)
    x[:k] += nz * np.exp(-t[:k] / 0.0015) * 0.05 * (0.5 + hammer)
    # the action's knock (key, hammer shank, plate mount): a dull noisy smear under 2-3 kHz for the first 0.2 s, seen
    # in every recorded note about 30 dB under the fundamental
    k = min(n, _nn(0.25))
    kn = _bp(rng.standard_normal(k), 150, 2500)
    x[:k] += kn * np.exp(-t[:k] / 0.04) * 0.035 * (0.6 + 0.8 * vel)
    x *= rise
    if not pedal:
        h = _nn(dur)
        if h < n:
            x[h:] *= np.exp(-np.arange(n - h) / _nn(rel / 4))
    x = _end_fade(x, 30)
    return (x * vel ** 1.2 * 0.5).astype(np.float32)


# ---------------------------------------------------------------- glockenspiel
# Measured on the University of Iowa MIS orchestral bells (a glockenspiel, ff, plastic and brass mallets, G5-D7) and
# checked against Versilian's glockenspiel (VSCO-2-CE / VCSL, CC0). Per register: (ratio to f1, level at 30 ms with a
# plastic mallet in dB re f1, level with a brass mallet, T60 s). The fundamental rings 8-12 s (Iowa) / 4-9 s
# (Versilian, shorter at the top).
GLOCK_TABLE = [
    (788.0, 7.9, [(3.20, -52, -18, 0.38), (4.20, -41, -40, 4.0), (6.65, -17, -7, 0.50), (9.39, -13, -36, 1.17),
                  (10.51, -49, -13, 0.41), (14.06, -51, -29, 0.95), (15.00, -26, -7, 0.86)]),
    (1055.0, 9.3, [(3.12, -18, -18, 0.78), (3.39, -35, -58, 1.5), (6.22, -18, -14, 0.18), (8.05, -18, -28, 1.06),
                   (9.71, -25, -8, 0.38), (14.03, -19, -3, 0.91)]),
    (1581.0, 10.0, [(3.01, -17, -14, 0.70), (3.48, -44, -32, 2.3), (5.81, -12, 2, 0.40), (6.42, -34, -13, 1.15),
                    (9.07, -41, -49, 0.25)]),
    (2116.0, 8.9, [(2.53, -35, -30, 0.48), (2.92, -26, -31, 0.43), (3.29, -35, -34, 0.50), (5.42, -27, -7, 0.70),
                   (5.61, -42, -12, 0.22), (8.65, -49, -44, 0.57)]),
]


def _glock_soft(fm):
    """How much a mallet's hardness moves a mode at fm Hz (dB per unit of hardness away from plastic), fitted to the
    brass-minus-plastic differences of the Iowa bells (+4 dB at 2.5 kHz, +12-18 dB at 5-12 kHz)."""
    return 20.0 * (1 - np.exp(-max(0.0, fm - 1500.0) / 4000.0))


def glockenspiel(p, f, vel, dur):
    hard = float(np.clip(p.get("hardness", 0.5), 0.0, 1.0))
    dec = float(p.get("decay", 1.0))
    rng = _rng(f, vel, 23)
    i = int(np.argmin([abs(np.log2(f / a[0])) for a in GLOCK_TABLE]))
    f_anchor, t1, modes = GLOCK_TABLE[i]
    t1 = t1 * min(1.0, (2116.0 / f) ** 0.35 if f > 2116 else 1.0) * dec
    ring = min(t1, float(p.get("ring", 7.0)))
    damped = bool(p.get("damped", False))
    n = _nn(min(dur + 0.08, ring) if damped else ring)
    n = max(n, _nn(0.05))
    t = _tt(n)
    x = np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * _t60_env(t, t1)
    x *= 1 - np.exp(-t / 0.0004)
    v = 0.5 + 0.5 * vel  # a softer stroke is also a duller one
    for r, lp_, lb, t60 in modes:
        fm = r * f
        if fm > SR * 0.44:
            continue
        if hard >= 0.5:
            lv = lp_ + (hard - 0.5) * 2 * (lb - lp_) * 0.5 + (hard - 0.5) * 2 * 0.5 * _glock_soft(fm)
        else:
            lv = lp_ - (0.5 - hard) * 2 * _glock_soft(fm)
        lv += (v - 1) * 0.5 * _glock_soft(fm)
        lv0 = lv + 60 * 0.03 / (t60 * dec)  # level at the strike (the table is at 30 ms)
        x += 10 ** (lv0 / 20) * np.sin(2 * np.pi * fm * t + rng.uniform(0, 6.28)) * _t60_env(t, t60 * dec)
    # the mallet's contact tick
    k = min(n, _nn(0.01))
    nz = _bp(rng.standard_normal(k), 1500, 3000 + 9000 * hard)
    x[:k] += nz * np.exp(-t[:k] / 0.0007) * 0.06 * hard * vel
    if damped:
        h = _nn(dur)
        if h < n:
            x[h:] *= np.exp(-np.arange(n - h) / _nn(0.02))
    x = _end_fade(x, 60)
    return (x * vel ** 1.1 * 0.35).astype(np.float32)


# ---------------------------------------------------------------- bowed strings: cello, viola, a section
# Bodies measured from the University of Iowa MIS (2012 recordings, arco ff, non-vibrato; 16 cello notes C2-D5,
# 14 viola notes C3-C6): each recorded note's harmonic levels divided by those of the bare waveguide string
# (engine/violin.py) at the same pitch, each note normalised to its total, all notes pooled and smoothed over 1/6 octave.
# Values are dB at 63 Hz x 2^(k/6), k = 0..48 (63 Hz to 16 kHz), 0 dB at 1 kHz. Above 8 kHz the recordings are bow
# noise and air more than string, so the curve is held at its 8 kHz value there. Refined in two closed-loop passes
# (render the model at every reference pitch, measure the same way, fold the residual back): the model now sits
# 0.87 dB (cello) and 0.74 dB (viola) from the recordings on average, 1/6-octave smoothed, 100 Hz-8 kHz.
CELLO_BODY = [-19.3, -11.6, -3.5, 0.2, 2.1, 3.4, 4.3, 6.6, 10.2, 11.5, 9.3, 4.3, 0.2, 1.2, 2.9, 1.5, 0.5, 1.6, 0.9,
              -0.3, 0.9, 0.6, -3.0, -4.4, -0.1, 2.7, 1.4, -1.4, -3.0, -3.1, -3.2, -1.2, 2.9, 4.2, 0.8, -5.8, -10.6,
              -9.4, -7.5, -4.7, -7.3, -5.6, -3.4, -1.6, -0.5, -0.9, -2.1, -3.3, -3.9]
VIOLA_BODY = [-31.1, -31.1, -31.1, -31.1, -31.1, -22.7, -26.5, -15.3, -6.1, -1.4, 0.7, 2.8, 3.3, 1.9, 0.3, 2.2, 6.9,
              10.6, 10.2, 7.4, 6.9, 7.9, 6.0, -1.3, -6.8, -2.2, 4.5, 9.2, 10.4, 8.0, 5.4, 4.1, 4.3, 3.4, 0.9, -1.3, 0.8,
              7.0, 10.4, 6.5, -1.6, -3.5, -1.1, 4.7, 8.9, 10.2, 9.7, 9.6, 9.9]
# The double bass (2026-11-26, the cinematic strand), by the same method: 13 Iowa MIS notes (arco ff, E1-D3), three
# closed-loop passes; the model sits 0.40 dB from the recordings on average (1/6-octave smoothed, 100 Hz-8 kHz).
# examples/production/cinematic/fit_bass.py. The bare waveguide is thin under 200 Hz next to a bass, hence the
# large low-end values. Pizzicato T60 hand-tuned [H] (no Iowa bass pizz in hand): 3 s at 80 Hz.
BASS_BODY = [27.7, 27.5, 26.9, 26.1, 26.9, 28.2, 25.9, 21.3, 20.3, 25.7, 23.9, 10.2, 3.2, 2.5, 9.1, 16.0, 15.7, 15.9, 8.7,
             3.8, 2.6, 5.3, 9.2, -0.6, 0.0, 13.5, 11.4, 6.7, 4.8, 1.8, 2.9, -3.1, -8.1, -4.1, -9.4, -16.1, -11.8, -12.0,
             -16.5, -13.9, -10.3, -9.0, -4.2, -4.2, -4.2, -4.2, -4.2, -4.2, -4.2]
STRING_KIND = {
    # body table, lowest mode of the modal layer, DC-block / radiation high-pass, top roll-off, pizzicato T60 =
    # a * (f_ref / f)^b s (fitted to Iowa pizz ff: cello C2 3.0, G2 3.1, D3 1.8, A3 2.2, E4 1.4 s; viola C3 4.5,
    # G3 1.25, D4 1.05, A4 0.44, E5 1.08 s), lowest note
    "cello": dict(table=CELLO_BODY, lo=60.0, hpf=40.0, lpf=11000.0, pz=(2.2, 150.0, 0.5), low=36),
    "viola": dict(table=VIOLA_BODY, lo=110.0, hpf=90.0, lpf=13000.0, pz=(1.1, 300.0, 0.7), low=48),
    "bass": dict(table=BASS_BODY, lo=40.0, hpf=30.0, lpf=9000.0, pz=(3.0, 80.0, 0.5), low=28),
}
# classical vibrato, measured on Versilian's solo violin (VSCO-2-CE "Arco Vib", 6 notes: 4.3-7.1 Hz, median 5.2;
# +-5 to +-17 cents) and string sections (16 notes: 5.4 Hz, +-10 cents as heard through the section)
CLASSICAL = dict(vibrato=0.12, vib_rate=5.4, vib_delay=0.18, vib_grow=0.2, intonation=0.4, bow_noise=0.3, ring=0.6)
_BODIES = {}


def _minphase(mag_db, n):
    """Minimum-phase FIR (length n) from a magnitude response in dB on an rfft grid of size 2*(len-1)."""
    N = 2 * (len(mag_db) - 1)
    logm = np.log(10 ** (mag_db / 20))
    c = np.fft.irfft(logm, N)
    w = np.zeros(N)
    w[0] = 1
    w[1:N // 2] = 2
    w[N // 2] = 1
    h = np.fft.irfft(np.exp(np.fft.rfft(c * w)), N)[:n]
    fade = max(8, n // 8)
    h[-fade:] *= np.cos(np.linspace(0, np.pi / 2, fade)) ** 2
    return h


def _smooth_oct(fgrid, db, frac=1 / 3):
    out = np.empty_like(db)
    p = 10 ** (db / 10)
    lf = np.log2(np.maximum(fgrid, 1.0))
    cs = np.cumsum(p)
    for i in range(len(fgrid)):
        lo = np.searchsorted(lf, lf[i] - frac / 2)
        hi = np.searchsorted(lf, lf[i] + frac / 2)
        hi = max(hi, lo + 1)
        out[i] = 10 * np.log10((cs[hi - 1] - (cs[lo - 1] if lo > 0 else 0)) / (hi - lo) + 1e-30)
    return out


def _table_db(table, f):
    cs = 63.0 * 2 ** (np.arange(len(table)) / 6)
    tab = np.array(table, dtype=float)
    k8 = int(np.argmin(abs(cs - 8000)))
    tab[k8:] = np.minimum(tab[k8:], tab[k8])
    lf = np.log2(np.maximum(f, 1.0))
    v = np.interp(lf, np.log2(cs), tab)
    below = f < cs[0]
    v[below] = tab[0] - 12 * (np.log2(cs[0]) - lf[below])
    return v


def string_body_ir(kind, variant=0):
    """A body: dense modes (for the vibrato's shimmer through the body's peaks) shaped by a minimum-phase filter so
    that its 1/3-octave response follows the measured curve."""
    key = (kind, int(variant))
    if key in _BODIES:
        return _BODIES[key]
    spec = STRING_KIND[kind]
    rng = np.random.default_rng(700 + 31 * int(variant) + {"cello": 0, "viola": 5000}.get(kind, 9000))
    n = int(0.37 * SR)
    t = _tt(n)
    ir = np.zeros(n)
    fr = spec["lo"]
    while fr < 9000:
        fr *= 2 ** rng.uniform(0.04, 0.11)
        lvl = 10 * np.log10(fr / 1000) + rng.normal(0, 3.0)
        q = rng.uniform(15, 45)
        ir += 10 ** (lvl / 20) * np.exp(-np.pi * fr * t / q) * np.sin(2 * np.pi * fr * t + rng.uniform(0, 2 * np.pi))
    ir[0] += 0.2 * np.sqrt((ir ** 2).sum())
    N = 1 << 15
    fg = np.fft.rfftfreq(N, 1 / SR)
    M = 20 * np.log10(np.abs(np.fft.rfft(ir, N)) + 1e-12)
    corr = _table_db(spec["table"], fg) - _smooth_oct(fg, M, 1 / 3)
    corr -= np.interp(1000, fg, corr)
    h = _minphase(np.clip(corr, -40, 40), 4096)
    ir = signal.oaconvolve(ir, h)[:n]
    ir /= np.sqrt((ir ** 2).sum()) * 6
    _BODIES[key] = ir.astype(np.float32)
    return _BODIES[key]


def string_body(kind, p, x, variant=None):
    ir = string_body_ir(kind, p.get("body", 0) if variant is None else variant)
    spec = STRING_KIND[kind]
    y = signal.oaconvolve(x, ir)[:len(x)]
    y = signal.sosfilt(signal.butter(2, spec["hpf"], btype="high", fs=SR, output="sos"), y)
    y = signal.sosfilt(signal.butter(2, spec["lpf"] - 3000 * float(p.get("dark", 0.3)), fs=SR, output="sos"), y)
    return y.astype(np.float32)


def _pizz(kind, f, vel, n, seed, bright=0.4):
    """A plucked string with the measured pizzicato decay (finger, not pick: soft and round)."""
    from instruments import ks_string
    a, fref, b = STRING_KIND.get(kind, STRING_KIND["viola"])["pz"] if kind in STRING_KIND else (0.9, 440.0, 0.7)
    t60 = a * (fref / f) ** b
    rng = _rng(f, vel, seed, 31)
    P = SR / f
    L = max(4, int(P))
    e = rng.standard_normal(L) * np.hanning(L)
    # a finger, not a pick: the excitation is rolled off steeply from about 3 x f (measured: with a brighter pluck the
    # first 100 ms carried 15-20 dB more 2-8 kHz than the recordings; at 3 x f, 4th order, about +4 dB)
    e = signal.sosfilt(signal.butter(4, min(SR * 0.45, max(300.0, 3.0 * f * (0.6 + 0.8 * bright) * (0.5 + vel))),
                                     fs=SR, output="sos"), e)
    D = max(1, int(P * 0.22))
    e2 = e.copy()
    e2[D:] -= e[:-D]
    exc = np.zeros(n)
    exc[:min(n, L)] = e2[:min(n, L)]
    y = ks_string(f, n, t60, exc, 0.5).astype(np.float64)
    # the pluck's first tenths of a second: the recordings fall about 10 dB in 100 ms and 20 dB in 300 ms before the
    # string's own decay takes over, and peak about 9.5 dB over the arco's level at the same pitch
    y += 2.0 * ks_string(f, n, 0.2, exc, 0.5).astype(np.float64)
    return y * vel * 6.8


def _art_list(nt):
    return list(nt.get("art") or [])


def string_line(kind, p, notes, total_n):
    """`cello` and `viola`: the violin's bowed waveguide (engine/violin.py) with classical defaults; pizzicato notes
    (`/pz`) use a plucked string with the measured decay. The body is applied afterwards (POST)."""
    import violin as _v
    q = dict(CLASSICAL)
    q.update(p)
    arco, pz = [], []
    for nt in notes:
        (pz if ("pz" in _art_list(nt) or q.get("pizz")) else arco).append(nt)
    y = np.zeros(total_n, dtype=np.float32)
    if arco:
        y += _v.violin_line(q, arco, total_n)
    for j, nt in enumerate(pz):
        s = int(nt["t0"])
        if s >= total_n:
            continue
        m = min(total_n - s, _nn(min(8.0, STRING_KIND[kind]["pz"][0] * 2.5)))
        y[s:s + m] += _pizz(kind, nt["f"], nt["vel"], m, j + int(q.get("seed", 7)), q.get("pizz_bright", 0.4)).astype(np.float32)
    return y


# a section: several players per line, each its own string, body, intonation, timing and vibrato, spread across the
# stage. The spread values are measured on Versilian's sections (VSCO-2-CE susvib, 18 notes; see docs/MANUAL.md).
SECTION = {"violins": dict(players=8, body="violin", trim=0.0), "violas": dict(players=6, body="viola", trim=-3.0),
           "celli": dict(players=5, body="cello", trim=-4.0), "cellos": dict(players=5, body="cello", trim=-4.0),
           "basses": dict(players=4, body="bass", trim=-12.75, sp_stop_ms=750)}
# basses (2026-11-26): write the sounding pitch (E1 = 41 Hz, the open E string); the trim puts the section at the
# celli's RMS an octave up (measured at E1-A2: the fitted body leaves the basses 8.75 dB hotter) [H: the balance].
# A spiccato note is damped by the bow `sp_stop_ms` after its onset (unless the next note comes first): the free
# waveguide string at 41-110 Hz rang over 1.5 s to -20 dB; VSCO-2-CE's solo contrabass spiccato falls 20 dB in 270-720
# ms after its peak (median 650; 3 notes), the model at 750 ms in 455-645 (examples/production/cinematic/README.md).
# Fast ostinati articulate like the recordings: 16ths at 100-140 bpm measure 5-8 dB of note-to-note contrast against
# 1-6 dB for the recorded notes overlap-added at the same rate.


def strings_section(p, notes, total_n):
    import violin as _v
    sec = p.get("section", "violins")
    spec = SECTION.get(sec, SECTION["violins"])
    players = int(p.get("players", spec["players"]))
    spread_ms = float(p.get("spread_ms", 18.0))
    detune = float(p.get("detune_cents", 6.0))
    width = float(np.clip(p.get("width", 0.7), 0, 1))
    seed = int(p.get("seed", 5))
    bow_env = p.get("bow_env")  # "cresc" | "dim" | "swell": applied to every arco note without its own
    base = dict(CLASSICAL)
    base.update({k: v for k, v in p.items() if k not in ("section", "players", "spread_ms", "detune_cents", "width",
                                                           "type", "bow_env")})
    if "sp_stop_ms" in spec:  # the basses: spiccato notes damped by the bow (fitted, see SECTION)
        base.setdefault("sp_stop_ms", spec["sp_stop_ms"])
    rng = np.random.default_rng(9000 + seed)
    # chords: group notes that start together; player j plays the (j mod k)-th note of a k-note chord (divisi)
    notes = sorted(notes, key=lambda nt: (nt["t0"], nt["f"]))
    groups, cur = [], []
    for nt in notes:
        if cur and nt["t0"] - cur[0]["t0"] > int(0.03 * SR):
            groups.append(cur)
            cur = []
        cur.append(nt)
    if cur:
        groups.append(cur)
    out = np.zeros((2, total_n), dtype=np.float32)
    for j in range(players):
        pj = dict(base)
        pj["seed"] = seed * 100 + j
        pj["vibrato"] = base["vibrato"] * rng.uniform(0.7, 1.3)
        pj["vib_rate"] = base["vib_rate"] * rng.uniform(0.88, 1.12)
        pj["bow_pos"] = float(base.get("bow_pos", 0.12)) * rng.uniform(0.85, 1.2)
        pj["pressure"] = float(base.get("pressure", 0.7)) + rng.normal(0, 0.04)
        pj["tune_cents"] = float(base.get("tune_cents", 0.0)) + rng.normal(0, detune)
        line = []
        for g in groups:
            g = sorted(g, key=lambda nt: nt["f"])
            nt = dict(g[j % len(g)])
            dt = float(np.clip(rng.normal(0, spread_ms), -2.5 * spread_ms, 2.5 * spread_ms)) / 1000
            nt["t0"] = max(0, int(nt["t0"] + dt * SR))
            nt["n"] = max(64, int(nt["n"] - dt * SR * 0.5))
            nt["f"] = nt["f"] * 2 ** (rng.normal(0, 3.0) / 1200)
            nt["vel"] = float(np.clip(nt["vel"] * rng.uniform(0.85, 1.0), 0.05, 1.0))
            art = _art_list(nt)
            if bow_env and not any(a in art for a in ("cresc", "dim", "swell", "pz")) and not p.get("pizz"):
                art = art + [bow_env]
            nt["art"] = art
            # a section's bow attack: measured 32-76 ms at forte, 300-700 ms at piano (VSCO-2-CE sections)
            nt["attack"] = float(p.get("attack", 0.05 + 0.6 * (1 - nt["vel"]) ** 1.5)) * rng.uniform(0.8, 1.25)
            line.append(nt)
        line.sort(key=lambda nt: nt["t0"])
        arco = [nt for nt in line if not ("pz" in nt["art"] or p.get("pizz"))]
        pz = [nt for nt in line if ("pz" in nt["art"] or p.get("pizz"))]
        y = np.zeros(total_n, dtype=np.float32)
        if arco:
            y += _v.violin_line(pj, arco, total_n)
        for k, nt in enumerate(pz):
            s = int(nt["t0"])
            if s >= total_n:
                continue
            m = min(total_n - s, _nn(5.0))
            y[s:s + m] += _pizz(spec["body"], nt["f"], nt["vel"], m, k + 31 * j + seed,
                                pj.get("pizz_bright", 0.4)).astype(np.float32)
        air = float(p.get("air", 0.5))
        if air > 0 and arco:  # bow hair and rosin: the recorded sections carry 15-20 dB more above 10 kHz
            envl = np.sqrt(np.convolve(y.astype(np.float64) ** 2, np.ones(882) / 882, "same"))
            nz = np.random.default_rng(4000 + 7 * j + seed).standard_normal(total_n)
            nz = signal.sosfilt(signal.butter(2, 7000, btype="high", fs=SR, output="sos"), nz)
            y = y + (nz * envl * 0.25 * air).astype(np.float32)
        if spec["body"] == "violin":
            y = _v.body(dict(pj, body=j), y)
        else:
            y = string_body(spec["body"], pj, y, variant=j)
        pos = (j / max(players - 1, 1) - 0.5) * 2 * width if players > 1 else 0.0
        a = (pos + 1) * np.pi / 4
        out[0] += y * np.cos(a)
        out[1] += y * np.sin(a)
    return out / np.sqrt(players) * np.sqrt(2) * 10 ** (spec["trim"] / 20)


# ---------------------------------------------------------------- bell, clean ending (opt-in)
def bell_clean(p, f, vel, dur):
    """`bell` with `"clean": true`: the same FM bell, but it rings on to -60 dB (at most `ring`, 9 s) and fades over
    its last 50 ms, instead of being cut 22 dB down at 2.5 x `decay` (the documented click). Without `clean` the
    engine plays the original `bell` untouched."""
    decay = p.get("decay", 2.2)
    n = _nn(min(max(dur, decay * 6.91), float(p.get("ring", 9.0))))
    t = _tt(n)
    ratio = p.get("ratio", 3.5)
    idx = (1.5 + 3 * vel) * np.exp(-t / 0.6)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t))
    x += 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / (decay * 0.3))
    env = np.exp(-t / decay) * np.minimum(t / 0.001, 1)
    return _end_fade(x * env * vel * 0.4, 50).astype(np.float32)


# ---------------------------------------------------------------- vibraphone
# Measured on the University of Iowa MIS vibraphone (2012, "sustain" ff: pedal down, motor off; C4, G4, C5, G5):
# fundamental T60 23 s (C4), 18.8 (G4), 14.7 (C5), 9.3 (G5): about 23 s x (263 Hz / f)^0.8; the bars are tuned so the
# first overtone sits at 4.0 x f1 (5-21 dB down at 30 ms, T60 0.7-4 s) and the second near 10 x f1 at C4, falling to
# 7.9 at G5 (from -9 dB at C4 to -49 dB at G5, T60 0.2-0.4 s); 2nd and 3rd harmonics 38-47 dB down (the resonator);
# the fundamental builds over 5-20 ms in its resonator tube. The motor turns discs in the tubes at 1-12 Hz (Wikipedia,
# "Vibraphone"), partly closing the resonators: a tremolo of the fundamental and a slight vibrato. No motor-on
# recording was reachable, so the motor's depth is hand-tuned (off by default).


def vibraphone(p, notes, total_n):
    """`vibraphone` (a line renderer, so the motor turns once for the whole track): polyphonic, notes may overlap."""
    hard = float(np.clip(p.get("hardness", 0.35), 0, 1))
    pedal = bool(p.get("pedal", False))
    rel = float(p.get("release", 0.12))
    dec = float(p.get("decay", 1.0))
    ring = float(p.get("ring", 10.0))
    rate = float(p.get("motor", 0.0))
    depth = float(np.clip(p.get("depth", 0.5), 0, 1))
    out = np.zeros(total_n, dtype=np.float64)
    tg = np.arange(total_n) / SR
    motor = 1 - depth * (0.5 + 0.5 * np.cos(2 * np.pi * rate * tg)) if rate > 0 else None
    for j, nt in enumerate(sorted(notes, key=lambda nt: nt["t0"])):
        f, vel, s = float(nt["f"]), float(nt["vel"]), int(nt["t0"])
        if s >= total_n:
            continue
        rng = _rng(f, vel, j, 41)
        t1 = 23.0 * (263.0 / f) ** 0.8 * dec
        dur = nt["n"] / SR
        n = _nn(min(t1, ring) if pedal else min(dur + rel, t1, ring))
        n = max(_nn(0.05), min(n, total_n - s))
        t = _tt(n)
        oc = float(np.clip(np.log2(f / 263.0), -1, 2))
        fund = np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * _t60_env(t, t1)
        fund *= 1 - np.exp(-t / (np.clip(8.0 * 263.0 / f, 2.0, 14.0) / 1000))
        if motor is not None:  # the discs close the resonator: the fundamental breathes, with a slight vibrato
            m = motor[s:s + n]
            fund = fund * m
        x = fund
        for k, lv in ((2, -40), (3, -46)):
            if k * f < SR * 0.44:
                x = x + 10 ** (lv / 20) * np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28)) * _t60_env(t, 0.4 * t1)
        soft = (hard - 0.35) * 2  # mallet: yarn (0) .. hard (1); 0.35 = the reference's mallets
        modes = [(4.0, -12 + 8 * soft, 3.5 * (263.0 / f) ** 0.5),
                 (10.0 - 2.1 * max(0.0, oc) / 1.58, -9 - 23 * oc + 14 * soft, 0.3)]
        for r, lv, t60 in modes:
            fm = r * f
            if fm > SR * 0.44:
                continue
            lv0 = lv + 60 * 0.03 / t60
            x = x + 10 ** (lv0 / 20) * np.sin(2 * np.pi * fm * t + rng.uniform(0, 6.28)) * _t60_env(t, t60 * dec)
        k = min(n, _nn(0.01))
        x[:k] += _bp(rng.standard_normal(k), 800, 2500 + 7000 * hard) * np.exp(-t[:k] / 0.0008) * 0.05 * (0.3 + hard)
        if not pedal:
            h = _nn(dur)
            if h < n:
                x[h:] *= np.exp(-np.arange(n - h) / _nn(rel / 4))
        out[s:s + n] += _end_fade(x, 40) * vel ** 1.2 * 0.45
    return out.astype(np.float32)
