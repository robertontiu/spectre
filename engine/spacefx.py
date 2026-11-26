"""Space and tone effects for the modern strands (docs/TRANCE.md "Modern trance production", G and I; docs/MANUAL.md
"Space: shimmer, granular, resonance suppressor"). Additive: studio.py calls into this module only when a project
names one of these effects, so every earlier project renders bit for bit as before.

  shimmer    a pitch-shifted feedback reverb: an 8-line feedback delay network (input diffusion, per-line damping,
             modulated delay lines) with a pitch shifter (+12 by default, an optional second interval) in its feedback
             path, so every pass through the tank climbs an interval and fades: the "Valhalla Shimmer" sound.
  granular   a grain cloud that freezes or stretches what it is fed: grains read from a read head that follows,
             stretches (scan < 1) or holds still (scan 0, a freeze) behind the playhead; grain size, density,
             position, spray, pitch, pitch spread, intervals, window, pan spread, reverse.
  suppress   a dynamic resonance suppressor (the job soothe-style processors do after saturation): an STFT that
             finds narrow peaks standing out of the spectrum's smoothed envelope and turns them down while they
             last, linked across the channels.

All three are deterministic: the granular schedule draws from its own generator seeded by the project seed and the
owner's name; the others draw nothing. Every parameter that `curves` names can move over time (section `auto`).
"""
import zlib

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


# Defaults (also what an automation curve starts from outside the sections that move a parameter) and the parameters
# section `auto` can move. `mix` is the dry/wet of the fx form (a return is all wet).
DEFAULTS = {
    "shimmer": dict(decay=6.0, size=0.6, damping=0.45, amount=0.5, shift=12.0, shift2=19.0, mix2=0.0, grain_ms=90.0,
                    mod=0.4, mod_rate=0.35, low_cut=350.0, width=1.0, mix=0.35),
    "granular": dict(grain_ms=300.0, density=80.0, position_ms=150.0, scan=1.0, spray_ms=800.0, pitch=0.0,
                     pitch_spread=0.0, pan_spread=0.8, reverse=0.0, jitter=0.6, smooth=2.0, smooth_ms=40.0,
                     blur_ms=1000.0, tone_hz=7000.0, dissolve=0.0, mix=0.5),
    "suppress": dict(depth=6.0, threshold=2.0, sharpness=0.5, ratio=3.0, lo=300.0, hi=16000.0, attack_ms=5.0,
                     release_ms=80.0, mix=1.0),
}
AUTOMATABLE = {"shimmer": {"amount", "mix"},
               "granular": {"density", "grain_ms", "scan", "position_ms", "spray_ms", "pitch", "pitch_spread", "mix"},
               "suppress": {"depth"}}


def _curve(v, n, default):
    """A parameter as a per-sample float64 curve: an (n,) array (automation) or a scalar."""
    if isinstance(v, np.ndarray):
        return v.astype(np.float64)
    return np.full(n, float(default if v is None else v), dtype=np.float64)


# ------------------------------------------------------------------ shimmer

# Delay line lengths (ms) of the tank at size 0.5: mutually prime in samples, spread 29-73 ms (Jot's FDN; the
# lengths are hand-picked [H] in the range Dattorro and Jot use for a hall).
_FDN_MS = np.array([29.7, 37.1, 41.1, 43.7, 53.0, 59.9, 67.7, 73.3])
_DIFF_MS = np.array([4.77, 3.59, 12.73, 9.30])  # input diffusers (Schroeder all-passes, g 0.7; Dattorro 1997)


