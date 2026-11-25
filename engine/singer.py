"""Voices: `singer` (sings words) and `vox2` (the improved wordless voice).

`singer` sings words with a singing voice synthesizer: a DiffSinger voicebank (engine/svs.py; voices in
engine/voices.json and docs/voice/VOICES.md). This module is its entry point: it parses the lyric notation shared by
the studio and svs.py and dispatches to svs. `"source": "svs"` is the only source and the default, so a `singer`
track without `source` sings with svs too; any other `source` is an error (see docs/MANUAL.md "Voices").

`vox2` (below) is pure synthesis, no model: an LF glottal source, formant vowels and soft consonant onsets for
wordless lines and chops.
"""
import functools
import hashlib
import sys

import numpy as np
from scipy import signal

SR = 44100

_WARNED = set()


def _warn(msg):
    if msg not in _WARNED:
        _WARNED.add(msg)
        print("warning: singer: " + msg, file=sys.stderr)


def _seed(*parts):
    h = hashlib.sha1(repr(parts).encode()).digest()
    return int.from_bytes(h[:4], "little")


# ------------------------------------------------------------------ lyrics -> per-note syllables

def parse_lyrics(text):
    """'here you are, round and round _ a-round' -> list of tokens per note: (word, syllable index, n syllables)
    or '_' (hold the previous syllable over this note: a melisma). Punctuation is ignored."""
    toks = []
    for raw in str(text).replace("\n", " ").split():
        if raw in ("_", "~"):
            toks.append("_")
            continue
        wd = "".join(c for c in raw if c.isalnum() or c in "-'[]@:")
        if not wd:
            continue
        n = len([s for s in wd.split("-") if s])
        for i in range(n):
            toks.append((wd, i, n))
    return toks


# ------------------------------------------------------------------ the sung line

def sing(p, notes, total_n):
    """Render a sung line with the singing voice synthesizer (engine/svs.py). notes: list of dict(t0, n, f, vel,
    glide[, syl]). Returns mono, or stereo (2, N) when `double` > 0. `source` defaults to "svs", the only one."""
    src = p.get("source", "svs")
    if src != "svs":
        raise ValueError(f"singer: source {src!r} does not exist; the singer has one source, \"svs\" (the default: "
                         "DiffSinger voices, docs/MANUAL.md \"Voices\"). For a wordless line use vox or vox2")
    import svs
    return svs.sing(p, notes, total_n)


def _norm(y):
    """Gain that puts the sung parts (50 ms windows above -40 dB of the loudest) at 0.2 RMS, about where `vox`
    sits, so levels don't depend on the lyric or the melody."""
    w = int(0.05 * SR)
    n = len(y) // w
    if n == 0:
        return 1.0
    r = np.sqrt((y[:n * w].reshape(n, w) ** 2).mean(1))
    act = r[r > r.max() * 0.01]
    return 0.2 / max(float(np.sqrt((act ** 2).mean())) if len(act) else 1.0, 1e-9)


# ------------------------------------------------------------------ vox2: the improved wordless voice
# A from-scratch voice (no model, no recordings) for wordless lines and chops. Over `vox` it adds:
# - an LF-model glottal source (Fant, Liljencrants & Lin 1985) set by Fant's Rd "voice quality" parameter
#   (Fant 1995: about 0.3 pressed .. 1 modal .. 2.7 breathy), its harmonic spectrum taken from one synthesized period;
#   louder notes get a slightly tenser (brighter) source, as in real voices;
# - jitter (cycle-to-cycle pitch wobble) and shimmer (amplitude wobble), small and low-passed;
# - aspiration noise pulsed with each glottal cycle (breath that belongs to the voice instead of a hiss beside it);
# - vowel sequences: `vowels` "oo ah" etc. take one vowel per note in turn, with ~80 ms formant transitions;
# - soft consonant onsets for chops and wordless syllables (`onset`: h, m, n, l, w, y, d): formant targets that
#   move into the vowel plus a nasal murmur or a tiny burst.

