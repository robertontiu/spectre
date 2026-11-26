"""Shared helpers for the techno fits and A/Bs (examples/production/techno/README.md): the references (engine/
third_party.json `refs-techno-cc0`, `refs-techno-ccby`, `refs-tr909-detroit`; measured only, never used in a track),
one-shot features (third-octave spectra in time windows, band decay times), and renders of engine sounds."""
import json
import os
import sys
import warnings

import numpy as np
from scipy import signal

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import instruments as I  # noqa: E402
import studio as ST  # noqa: E402

SR = 44100
CACHE = os.environ.get("SPECTRE_CACHE", os.path.expanduser("~/.cache/spectre"))
THIRD = np.array([25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
                  2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000])


def refs(role=None, ids=("refs-techno-cc0", "refs-techno-ccby", "refs-tr909-detroit")):
    m = json.load(open(os.path.join(REPO, "engine", "third_party.json")))
    out = []
    for r in m["resources"]:
        if r["id"] in ids:
            for f in r["files"]:
                if role is None or f["role"] == role:
                    out.append(dict(f, src=r["id"]))
    return out


def load(f):
    import librosa
    p = os.path.join(CACHE, f["path"])
    if not os.path.exists(p):
        raise SystemExit(f"missing {p}: python3 tools/engine_assets.py install refs-techno-cc0 refs-techno-ccby "
                         "refs-tr909-detroit")
    y, _ = librosa.load(p, sr=SR, mono=False)
    return np.stack([y, y]) if y.ndim == 1 else y


def mono(x):
    x = np.asarray(x, dtype=np.float64)
    return x.mean(0) if x.ndim == 2 else x


def onset(x, thr=0.05):
    m = mono(x)
    i = int(np.argmax(np.abs(m) > np.abs(m).max() * thr))
    return m[max(0, i - 20):]


def third_win(m, t0, t1, total):
    a, b = int(t0 * SR), int(t1 * SR)
    seg = np.pad(m, (0, max(0, b - len(m))))[a:b]
    X = np.abs(np.fft.rfft(seg, 2 ** 17)) ** 2
    f = np.fft.rfftfreq(2 ** 17, 1 / SR)
    s = np.array([X[(f >= c * 2 ** (-1 / 6)) & (f < c * 2 ** (1 / 6))].sum() for c in THIRD])
    return 10 * np.log10(s / total + 1e-12)


def total_power(m, dur):
    seg = np.pad(m, (0, max(0, int(dur * SR) - len(m))))[:int(dur * SR)]
    X = np.abs(np.fft.rfft(seg, 2 ** 17)) ** 2
    f = np.fft.rfftfreq(2 ** 17, 1 / SR)
    return X[(f >= THIRD[0] * 2 ** (-1 / 6)) & (f < THIRD[-1] * 2 ** (1 / 6))].sum()


def t20(m, lo, hi, ms=5):
    y = signal.sosfilt(signal.butter(4, [lo, min(hi, 21000)], btype="band", fs=SR, output="sos"), np.pad(m, (0, SR)))
    k = int(ms / 1000 * SR)
    n = len(y) // k
    e = np.sqrt((y[:n * k].reshape(n, k) ** 2).mean(1))
    j = int(np.argmax(e))
    e = 20 * np.log10(e / e[j] + 1e-9)
    below = np.where(e[j:] < -20)[0]
    return float((j + (below[0] if len(below) else len(e) - j)) * ms)


def feats(x, wins, bands):
    """One-shot features: third-octave powers of each time window (dB re the whole sound's power over all windows) and
    each band's time to fall 20 dB from the onset (ms)."""
    m = onset(x)
    tot = total_power(m, wins[-1][1])
    S = np.array([third_win(m, a, b, tot) for a, b in wins])
    T = np.array([t20(m, lo, hi) for lo, hi in bands])
    return S, T


def dist(F, R, floor=40.0, w_env=4.0):
    """Spectral RMS dB difference over the bands within `floor` dB of the reference's loudest band (all windows), plus
    w_env x the RMS of log2(model / reference) decay times (0.1 = about 7% off)."""
    S, T = F
    RS, RT = R
    ok = RS > RS.max() - floor
    d = np.where(ok, np.maximum(S, RS.max() - floor - 10) - RS, 0)
    spec = float(np.sqrt(np.sum(d ** 2) / ok.sum()))
    env = float(np.sqrt(np.mean(np.log2(np.maximum(T, 3) / np.maximum(RT, 3)) ** 2)))
    return spec, env, spec + w_env * env


def mean_feats(FS):
    S = 10 * np.log10(np.mean([10 ** (f[0] / 10) for f in FS], 0))
    T = np.exp(np.mean([np.log(np.maximum(f[1], 1)) for f in FS], 0))
    return S, T


def hit(kind, p, vel=0.9, seed=0, ps=0.0):
    I.RNG = np.random.default_rng(seed)
    return np.asarray(I.DRUMS[kind](p, vel, ps), dtype=np.float64)


def project(tracks, pats, bars, bpm=150, returns=None, extra=None):
    P = {"title": "techno-cmp", "bpm": bpm, "swing": 0.5, "seed": 7, "seeds": "per-track", "genre": "techno",
         "tracks": tracks, "patterns": pats, "arrangement": [{"name": "a", "bars": bars, "play": list(pats)}],
         "buses": {}, "mix": {"reverb": {"size": 0.6, "return_db": -60}, "returns": returns or {}},
         "master": {"lufs": -10.5}}
    if extra:
        P.update(extra)
    return P


def stems(P):
    st = {}
    ST.render(P, stem_hook=lambda nm, x: st.__setitem__(nm, x.copy()), quiet=True)
    return st


def minimize_log(f, x0, step=0.35, maxiter=400, restarts=2, verbose=""):
    """Nelder-Mead over z where x = x0 * exp(z) (every parameter positive), with a real initial simplex (`step` in log
    units: scipy's default simplex is 0.025% of a zero start) and restarts from the best point."""
    from scipy import optimize
    x0 = np.asarray(x0, dtype=float)
    n = len(x0)
    z = np.zeros(n)
    best = None
    for k in range(restarts):
        sim = np.vstack([z] + [z + step * np.eye(n)[i] * (1 if (i + k) % 2 == 0 else -1) for i in range(n)])
        r = optimize.minimize(lambda zz: f(x0 * np.exp(zz)), z, method="Nelder-Mead",
                              options=dict(maxiter=maxiter, initial_simplex=sim, xatol=1e-3, fatol=1e-3, adaptive=True))
        z = r.x
        best = r
        step *= 0.5
        if verbose:
            print(verbose, "pass", k, round(float(r.fun), 3), flush=True)
    return x0 * np.exp(best.x), float(best.fun)