@njit(cache=True)
def _shimmer_kernel(xl, xr, lens, gains, damp, mod_s, mod_rate, diff_lens, amount, sh_ratio, sh2_ratio, mix2, win,
                    fb_hp, seed_phase):
    n = len(xl)
    N = 8
    maxlen = 0
    for i in range(N):
        if lens[i] > maxlen:
            maxlen = lens[i]
    size = 1
    while size < maxlen + int(mod_s) + 8:
        size *= 2
    mask = size - 1
    buf = np.zeros((N, size))
    lp = np.zeros(N)
    w = 0
    # input diffusers, one chain per channel
    dsize = 1
    for j in range(4):
        while dsize < diff_lens[j] + 2:
            dsize *= 2
    dmask = dsize - 1
    dbuf = np.zeros((2, 4, dsize))
    dw = 0
    # pitch shifters (two taps each, crossfaded): a buffer of the tank's output
    psize = 1
    while psize < int(win) * 2 + 8:
        psize *= 2
    pmask = psize - 1
    pbuf = np.zeros(psize)
    pw_ = 0
    ph1 = 0.0
    ph2 = 0.0
    # one-pole high-pass on the shifted feedback (keeps the climb from muddying the low end)
    hp_a = np.exp(-2.0 * np.pi * fb_hp / 44100.0)
    hp_x = 0.0
    hp_y = 0.0
    yl = np.zeros(n)
    yr = np.zeros(n)
    fbk = 0.0
    TWO_PI = 2.0 * np.pi
    outs = np.empty(N)
    for t in range(n):
        # diffuse the inputs
        il = xl[t]
        ir = xr[t]
        for j in range(4):
            d = diff_lens[j]
            r = (dw - d) & dmask
            v = dbuf[0, j, r]
            u = il + 0.7 * v
            dbuf[0, j, dw] = u
            il = v - 0.7 * u
            v = dbuf[1, j, r]
            u = ir + 0.7 * v
            dbuf[1, j, dw] = u
            ir = v - 0.7 * u
        dw = (dw + 1) & dmask
        # read the delay lines (modulated, linear interpolation)
        s = 0.0
        for i in range(N):
            m = mod_s * np.sin(TWO_PI * mod_rate * (1.0 + 0.13 * i) * t / 44100.0 + seed_phase + 0.9 * i)
            dl = lens[i] + m
            ip = int(dl)
            fr = dl - ip
            a = buf[i, (w - ip) & mask]
            b = buf[i, (w - ip - 1) & mask]
            v = a + (b - a) * fr
            # damping: one-pole low-pass per line
            lp[i] = v * (1.0 - damp) + lp[i] * damp
            outs[i] = lp[i] * gains[i]
            s += outs[i]
        # Householder feedback matrix: y = x - 2/N * sum(x)
        k = 2.0 / N * s
        # stereo outputs (alternating signs keep the two sides decorrelated)
        ol = outs[0] - outs[2] + outs[4] - outs[6]
        orr = outs[1] - outs[3] + outs[5] - outs[7]
        yl[t] = ol * 0.5
        yr[t] = orr * 0.5
        # the shimmer: the tank's output, pitched up, back into the tank
        pbuf[pw_] = 0.5 * (ol + orr)
        sh = 0.0
        for q in range(2):
            ratio = sh_ratio if q == 0 else sh2_ratio
            g = 1.0 if q == 0 else mix2
            if g <= 0.0:
                continue
            ph = ph1 if q == 0 else ph2
            for tap in range(2):
                p = ph + 0.5 * tap
                p = p - np.floor(p)
                dly = 2.0 + p * win
                ip = int(dly)
                fr = dly - ip
                a = pbuf[(pw_ - ip) & pmask]
                b = pbuf[(pw_ - ip - 1) & pmask]
                sh += g * (a + (b - a) * fr) * np.sin(np.pi * p)
            ph = ph - (ratio - 1.0) / win
            ph = ph - np.floor(ph)
            if q == 0:
                ph1 = ph
            else:
                ph2 = ph
        sh = sh / (1.0 + mix2)
        pw_ = (pw_ + 1) & pmask
        hp_y = hp_a * (hp_y + sh - hp_x)
        hp_x = sh
        fbk = np.tanh(hp_y * amount[t] * 1.2)
        # write: input + feedback through the matrix + the shimmer
        for i in range(N):
            inj = il if (i % 2 == 0) else ir
            buf[i, w] = outs[i] - k + 0.35 * inj + 0.5 * fbk * (1.0 if i % 2 == 0 else -1.0)
        w = (w + 1) & mask
    return yl, yr