def _lf_period(Rd, n=2048):
    """One period of the LF glottal flow derivative for voice quality Rd (Fant 1995 Rd -> Ra, Rk, Rg)."""
    Rd = float(np.clip(Rd, 0.3, 2.7))
    Ra = (-1 + 4.8 * Rd) / 100
    Rk = (22.4 + 11.8 * Rd) / 100
    Rg = 1 / (4 * ((0.11 * Rd / (0.5 + 1.2 * Rk)) - Ra) / Rk)
    T0 = 1.0
    tp = T0 / (2 * Rg)
    te = tp * (1 + Rk)
    ta = Ra * T0
    te = min(te, 0.98)
    wg = np.pi / tp
    # epsilon from the return-phase continuity eps*ta = 1 - exp(-eps*(T0-te))
    eps = 1 / ta
    for _ in range(50):
        eps = (1 - np.exp(-eps * (T0 - te))) / ta
    t = np.arange(n) / n
    # alpha such that the flow returns to zero over the period (solve numerically)
    def area(alpha):
        o = t < te
        e = np.where(o, np.exp(alpha * t) * np.sin(wg * t), 0.0)
        E0 = 1.0
        Ee = -np.exp(alpha * te) * np.sin(wg * te)
        r = np.where(~o, -Ee / (eps * ta) * (np.exp(-eps * (t - te)) - np.exp(-eps * (T0 - te))), 0.0)
        return e + r
    lo, hi = -50.0, 50.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if area(mid).sum() > 0:  # too much positive (opening) lobe: grow faster toward the closing lobe
            lo = mid
        else:
            hi = mid
    return area((lo + hi) / 2)


@functools.lru_cache(maxsize=64)
def _lf_harmonics(rd_q, K=80):
    """Harmonic magnitudes 1..K of the LF flow derivative for Rd (quantised to 0.05), normalised to harmonic 1."""
    g = _lf_period(rd_q / 20.0)
    S = np.abs(np.fft.rfft(g))[1:K + 1]
    return S / max(S[0], 1e-9)


_V2_ONSETS = {  # (F1, F2, F3) start targets, murmur 0-1, burst 0-1, breath 0-1, ms
    "h": (None, 0.0, 0.0, 1.0, 70), "m": ((250, 1000, 2200), 1.0, 0.0, 0.0, 70),
    "n": ((250, 1500, 2500), 1.0, 0.0, 0.0, 60), "l": ((350, 1100, 2600), 0.3, 0.0, 0.0, 70),
    "w": ((300, 650, 2200), 0.2, 0.0, 0.0, 90), "y": ((280, 2200, 2900), 0.2, 0.0, 0.0, 80),
    "d": ((300, 1700, 2600), 0.2, 1.0, 0.0, 40),
}


