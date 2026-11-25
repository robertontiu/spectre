"""Stacks, buses, returns, production fx and structured humanizing (queue item 9b, sound side; docs/PRODUCTION.md
"Gaps and proposals" 3, 4, 7; docs/MANUAL.md "Production: stacks, buses, synth voice").

Everything here is opt-in: studio.py calls into it only when a project uses a key it handles (`layers`, `bus`,
`buses`, `sends`, `mix.returns`, `eq`, the fx types `ott`, `dyneq`, `clip`, `mseq`, an `hpf`/`lpf` with `slope`, a
`humanize` dict), so every earlier project renders bit for bit as before.

  role_eq        a role's EQ preset from the genre's map (engine/eqmaps.json): high-pass at the map's high-pass point
                 (12 dB/oct), low-pass where the map has one, a cut in each region the map cuts, a small emphasis in
                 each region the role owns. A starting point, overridable.
  ott            three-band upward and downward compression after the Ableton "OTT" preset (crossovers 88.3 Hz and
                 2.5 kHz; per band thresholds above and below, ratio about 66:1 above, 4:1 upward below, output gains),
                 with `depth` (dry/wet), `time`, `upward`, `downward`, automatic make-up.
  dyneq          a peak cut that opens only while another track plays (keyed by its hits): the 808-under-kick notch.
  clip           a soft clipper, 4x oversampled.
  mseq           mid/side processing: an fx chain on the mid, another on the side, side high-pass.
  humanize       correlated timing (and velocity) drift: 1/f noise over the song plus per-phrase push and pull.
"""
import json
import os
import zlib

import numpy as np
from scipy import signal

SR = 44100
EQMAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eqmaps.json")

try:
    from numba import njit
except Exception:  # pragma: no cover
    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


def db(x):
    return 10 ** (x / 20)


# ------------------------------------------------------------------ filters

def butter(st, kind, hz, slope):
    """hpf / lpf with a slope of 6, 12, 18, 24, 36 or 48 dB/oct (Butterworth; the engine's plain `hpf`/`lpf` are
    first-order, 6 dB/oct)."""
    order = max(1, int(round(float(slope) / 6)))
    sos = signal.butter(order, float(np.clip(hz, 10, SR * 0.45)), btype="high" if kind == "hpf" else "low",
                        fs=SR, output="sos")
    return signal.sosfilt(sos, st, axis=-1).astype(np.float32)


def _lr4(x, fc):
    """Linkwitz-Riley 4th-order split: (low, high)."""
    lo = signal.butter(2, fc, btype="low", fs=SR, output="sos")
    hi = signal.butter(2, fc, btype="high", fs=SR, output="sos")
    return (signal.sosfilt(lo, signal.sosfilt(lo, x, axis=-1), axis=-1),
            signal.sosfilt(hi, signal.sosfilt(hi, x, axis=-1), axis=-1))


# ------------------------------------------------------------------ role EQ presets

def load_map(genre):
    if not genre:
        return None
    d = json.load(open(EQMAPS))
    g = d.get("_aliases", {}).get(genre, genre)
    if g not in d:
        return None
    m = dict(d[g])
    roles = dict(d[m["inherit"]]["roles"]) if m.get("inherit") else {}
    roles.update(m["roles"])
    m["roles"] = roles
    return m


def _gm(r):
    return float(np.sqrt(r[0] * r[1]))


def role_eq(genre, role, spec=None):
    """The EQ preset of `role` in `genre`'s map as an fx list. spec: "auto" or a dict of overrides: `hp` (Hz, or null
    for none), `lp`, `cut_db` (default -3 in carving genres, -1.5 in the acoustic ones), `own_db` (+1.5; 0 in the
    acoustic ones), `slope` (12), `genre`, `role`. Returns [] when the map has no such role."""
    spec = spec if isinstance(spec, dict) else {}
    m = load_map(spec.get("genre", genre))
    role = spec.get("role", role)
    if m is None or role not in m["roles"]:
        return []
    row = m["roles"][role]
    light = m.get("tolerance_db", 6) > 6       # joc, caroling, Latin pop, chamber: orchestration first, light moves
    cut_db = float(spec.get("cut_db", -1.5 if light else -3.0))
    own_db = float(spec.get("own_db", 0.0 if light else 1.5))
    slope = spec.get("slope", 12)
    fx = []
    hp = spec.get("hp", _gm(row["hp"]) if row.get("hp") else None)
    if hp:
        fx.append({"type": "hpf", "hz": round(float(hp), 1), "slope": slope})
    lp = spec.get("lp", _gm(row["lp"]) if row.get("lp") else None)
    if lp:
        fx.append({"type": "lpf", "hz": round(float(lp), 1), "slope": slope})
    if cut_db:
        for a, b in row.get("cut", []):
            fc = _gm((a, b))
            fx.append({"type": "eq", "hz": round(fc, 1), "gain_db": cut_db, "q": round(float(np.clip(fc / (b - a), 0.5, 3)), 2)})
    if own_db:
        for a, b in row.get("own", []):
            fc = _gm((a, b))
            fx.append({"type": "eq", "hz": round(fc, 1), "gain_db": own_db, "q": round(float(np.clip(fc / (b - a), 0.4, 2)), 2)})
    return fx