def shimmer(x, cfg, curves=None):
    """x: (2, n) float32 input (already pre-delayed). cfg: decay (s, RT60 of the tank, 6.0), size 0-1 (0.6; the
    delay lengths), damping 0-1 (0.45; highs die first), amount 0-1 (0.5; how much of the tank comes back pitched:
    the shimmer), shift (semitones, 12), shift2 (semitones, 7 or 19; off when mix2 is 0), mix2 0-1 (0), grain_ms
    (90; the pitch shifter's window: longer = smoother, more smeared), mod 0-1 (0.4; chorus of the delay lines:
    depth up to 1.5 ms), mod_rate (Hz, 0.35), low_cut (Hz, 350: high-pass on the shifted feedback), width 0-1 (1).
    curves: {"amount": (n,) array} from section automation. Returns the wet (2, n) float32."""
    curves = curves or {}
    n = x.shape[1]
    size = float(np.clip(cfg.get("size", 0.6), 0.0, 1.0))
    scale = 0.5 + 1.5 * size
    lens = np.round(_FDN_MS * scale / 1000 * SR).astype(np.int64)
    rt = max(float(cfg.get("decay", 6.0)), 0.1)
    gains = 10 ** (-3.0 * lens / (rt * SR))
    damp = float(np.clip(cfg.get("damping", 0.45), 0.0, 0.98)) * 0.85
    mod_s = float(np.clip(cfg.get("mod", 0.4), 0, 1)) * 0.0015 * SR
    diff = np.round(_DIFF_MS * (0.6 + 0.8 * size) / 1000 * SR).astype(np.int64)
    amount = np.clip(_curve(curves.get("amount", cfg.get("amount")), n, 0.5), 0.0, 1.0)
    win = float(cfg.get("grain_ms", 90.0)) / 1000 * SR
    r1 = 2 ** (float(cfg.get("shift", 12.0)) / 12)
    r2 = 2 ** (float(cfg.get("shift2", 19.0)) / 12)
    mix2 = float(np.clip(cfg.get("mix2", 0.0), 0.0, 1.0))
    xl = np.ascontiguousarray(x[0], dtype=np.float64)
    xr = np.ascontiguousarray(x[1], dtype=np.float64)
    yl, yr = _shimmer_kernel(xl, xr, lens, gains, damp, mod_s, float(cfg.get("mod_rate", 0.35)), diff, amount,
                             r1, r2, mix2, win, float(cfg.get("low_cut", 350.0)), 0.37)
    # the shimmer adds energy to the tank: level-compensate so `amount` changes colour, not loudness (measured on a
    # plucked A4 at decay 6 s: the uncompensated tank is +8.7 / +16 / +17 dB at amount 0.5 / 0.9 / 1.0)
    comp = 1 / (1 + 5 * amount ** 1.5)
    yl, yr = yl * comp, yr * comp
    wd = float(np.clip(cfg.get("width", 1.0), 0, 1))
    if wd < 1:
        m = 0.5 * (yl + yr)
        yl, yr = m + (yl - m) * wd, m + (yr - m) * wd
    return np.stack([yl, yr]).astype(np.float32)


# ------------------------------------------------------------------ granular

@njit(cache=True)
def _grains_kernel(src, out_l, out_r, starts, lens, pos, rates, gl, gr, rev, wtype, wpar):
    n = len(out_l)
    m = len(src)
    for g in range(len(starts)):
        s0 = starts[g]
        L = lens[g]
        p0 = pos[g]
        r = rates[g]
        for j in range(L):
            t = s0 + j
            if t >= n:
                break
            if t < 0:
                continue
            x = j / L
            if wtype == 0:      # hann
                wv = 0.5 - 0.5 * np.cos(2 * np.pi * x)
            elif wtype == 1:    # triangle
                wv = 1.0 - abs(2 * x - 1)
            elif wtype == 2:    # tukey (flat middle, cosine edges over wpar of the grain)
                e = wpar / 2
                if x < e:
                    wv = 0.5 - 0.5 * np.cos(np.pi * x / e)
                elif x > 1 - e:
                    wv = 0.5 - 0.5 * np.cos(np.pi * (1 - x) / e)
                else:
                    wv = 1.0
            else:               # gauss
                wv = np.exp(-0.5 * ((x - 0.5) / wpar) ** 2)
            if rev[g]:
                q = p0 + (L - 1 - j) * r
            else:
                q = p0 + j * r
            i = int(q)
            if i < 0 or i + 1 >= m:
                continue
            fr = q - i
            v = (src[i] + (src[i + 1] - src[i]) * fr) * wv
            out_l[t] += v * gl[g]
            out_r[t] += v * gr[g]


_WINDOWS = {"hann": 0, "triangle": 1, "tukey": 2, "gauss": 3}


@njit(cache=True)
def _env_follow(x, att, rel):
    y = np.empty_like(x)
    cur = 0.0
    for i in range(len(x)):
        v = x[i]
        a = att if v > cur else rel
        cur = v + (cur - v) * a
        y[i] = cur
    return y