def vox2_line(p, notes, total_n):
    """Improved wordless voice (see the block comment above). Monophonic, legato with `~` glides."""
    from instruments import FORMANTS, _vowel, adsr, noise, bp  # noqa: F401  (shared formant tables)
    rng = np.random.default_rng(_seed("vox2", p.get("seed", 1), p.get("voice", "alto")))
    out = np.zeros(total_n)
    voice = p.get("voice", "alto")
    seq = str(p.get("vowels", p.get("vowel", "ah"))).split()
    onsets = str(p.get("onset", "")).split() or [""]
    vdepth, vrate, vdelay = p.get("vibrato", 0.3), p.get("vib_rate", 5.3), p.get("vib_delay", 0.25)
    glide_s = p.get("glide_ms", 90) / 1000
    breath = p.get("breath", 0.3)
    ring = p.get("ring", 0.5)
    rd0 = p.get("rd", 0.7)  # Fant's Rd: lower = tenser, brighter; higher = breathier, softer
    trans = p.get("transition_ms", 80) / 1000
    jit, shim = p.get("jitter", 0.006), p.get("shimmer", 0.06)
    prev_f, prev_phase, prevF = None, None, None
    D = 64
    for i, nt in enumerate(notes):
        start = nt["t0"]
        if start >= total_n:
            break
        nxt = notes[i + 1]["t0"] if i + 1 < len(notes) else None
        next_glides = nxt is not None and notes[i + 1].get("glide")
        rel = p.get("release", 0.16)
        length = nt["n"] + int(rel * SR)
        if nxt is not None:
            length = min(length, nxt - start + (0 if next_glides else int(0.006 * SR)))
        length = int(min(max(length, 32), total_n - start))
        t = np.arange(length) / SR
        glide = bool(nt.get("glide")) and prev_f is not None
        f = np.full(length, float(nt["f"]))
        if glide:
            f = prev_f * (nt["f"] / prev_f) ** np.clip(t / glide_s, 0, 1)
        else:
            f = f * 2 ** (-p.get("scoop", 0.5) * np.exp(-t / 0.045) / 12)
        vib = vdepth * np.sin(2 * np.pi * vrate * t + rng.random() * 6) * np.clip((t - vdelay) / 0.4, 0, 1)
        drift = np.interp(t, np.linspace(0, t[-1] + 1e-3, 6), rng.normal(0, 0.06, 6))
        jj = signal.lfilter([0.05], [1, -0.95], rng.normal(0, 1, length)) * jit * 12 / np.log(2) * 0.3
        f = f * 2 ** ((vib + drift) / 12 + jj / 12)
        ph = (prev_phase if (glide and prev_phase is not None) else 0.0) + 2 * np.pi * np.cumsum(f) / SR
        Fv, Bv = _vowel(voice, seq[i % len(seq)])
        ons = onsets[i % len(onsets)] if not glide else ""
        o = _V2_ONSETS.get(ons)
        td = t[::D]
        nd = len(td)
        # formant track: from the previous vowel (glide/legato) or the onset target into this vowel
        F = np.repeat(Fv[None, :], nd, 0)
        if o is not None and o[0] is not None:
            Fs = Fv.copy()
            Fs[:3] = o[0]
            w = np.clip(td / (o[4] / 1000), 0, 1)[:, None]
            F = Fs[None, :] * (1 - w) + Fv[None, :] * w
        elif prevF is not None and (glide or (nxt is not None and False)):
            w = np.clip(td / trans, 0, 1)[:, None]
            w = w * w * (3 - 2 * w)
            F = prevF[None, :] * (1 - w) + Fv[None, :] * w
        fd = f[::D]
        rd = float(np.clip(rd0 - 0.5 * (nt["vel"] - 0.7), 0.3, 2.7))
        H = _lf_harmonics(int(round(rd * 20)))
        K = int(max(1, min(len(H), 9500 / max(fd.min(), 40))))
        amps = np.zeros((K, nd))
        for k in range(1, K + 1):
            fk = k * fd
            h = np.ones(nd)
            for j in range(5):
                r = fk / F[:, j]
                h = h / np.sqrt((1 - r * r) ** 2 + (fk * Bv[j] * 1.4 / (F[:, j] ** 2)) ** 2)
            sf_ = 1 + ring * 4 * np.exp(-((fk - 2900) / 700) ** 2)
            amps[k - 1] = h * sf_ * H[k - 1] * (fk < 9500)  # the flow derivative already includes lip radiation
        norm = np.sqrt((amps[:, :8] ** 2).sum(0)).mean() + 1e-9
        idx = np.arange(length) / D
        x = np.zeros(length)
        for k in range(1, K + 1):
            x += np.interp(idx, np.arange(nd), amps[k - 1]) * np.sin(k * ph)
        x /= norm
        # aspiration: noise through F1-F3, pulsed with each glottal cycle
        pulse = 0.55 + 0.45 * np.cos(ph % (2 * np.pi))
        nz = rng.normal(0, 1, length)
        asp = (bp(nz, Fv[0] * 0.8, Fv[0] * 1.25) * 0.6 + bp(nz, Fv[1] * 0.85, Fv[1] * 1.2) * 0.8
               + bp(nz, 2400, 6500) * 0.25) * pulse * breath * 0.5
        env = adsr(min(nt["n"], length), p.get("attack", 0.05), 0.25, p.get("sustain_level", 0.85), rel)[:length]
        if len(env) < length:
            env = np.pad(env, (0, length - len(env)))
        if glide:
            env = np.maximum(env, 0.85 * (np.arange(length) < nt["n"]))
            h0 = min(nt["n"], length)
            env[h0:] = 0.85 * np.exp(-np.arange(length - h0) / max(int(rel / 5 * SR), 1))
        shimmer = 1 + shim * signal.lfilter([0.1], [1, -0.9], rng.normal(0, 1, length)) * 3
        y = (x * 0.5 * shimmer + asp) * env * nt["vel"]
        if o is not None:
            L = min(length, int(o[4] / 1000 * SR))
            if o[1] > 0:  # nasal/liquid murmur: muffle the start
                mur = signal.sosfilt(signal.butter(2, 400, "low", fs=SR, output="sos"), y[:L])
                wv = np.linspace(1, 0, L) ** 0.7 * o[1]
                y[:L] = y[:L] * (1 - wv) + mur * wv * 1.6
            if o[2] > 0:  # a tiny burst
                bL = min(length, int(0.012 * SR))
                y[:bL] += bp(rng.normal(0, 1, bL), 2500, 6000) * np.exp(-np.arange(bL) / (0.003 * SR)) * 0.15 * o[2]
        if o is not None and o[3] > 0:  # breath before the note
            L = int(o[4] / 1000 * SR)
            s = max(0, start - L)
            m = start - s
            if m > 16:
                hb = bp(rng.normal(0, 1, m), Fv[0], 5000) * np.linspace(0, 1, m) ** 2 * 0.08 * o[3] * nt["vel"]
                out[s:start] += hb
        if not glide:
            fade = min(64, length)
            y[:fade] *= np.linspace(0, 1, fade)
        if nxt is not None and not next_glides:
            fo = min(int(0.006 * SR), length)
            y[-fo:] *= np.linspace(1, 0, fo)
        out[start:start + length] += y
        j = (nxt - start) if nxt is not None else None
        prev_phase = float(ph[j - 1]) if (j is not None and 0 < j <= length) else None
        prev_f = nt["f"]
        prevF = Fv
    return out.astype(np.float32)