# ------------------------------------------------------------------ envelope followers

@njit(cache=True)
def _follow(x, a_att, a_rel):
    y = np.empty_like(x)
    cur = 0.0
    for i in range(len(x)):
        v = x[i]
        a = a_att if v > cur else a_rel
        cur = v + (cur - v) * a
        y[i] = cur
    return y


def follower_db(x, attack_ms, release_ms, D=16):
    """Envelope (dB) of a mono signal: mean square over blocks of D samples, attack/release one-pole, back to full
    rate. Returns (n,) dB."""
    n = len(x)
    m = n // D + 1
    xp = np.pad(x.astype(np.float64), (0, m * D - n))
    ms = (xp.reshape(m, D) ** 2).mean(1)
    fs = SR / D
    aa = np.exp(-1.0 / max(attack_ms / 1000 * fs, 1e-3))
    ar = np.exp(-1.0 / max(release_ms / 1000 * fs, 1e-3))
    env = _follow(ms, aa, ar)
    e = 10 * np.log10(env + 1e-12)
    return np.interp(np.arange(n) / D, np.arange(m), e)


# ------------------------------------------------------------------ ott

# The Ableton Live "OTT" Multiband Dynamics preset: crossovers 88.3 Hz and 2.5 kHz, input +5.2 dB per band,
# above-threshold ratio 66.7:1 (low, mid) and inf:1 (high), below-threshold upward ratio 4:1, output +10.3 / +5.7 /
# +10.3 dB (EDMProd, "OTT tutorial"); thresholds (above, below) low -33.8 / -40.8, mid -30.2 / -41.8, high -35.5 /
# -40.8 dB, whose gaps (7.0, 11.6, 5.3 dB) are the uncompressed windows MusicRadar gives; attack and release per band
# (47.8 / 282, 22.4 / 282, 13.5 / 132 ms: faster toward the highs, as MusicRadar describes) are [H].
OTT_BANDS = [dict(thr_a=-33.8, thr_b=-40.8, ra=66.7, att=47.8, rel=282.0, out=10.3),
             dict(thr_a=-30.2, thr_b=-41.8, ra=66.7, att=22.4, rel=282.0, out=5.7),
             dict(thr_a=-35.5, thr_b=-40.8, ra=1000.0, att=13.5, rel=132.0, out=10.3)]


def ott(st, fx):
    """fx: depth 0-1 (0.5; dry/wet), time (1.0; scales attack and release), upward 0-1 (1), downward 0-1 (1),
    rb (4; the upward ratio), max_up_db (24; a cap on the upward gain so silence is not lifted), in_ref (-18; the
    level, dBFS RMS of the active signal, the input is brought to before the thresholds: the preset's thresholds assume
    a full-scale signal, so the effect does not change with gain_db), makeup ("auto": the output RMS is matched to the
    input, so OTT changes density and tone, not level; or a number of dB), low/mid/high (dB, output trim per band)."""
    depth = float(fx.get("depth", 0.5))
    if depth <= 0:
        return st
    x = st.astype(np.float64)
    mono = x.mean(0)
    absm = np.abs(mono)
    act = absm > absm.max() * 1e-3 if absm.max() > 0 else absm > 0
    rms = np.sqrt(np.mean(mono[act] ** 2)) if act.any() else 0.0
    if rms <= 0:
        return st
    g_in = db(float(fx.get("in_ref", -18.0))) / rms
    xn = x * g_in * db(5.2)
    low, rest = _lr4(xn, 88.3)
    mid, high = _lr4(rest, 2500.0)
    tm = float(fx.get("time", 1.0))
    up, down = float(fx.get("upward", 1.0)), float(fx.get("downward", 1.0))
    rb = float(fx.get("rb", 4.0))
    cap = float(fx.get("max_up_db", 24.0))
    wet = np.zeros_like(xn)
    for band, B, trim in zip((low, mid, high), OTT_BANDS, (fx.get("low", 0), fx.get("mid", 0), fx.get("high", 0))):
        e = follower_db(band.mean(0) if band.ndim == 2 else band, B["att"] * tm, B["rel"] * tm)
        gdown = np.where(e > B["thr_a"], (e - B["thr_a"]) * (1 / B["ra"] - 1), 0.0) * down
        gup = np.where(e < B["thr_b"], np.minimum((B["thr_b"] - e) * (1 - 1 / rb), cap), 0.0) * up
        gup = np.where(e < -90, 0.0, gup)
        g = db(gdown + gup + B["out"] + float(trim))
        wet += band * g
    y = xn * (1 - depth) + wet * depth
    y = y / (g_in * db(5.2))
    mk = fx.get("makeup", "auto")
    if mk == "auto":
        r_in = np.sqrt(np.mean(x[:, act] ** 2))
        r_out = np.sqrt(np.mean(y[:, act] ** 2))
        if r_out > 0:
            y *= r_in / r_out
    else:
        y *= db(float(mk))
    return y.astype(np.float32)