def deattack(src, amount, attack_ms=40.0):
    """The source with its attacks flattened (a transient shaper turned all the way down): a fast and a slow envelope
    of |src| (attack 0.5 ms and `attack_ms`, both releasing over 30 ms); where the fast one runs ahead of the slow one,
    a note is starting, and the source is turned down by (slow / fast) ** amount, so a note's first tens of ms come out
    at the level of what follows them. Grains read from this, so a grain that starts on a pluck's attack does not
    replay it as a new note."""
    if amount <= 0:
        return src
    a = np.abs(src)
    rel = np.exp(-1 / (0.030 * SR))
    fast = _env_follow(a, np.exp(-1 / (0.0005 * SR)), rel)
    slow = _env_follow(a, np.exp(-1 / (attack_ms / 1000 * SR)), rel)
    g = np.minimum(1.0, (slow + 1e-9) / (fast + 1e-9)) ** amount
    g = _env_follow(g[::-1].copy(), np.exp(-1 / (0.002 * SR)), np.exp(-1 / (0.002 * SR)))[::-1]  # no clicks
    return src * g


def _blur(y, ms):
    """Smooth the cloud's spectrum over time: every STFT bin's magnitude is replaced by its average over `ms` (phases
    kept), so what is left of single grains (a level bump, a brighter moment) melts into the texture. One channel at a
    time, in place where it can (speed pass 2026-11-26: the same numbers, a third of the memory: the stereo STFT of a
    6-minute track and its four companions were several GB)."""
    from scipy.ndimage import uniform_filter1d
    nfft, hop = 2048, 512
    n = y.shape[1]
    w = np.sqrt(np.hanning(nfft + 1)[:-1])
    k = max(1, int(round(ms / 1000 * SR / hop)))
    outs = []
    for ch in y:
        _, _, Z = signal.stft(ch, fs=SR, window=w, nperseg=nfft, noverlap=nfft - hop, boundary="even", padded=True)
        M = np.abs(Z)
        g = uniform_filter1d(M, k, axis=-1, mode="nearest")
        g /= (M + 1e-9)
        del M
        np.clip(g, 0.0, 4.0, out=g)
        Z *= g
        del g
        _, o = signal.istft(Z, fs=SR, window=w, nperseg=nfft, noverlap=nfft - hop, boundary=True)
        del Z
        outs.append(o[:n])
    out = np.stack(outs)
    if out.shape[1] < n:
        out = np.pad(out, ((0, 0), (0, n - out.shape[1])))
    return out


def _dissolve(y, scan, dis, starts=()):
    """A freeze that dissolves like a tail: wherever the read head stands still (scan under 0.02), the cloud falls 60 dB
    and its low-pass closes from 16 kHz by 4 octaves over `dis` seconds from the moment the freeze began; it stays
    dissolved after the freeze until the next section start (so it does not come back in the song's tail)."""
    n = y.shape[1]
    frozen = scan < 0.02
    if not frozen.any():
        return y
    tau = np.full(n, -1.0)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], frozen.astype(np.int8), [0]])))
    later = sorted(int(v) for v in starts)
    for a, b in zip(edges[::2], edges[1::2]):
        nxt = next((v for v in later if v >= b), n)
        tau[a:nxt] = np.arange(nxt - a) / SR
    fz = tau >= 0
    g = np.ones(n)
    g[fz] = 10 ** (-3 * tau[fz] / dis)
    out = y * g
    B = 1024
    zi = np.zeros((2, 2))
    for s0 in range(0, n, B):
        s1 = min(n, s0 + B)
        if not fz[s0:s1].any():
            zi[:] = 0
            continue
        t0 = max(tau[s0:s1].max(), 0.0)
        fc = float(np.clip(16000 * 2 ** (-4 * t0 / dis), 150, SR * 0.45))
        b_, a_ = signal.butter(2, fc, fs=SR)
        for c in range(2):
            out[c, s0:s1], zi[c] = signal.lfilter(b_, a_, out[c, s0:s1], zi=zi[c] if zi[c].any() else
                                                  signal.lfilter_zi(b_, a_) * out[c, s0])
    return out


def _sections_heads(n, sections, scan, position_s, anchor):
    """The read head (samples, float) for every output sample: at each section start (anchor "section") it sits
    `position_s` behind the playhead, then moves at `scan` x real time (1 follows, 0.25 stretches 4x, 0 freezes)."""
    starts = [0]
    if anchor == "section" and sections:
        starts = sorted({max(0, int(S["start"] * SR)) for S in sections if int(S["start"] * SR) < n} | {0})
    head = np.empty(n)
    starts.append(n)
    for a, b in zip(starts[:-1], starts[1:]):
        if b <= a:
            continue
        sc = scan[a:b]
        head[a:b] = (a - position_s * SR) + np.concatenate([[0.0], np.cumsum(sc[:-1])])
    return head


def _seek_material(head, src, scan, sections, anchor, thr_db=-40.0, look_s=0.3):
    """A freeze that would hold silence (2026-11-26): where a section starts frozen (scan 0 at its first sample) and
    the source is silent (under `thr_db` re its peak) over the `look_s` before the read head, as when the section
    before ends in a rest, the head moves back to the last sounding sample for the whole section, so the freeze holds
    the material instead of the rest. Heads that already sit in sound are left exactly as they were."""
    if anchor != "section" or not sections:
        return head
    n = len(head)
    loud = np.flatnonzero(np.abs(src) > np.abs(src).max() * 10 ** (thr_db / 20))
    if not len(loud):
        return head
    starts = sorted({max(0, int(S["start"] * SR)) for S in sections if int(S["start"] * SR) < n} | {0}) + [n]
    for a, b in zip(starts[:-1], starts[1:]):
        if b <= a or scan[a] != 0:
            continue
        h = int(head[a])
        k = np.searchsorted(loud, h) - 1          # the last sounding sample before the head
        if k < 0 or loud[k] >= h - int(look_s * SR):
            continue                               # nothing earlier, or the head already reads sound
        head[a:b] -= h - loud[k]
    return head


def granular(x, cfg, curves=None, seed=1, owner="granular", sections=None):
    """x: (2, n) input. cfg: grain_ms (300), density (grains per second, 80), position_ms (150: how far behind the
    playhead the read head starts), scan (1.0: the read head's speed against real time; 0 = freeze, 0.25 = stretched
    4x), spray_ms (800: random extra distance back per grain; wide reads make a pad, not a slowed melody), pitch (semitones, 0), pitch_spread (semitones, 0: each
    grain detuned at random within +-), intervals (a list of semitones, e.g. [0, 12, 7]: each grain picks one),
    window (hann, triangle, tukey, gauss), window_shape (tukey: the fraction that fades, 0.5; gauss: sigma, 0.18),
    pan_spread 0-1 (0.8), reverse 0-1 (0: the share of grains played backwards), jitter 0-1 (0.6: how irregular the
    grain onsets are), anchor ("section": the read head returns to the playhead at every section start; "none":
    it never does), smooth (0-3, 2: the input's attacks flattened before the grains read it, over smooth_ms 40, so
    a grain that starts on an attack does not replay it as a stray note), blur_ms (1000: the cloud's spectrum averaged
    over this time, phases kept; 0 for audible single grains), tone_hz (7000: a 12 dB/oct low-pass on the cloud; 0 =
    off), dissolve (s, 0 = hold: where scan is 0 the cloud falls 60 dB and darkens over this time, and stays gone until
    the next section), seek (true: a section that starts frozen over silence reads the last sounding material before
    it instead; _seek_material), seed. Slow-motion settings: spray_ms 40, grain_ms 90, density 30, smooth 0, blur_ms 0. curves: per-sample arrays for density, grain_ms, scan, position_ms, spray_ms, pitch,
    pitch_spread. Returns the cloud (2, n) float32, level-matched to its input (RMS over the active part)."""
    curves = curves or {}
    n = x.shape[1]
    src = np.ascontiguousarray(x.mean(0), dtype=np.float64)
    if not np.any(src):
        return np.zeros((2, n), dtype=np.float32)
    src = deattack(src, float(cfg.get("smooth", DEFAULTS["granular"]["smooth"])),
                   float(cfg.get("smooth_ms", DEFAULTS["granular"]["smooth_ms"])))
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, zlib.crc32(owner.encode("utf-8")), 7,
                                 int(cfg.get("seed", 0))])
    dens = np.clip(_curve(curves.get("density", cfg.get("density")), n, DEFAULTS["granular"]["density"]), 0.5, 400.0)
    gms = np.clip(_curve(curves.get("grain_ms", cfg.get("grain_ms")), n, DEFAULTS["granular"]["grain_ms"]), 5.0, 2000.0)
    scan = _curve(curves.get("scan", cfg.get("scan")), n, 1.0)
    pos_ms = _curve(curves.get("position_ms", cfg.get("position_ms")), n, DEFAULTS["granular"]["position_ms"])
    spray = np.maximum(_curve(curves.get("spray_ms", cfg.get("spray_ms")), n, DEFAULTS["granular"]["spray_ms"]), 0.0)
    pitch = _curve(curves.get("pitch", cfg.get("pitch")), n, 0.0)
    pspread = np.maximum(_curve(curves.get("pitch_spread", cfg.get("pitch_spread")), n, 0.0), 0.0)
    head = _sections_heads(n, sections, scan, float(pos_ms[0]) / 1000, cfg.get("anchor", "section"))
    head = head - (pos_ms - pos_ms[0]) / 1000 * SR    # an automated position moves the head too
    if cfg.get("seek", True):
        head = _seek_material(head, src, scan, sections, cfg.get("anchor", "section"))
    jit = float(np.clip(cfg.get("jitter", 0.6), 0, 1))
    # grain onsets: one grain every 1/density s, each interval scaled at random by (1 +- jitter)
    t = 0.0
    onsets = []
    while t < n:
        onsets.append(int(t))
        d = SR / dens[int(t)]
        t += d * (1 + jit * (rng.random() * 2 - 1))
    onsets = np.array(onsets, dtype=np.int64)
    G = len(onsets)
    lens = np.maximum(16, (gms[onsets] / 1000 * SR).astype(np.int64))
    ivs = cfg.get("intervals") or [0]
    iv = np.array([float(v) for v in ivs])[rng.integers(0, len(ivs), G)]
    semis = pitch[onsets] + iv + pspread[onsets] * (rng.random(G) * 2 - 1)
    rates = 2 ** (semis / 12)
    back = spray[onsets] / 1000 * SR * rng.random(G)
    pos = head[onsets] - back
    # never read the future: a grain ends at or before the playhead
    latest = onsets - lens * rates - 1
    pos = np.minimum(pos, latest)
    ok = pos >= 0
    ps = float(np.clip(cfg.get("pan_spread", 0.8), 0, 1))
    pan = ps * (rng.random(G) * 2 - 1)
    a = (pan + 1) * np.pi / 4
    over = np.maximum(dens[onsets] * gms[onsets] / 1000, 1.0)  # grains overlapping: keep the level steady
    amp = 1 / np.sqrt(over)
    gl = np.cos(a) * np.sqrt(2) * amp
    gr = np.sin(a) * np.sqrt(2) * amp
    rev = rng.random(G) < float(cfg.get("reverse", 0.0))
    win = cfg.get("window", "hann")
    if win not in _WINDOWS:
        raise ValueError(f"granular: window must be one of {sorted(_WINDOWS)}, not {win!r}")
    wpar = float(cfg.get("window_shape", 0.5 if win == "tukey" else 0.18))
    out_l = np.zeros(n)
    out_r = np.zeros(n)
    _grains_kernel(src, out_l, out_r, onsets[ok], lens[ok], pos[ok], rates[ok], gl[ok], gr[ok], rev[ok],
                   _WINDOWS[win], wpar)
    y = np.stack([out_l, out_r])
    bl = float(cfg.get("blur_ms", DEFAULTS["granular"]["blur_ms"]))
    if bl > 0:
        y = _blur(y, bl)
    tone = float(cfg.get("tone_hz", DEFAULTS["granular"]["tone_hz"]))
    if tone > 0:  # the cloud's damping: a 12 dB/oct low-pass, so the held top does not turn shrill
        y = signal.sosfilt(signal.butter(2, min(tone, SR * 0.45), fs=SR, output="sos"), y, axis=-1)
    act = np.abs(src) > np.abs(src).max() * 1e-3
    r_in = np.sqrt(np.mean(x[:, act].astype(np.float64) ** 2)) if act.any() else 0.0
    r_out = np.sqrt(np.mean(y[:, act] ** 2)) if act.any() else 0.0
    if r_out > 0 and r_in > 0:
        y *= r_in / r_out
    dis = float(cfg.get("dissolve", DEFAULTS["granular"]["dissolve"]))
    if dis > 0:
        y = _dissolve(y, scan, dis, [S["start"] * SR for S in (sections or [])])
    return y.astype(np.float32)