# ------------------------------------------------------------------ dyneq (keyed by another track's hits)

def key_gain(events, n, depth_db, attack_ms=2.0, hold_ms=30.0, release_ms=120.0):
    """A gain curve (dB, <= 0) that falls to depth_db at each of the key's hits (scaled by its velocity), holds, and
    recovers over release_ms."""
    g = np.zeros(n)
    att, hold = max(1, int(attack_ms / 1000 * SR)), int(hold_ms / 1000 * SR)
    rel = release_ms / 1000
    k = np.arange(int(rel * 5 * SR)) / SR
    shape = np.concatenate([np.linspace(0, 1, att, endpoint=False), np.ones(hold), np.exp(-k / max(rel, 1e-3))])
    for e in events:
        i = int(e["t"] * SR) - att
        if i >= n or i + len(shape) <= 0:
            continue
        a = max(i, 0)
        m = min(len(shape) - (a - i), n - a)
        v = shape[a - i:a - i + m] * depth_db * min(1.0, float(e.get("vel", 1.0)) / 0.8)
        g[a:a + m] = np.minimum(g[a:a + m], v)
    return g


def dyneq(st, fx, events):
    """fx: hz, q (1.4), depth_db (-6), key (a track name), attack_ms (2), hold_ms (30), release_ms (120). The band
    around hz is lowered by depth_db while the key plays: H = 1 + (G(t) - 1) x BP (a peak filter whose gain moves)."""
    key = fx.get("key")
    if key not in events:
        raise ValueError(f"dyneq: key '{key}' is not a track with events")
    n = st.shape[1]
    gdb = key_gain(events[key], n, float(fx.get("depth_db", -6.0)), float(fx.get("attack_ms", 2.0)),
                   float(fx.get("hold_ms", 30.0)), float(fx.get("release_ms", 120.0)))
    fc, q = float(fx.get("hz", 55.0)), float(fx.get("q", 1.4))
    w = 2 * np.pi * fc / SR
    al = np.sin(w) / (2 * q)
    b = np.array([al, 0, -al]) / (1 + al)
    a = np.array([1 + al, -2 * np.cos(w), 1 - al]) / (1 + al)
    bp = signal.lfilter(b, a, st.astype(np.float64), axis=-1)
    return (st + (db(gdb) - 1)[None, :] * bp).astype(np.float32)


# ------------------------------------------------------------------ clip

def clip(st, fx):
    """Soft clipper, 4x oversampled. drive_db (0; gain into the clipper), ceiling_db (-1 dBFS), knee 0-1 (0.4; how
    far under the ceiling the curve starts to bend), out_db (0)."""
    x = st.astype(np.float64) * db(float(fx.get("drive_db", 0.0)))
    c = db(float(fx.get("ceiling_db", -1.0)))
    thr = c * (1 - float(np.clip(fx.get("knee", 0.4), 0.0, 0.99)))
    up = signal.resample_poly(x, 4, 1, axis=-1)
    a = np.abs(up)
    over = a > thr
    up[over] = np.sign(up[over]) * (thr + (c - thr) * np.tanh((a[over] - thr) / (c - thr)))
    y = signal.resample_poly(up, 1, 4, axis=-1)[:, :st.shape[1]]
    return (y * db(float(fx.get("out_db", 0.0)))).astype(np.float32)


# ------------------------------------------------------------------ mid/side

def mseq(st, fx, apply):
    """fx: mid (an fx list for the mid), side (an fx list for the side), side_hpf (Hz: the side high-passed, 12 dB/oct;
    keeps a layer's lows mono), mid_db, side_db."""
    m = (st[0] + st[1]) * 0.5
    s = (st[0] - st[1]) * 0.5
    if fx.get("mid"):
        m = apply(np.stack([m, m]).astype(np.float32), fx["mid"])[0]
    if fx.get("side"):
        s = apply(np.stack([s, s]).astype(np.float32), fx["side"])[0]
    if fx.get("side_hpf"):
        s = butter(s.astype(np.float32), "hpf", fx["side_hpf"], 12)
    m = m * db(float(fx.get("mid_db", 0.0)))
    s = s * db(float(fx.get("side_db", 0.0)))
    return np.stack([m + s, m - s]).astype(np.float32)