# ------------------------------------------------------------------ resonance suppressor

def suppress(x, cfg, curves=None):
    """x: (2, n). cfg: depth (dB, 6: the most any region is turned down), threshold (dB, 2: how far the spectrum's
    peaks must stand above its broad trend before anything is touched), sharpness 0-1 (0.5: the width of the trend a
    resonance is measured against, 1 octave at 0 to 1/3 octave at 1; sharper = only narrower resonances), ratio (3:
    of the excess above the threshold, 1 - 1/ratio is removed), lo / hi (Hz, 300 / 16000: the band it works in),
    attack_ms (5), release_ms (80), mix 0-1 (1), delta (true: output only what it removed, to hear it). Linked: one
    gain per bin for both channels, from the louder.

    Detection: the power spectrum (STFT, 2048 points, hop 512), averaged over about 20 ms, is turned into its upper
    envelope (the line through the harmonics' peaks: a maximum over 1/6 octave or 250 Hz, whichever is wider, so the
    gaps between a note's harmonics are not read as the trend), then compared with that envelope smoothed over the
    trend width: where the envelope bulges above its trend (a resonant band, a whistle after saturation), the whole
    region is turned down; a flat or gently sloped spectrum, noise or a plain saw, is left alone.
    curves: {"depth": (n,)}."""
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    curves = curves or {}
    n = x.shape[1]
    nfft, hop = 2048, 512
    win = np.sqrt(np.hanning(nfft + 1)[:-1])
    f, tt, Z = signal.stft(x.astype(np.float64), fs=SR, window=win, nperseg=nfft, noverlap=nfft - hop,
                           boundary="even", padded=True)
    pw = (np.abs(Z) ** 2).max(0)                            # (bins, frames), linked
    pw = gaussian_filter1d(pw, 0.8, axis=1)                 # about 20 ms of averaging: steadier detection
    mdb = 10 * np.log10(pw + 1e-18)
    df = f[1] - f[0]
    lin = maximum_filter1d(mdb, size=int(250 / df) | 1, axis=0)
    ppo = 48
    lf = 2 ** np.arange(np.log2(20.0), np.log2(SR / 2), 1 / ppo)
    idx = np.interp(lf, f, np.arange(len(f)))
    i0 = np.clip(np.floor(idx).astype(np.int64), 0, len(f) - 2)
    w = (idx - i0)[:, None]
    g_lin = lin[i0] * (1 - w) + lin[i0 + 1] * w
    g_raw = mdb[i0] * (1 - w) + mdb[i0 + 1] * w
    up = np.maximum(g_lin, maximum_filter1d(g_raw, size=ppo // 6 | 1, axis=0))
    up = gaussian_filter1d(up, ppo / 24, axis=0)
    sharp = float(np.clip(cfg.get("sharpness", 0.5), 0, 1))
    width_oct = 1.0 * (1 / 3) ** sharp
    sg = width_oct * ppo / 2.355
    trend = gaussian_filter1d(up, sg, axis=0, mode="nearest")
    for _ in range(3):  # a robust trend: the bulges are clipped to it and the rest smoothed again, so a resonance
        trend = gaussian_filter1d(np.minimum(up, trend), sg, axis=0, mode="nearest")  # cannot pull it up
    thr = float(cfg.get("threshold", 2.0))
    ratio = max(float(cfg.get("ratio", 3.0)), 1.0)
    red_l = np.clip(up - trend - thr, 0, None) * (1 - 1 / ratio)
    red = np.empty_like(mdb)
    for k in range(red.shape[1]):
        red[:, k] = np.interp(f, lf, red_l[:, k])
    band = (f >= float(cfg.get("lo", 300.0))) & (f <= float(cfg.get("hi", 16000.0)))
    red[~band] = 0
    depth = curves.get("depth")
    if isinstance(depth, np.ndarray):
        fr_idx = np.clip((tt * SR).astype(np.int64), 0, n - 1)
        dcap = depth[fr_idx][None, :]
    else:
        dcap = float(cfg.get("depth", 6.0))
    red = np.minimum(red, dcap)
    red = gaussian_filter1d(red, 2.0, axis=0)               # no single-bin gain jumps (musical noise)
    fr_rate = SR / hop                                      # attack / release across frames
    aa = np.exp(-1 / max(float(cfg.get("attack_ms", 5.0)) / 1000 * fr_rate, 1e-3))
    ar = np.exp(-1 / max(float(cfg.get("release_ms", 80.0)) / 1000 * fr_rate, 1e-3))
    sm = np.empty_like(red)
    cur = np.zeros(red.shape[0])
    for k in range(red.shape[1]):
        v = red[:, k]
        a = np.where(v > cur, aa, ar)
        cur = v + (cur - v) * a
        sm[:, k] = cur
    g = 10 ** (-sm / 20)
    mix = float(np.clip(cfg.get("mix", 1.0), 0, 1))
    if cfg.get("delta"):
        Zo = Z * (1 - g)[None]
    else:
        Zo = Z * (1 - mix + mix * g)[None]
    _, y = signal.istft(Zo, fs=SR, window=win, nperseg=nfft, noverlap=nfft - hop, boundary=True)
    y = y[:, :n]
    if y.shape[1] < n:
        y = np.pad(y, ((0, 0), (0, n - y.shape[1])))
    return y.astype(np.float32)


# ------------------------------------------------------------------ hall (early reflections + a diffuse tail)

# The concert-hall numbers behind the defaults (Beranek, "Concert Halls and Opera Houses", 2nd ed. 2004): the best-
# rated halls have a mid-frequency RT60 (occupied) of 1.8-2.2 s, an initial-time-delay gap (direct sound to the first
# reflection) near 20 ms, and a bass ratio (RT at 125-250 Hz over 500-1000 Hz) of 1.1-1.25; the early reflections
# arrive mostly within the first 80 ms. The cinematic brief asks for more than a concert hall: a 2.5-3.5 s tail with
# pre-delay, early reflections at 15-35 ms for choirs (docs/CINEMATIC_HYBRID.md gap 5, docs/voice/MIXING.md), so
# `decay` defaults to 2.8 s, the middle of that range (measured: Schroeder T20 2.4 s at 125 Hz-1 kHz at decay 2.4,
# shorter above 2 kHz as in halls).
HALL = dict(decay=2.8, size=0.85, damping=0.35, itdg_ms=20.0, er_ms=80.0, er_level=0.7, taps=14, er_lpf=6000.0,
            width=1.0, mod=0.25, mod_rate=0.3)


def hall(x, cfg):
    """A large hall for a return (`"type": "hall"`): early reflections (`taps` per side between `itdg_ms` and
    `er_ms`, falling off with time and darkened above `er_lpf`, at `er_level`) and a diffuse tail (the shimmer's
    8-line feedback delay network with the pitch path off: `decay` RT60 s, `size`, `damping`, `mod`) fed by the
    input and the reflections, starting as the reflections thin out. x: (2, n) float32 (pre-delayed). Returns the
    wet (2, n) float32. Deterministic (the reflection pattern is fixed)."""
    q = dict(HALL)
    q.update({k: cfg[k] for k in HALL if k in cfg})
    n = x.shape[1]
    rng = np.random.default_rng(1951)  # fixed: the same room every time
    er = np.zeros((2, n))
    taps = int(q["taps"])
    t0, t1 = float(q["itdg_ms"]), max(float(q["er_ms"]), float(q["itdg_ms"]) + 5)
    for c in range(2):
        ts = np.sort(rng.uniform(t0, t1, taps))
        ts[0] = t0 + (3.0 if c else 0.0)
        for k, tm in enumerate(ts):
            d = int(tm / 1000 * SR)
            if d >= n:
                continue
            g = (t0 / tm) ** 1.2 * rng.uniform(0.6, 1.0) * (1 if k % 3 else -1)
            src = x[c] if k % 2 == 0 else x[1 - c]  # reflections from both sides of the room
            er[c, d:] += g * src[:n - d]
    er = signal.sosfilt(signal.butter(1, float(q["er_lpf"]), fs=SR, output="sos"), er, axis=1) / np.sqrt(taps / 4)
    size = float(np.clip(q["size"], 0.0, 1.0))
    scale = 0.5 + 1.5 * size
    lens = np.round(_FDN_MS * scale / 1000 * SR).astype(np.int64)
    rt = max(float(q["decay"]), 0.1)
    gains = 10 ** (-3.0 * lens / (rt * SR))
    damp = float(np.clip(q["damping"], 0.0, 0.98)) * 0.85
    mod_s = float(np.clip(q["mod"], 0, 1)) * 0.0015 * SR
    diff = np.round(_DIFF_MS * (0.6 + 0.8 * size) / 1000 * SR).astype(np.int64)
    feed = x.astype(np.float64) * 0.5 + er * 0.5
    dly = int(t1 * 0.5 / 1000 * SR)  # the tail builds as the reflections thin out
    feed = np.pad(feed, ((0, 0), (dly, 0)))[:, :n]
    yl, yr = _shimmer_kernel(np.ascontiguousarray(feed[0]), np.ascontiguousarray(feed[1]), lens, gains, damp, mod_s,
                             float(q["mod_rate"]), diff, np.zeros(n), 1.0, 1.0, 0.0, 4096.0, 20.0, 0.53)
    tail = np.stack([yl, yr])
    wet = tail + er * float(q["er_level"])
    wd = float(np.clip(q["width"], 0, 1))
    if wd < 1:
        m = wet.mean(0, keepdims=True)
        wet = m + (wet - m) * wd
    return wet.astype(np.float32)