# ------------------------------------------------------------------ returns

def duck_curve(key_env_db, depth_db, attack_ms=10.0, release_ms=250.0):
    """Gain (linear) for a return ducked by a key: key_env_db is the key's mono envelope in dB (already followed);
    the return falls by depth_db x (how near the key is to its own loud level: 0 at 30 dB under its 95th percentile,
    1 at it)."""
    e = key_env_db
    ref = np.percentile(e[e > -100], 95) if np.any(e > -100) else 0.0
    amt = np.clip((e - (ref - 30.0)) / 30.0, 0, 1)
    return db(-abs(depth_db) * amt)


def predelay(x, ms):
    k = int(ms / 1000 * SR)
    if k <= 0:
        return x
    y = np.zeros_like(x)
    y[:, k:] = x[:, :-k]
    return y


def pingpong(x, beat_s, beats, feedback, offset_ms=0.0, lpf=None):
    """A ping-pong delay: the mono input bounces left, right, left... every `beats` beats (plus offset_ms, off the
    grid on purpose), each repeat x feedback."""
    d = int((beats * beat_s + offset_ms / 1000) * SR)
    n = x.shape[1]
    mono = x.mean(0)
    y = np.zeros((2, n), dtype=np.float32)
    g = 1.0
    k = 1
    sos = signal.butter(2, lpf, fs=SR, output="sos") if lpf else None
    cur = mono.astype(np.float64)
    while g > 0.003 and k * d < n:
        if sos is not None:
            cur = signal.sosfilt(sos, cur)
        ch = (k - 1) % 2
        y[ch, k * d:] += (cur[:n - k * d] * g).astype(np.float32)
        g *= feedback
        k += 1
    return y


# ------------------------------------------------------------------ correlated humanizing

def _pink(n, beta, rng):
    """Gaussian noise with a 1/f^beta power spectrum, unit standard deviation (spectral synthesis)."""
    if n < 4:
        return np.zeros(n)
    f = np.fft.rfftfreq(n)
    amp = np.zeros_like(f)
    amp[1:] = f[1:] ** (-beta / 2)
    ph = rng.uniform(0, 2 * np.pi, len(f))
    x = np.fft.irfft(amp * np.exp(1j * ph), n)
    x -= x.mean()
    s = x.std()
    return x / s if s > 0 else x


def humanize_curves(seed, name, total, bar, h):
    """Timing (s) and velocity (factor) deviation as functions of song time for one track. h: the track's `humanize`
    dict: ms (4; standard deviation of the timing drift), beta (1.0; 1/f^beta: 0 = independent jitter, 1 = pink,
    long-range correlated, as human players' deviations are: Hennig et al. 2011), phrase_bars (4) and phrase_ms (0;
    each phrase pushed or pulled by a random amount of that size, joined smoothly), vel (0; standard deviation of a
    correlated velocity drift, a fraction), seed (another draw)."""
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, zlib.crc32(name.encode("utf-8")), 2, int(h.get("seed", 0))])
    step = bar / 16
    n = int(total / step) + 8
    grid = np.arange(n) * step
    ms = float(h.get("ms", 4.0)) / 1000
    beta = float(h.get("beta", 1.0))
    dt = _pink(n, beta, rng) * ms
    dt = np.clip(dt, -2.5 * ms, 2.5 * ms) if ms > 0 else dt
    pms = float(h.get("phrase_ms", 0.0)) / 1000
    if pms > 0:
        pb = max(1, int(h.get("phrase_bars", 4))) * 16
        k = n // pb + 2
        offs = rng.normal(0, pms, k)
        pos = np.arange(n) / pb
        i = np.floor(pos).astype(int)
        fr = pos - i
        x = np.clip((fr - 0.875) / 0.125, 0, 1)            # glide into the next phrase over its last eighth
        w = 0.5 - 0.5 * np.cos(np.pi * x)
        dt = dt + offs[i] * (1 - w) + offs[i + 1] * w
    vel = float(h.get("vel", 0.0))
    dv = 1 + _pink(n, beta, rng) * vel if vel > 0 else np.ones(n)
    return grid, dt, dv


def apply_humanize(P, events, tracks, total, bar):
    """Correlated humanizing for every track whose `humanize` is a dict (the hand skipped its independent jitter)."""
    for name, tr in tracks.items():
        h = tr.get("humanize")
        if not isinstance(h, dict) or not events.get(name):
            continue
        grid, dt, dv = humanize_curves(P.get("seed", 1), name, total, bar, h)
        for e in events[name]:
            t = e["t"]
            e["t"] = t + float(np.interp(t, grid, dt))
            if "vel" in e and h.get("vel"):
                e["vel"] = float(np.clip(e["vel"] * np.interp(t, grid, dv), 0.03, 1.0))
