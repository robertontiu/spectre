"""violin: a bowed violin for solo lines, physically modelled (lăutar fiddle and classical violin).

The string is a digital waveguide bowed through a friction curve (McIntyre, Schumacher & Woodhouse 1983; Smith 1986;
the STK `Bowed` model by Cook & Scavone): the bow sticks and slips, so Helmholtz motion, the scratch of the first
periods, bow changes, slurred finger changes and slides all happen in the string itself rather than being painted on.
A second string plays double stops. The body is a modal impulse response (the A0 air mode near 275 Hz, the B1-/B1+
corpus modes near 470/540 Hz, dense modes above 1 kHz under a 2-3 kHz "bridge hill"; Woodhouse 2014, Bissinger 2008),
applied to the whole track afterwards (`body`, the track's POST processor), so vibrato makes the harmonics move through
the body's peaks the way a real violin shimmers.

Notes come from instruments.mono_voice: dict(t0, n, f, vel, glide, [art]). `art` is the list of articulations
written after the note length in the pattern (`"0:D5:4/g-1,tr+1"`, see docs/MANUAL.md, "Violin"):
  s          slurred to the previous note (same bow, finger change only)
  g, g-1, g+2, g=C#5   grace note (acciaccatura) a semitone below (default), or the interval/note given
  m, m+1, m-2          mordent: main, neighbour, main (default +2)
  tr, tr+1, tr+2       trill with the upper neighbour (default +2)
  ftr, ftr+1           "false lăutar trill": a bowed tremolo with brief touches of the upper note
  trem                 bowed tremolo (fast bow changes)
  turn                 gruppetto: upper, main, lower, main
  sl, sl-3, sl+2       slide into the note from N semitones away (default -2)
  fall, fall-4         terminal glissando: slide off the end of the note (default -3)
  sp                   spiccato: the bow bounces off, the string rings
  pz                   pizzicato
  h                    natural harmonic (flageolet): glassy, no vibrato
  nv                   no vibrato on this note; vib = extra vibrato
  d-5, d+3, d=A4       double stop: a second string at the interval or note given (same bow)
  up, dn               bow direction for this stroke
  acc                  a bitten accent (also `!` on the length)
  cresc, dim, swell    bow speed and force grow across the note, fade, or swell and fade (messa di voce)
"""
import numpy as np
from scipy import signal

try:
    from numba import njit
except Exception:  # pragma: no cover - numba ships with librosa; keep a slow path just in case
    def njit(*a, **k):
        def wrap(f):
            return f
        return wrap if not (a and callable(a[0])) else a[0]

SR = 44100
BUF = 8192          # waveguide buffer (lowest note ~ 11 Hz: plenty)
COMP = 1.45         # loop delay of the bridge filter and interpolation at pole 0.63 (calibrated, G3-E6)


def _comp(pole):
    """Loop-delay compensation: the bridge low-pass delays the low harmonics by about pole / (1 - pole) samples."""
    return COMP + pole / (1 - pole) - 0.63 / 0.37 - 0.52 * (0.63 - pole)


@njit(cache=True)
def _string(L, beta, vb, slope, contact, pluck, noise_amt, loss, pole, seed):
    """One bowed string. Per-sample control arrays: L total loop delay (samples), beta bow position (0-0.5),
    vb bow velocity (signed), slope of the friction curve (bow force: 5 - 4*pressure), contact 0/1 (bow on the string),
    pluck (an impulse injected into the string). Returns the force on the bridge."""
    np.random.seed(seed)
    n = L.shape[0]
    out = np.zeros(n, dtype=np.float32)
    neck = np.zeros(BUF)
    brid = np.zeros(BUF)
    w = 0
    lps = 0.0
    for i in range(n):
        Li = L[i]
        Lb = Li * beta[i]
        Ln = Li - Lb
        # fractional reads (linear interpolation)
        rb = w - Lb
        ib = int(np.floor(rb))
        fb = rb - ib
        bo = brid[ib % BUF] * (1 - fb) + brid[(ib + 1) % BUF] * fb
        rn = w - Ln
        inn = int(np.floor(rn))
        fn = rn - inn
        no = neck[inn % BUF] * (1 - fn) + neck[(inn + 1) % BUF] * fn
        # bridge: one-pole low-pass loss, inverting reflection; nut: inverting reflection
        lps = (1 - pole) * bo + pole * lps
        bref = -loss * lps
        nref = -no
        vs = bref + nref
        newv = 0.0
        if contact[i] > 0:
            v = vb[i]
            if noise_amt > 0:
                v += noise_amt * np.random.randn() * (abs(v) + 0.002)
            dv = v - vs
            x = (dv + 0.001) * slope[i]
            r = (abs(x) + 0.75) ** -4.0
            if r > 0.98:
                r = 0.98
            elif r < 0.01:
                r = 0.01
            newv = dv * r * contact[i]
        p = pluck[i]
        neck[w % BUF] = bref + newv + p
        brid[w % BUF] = nref + newv + p
        out[i] = bo
        w += 1
    return out


def _smooth(x, ms):
    k = max(1, int(ms / 1000 * SR))
    if k <= 1:
        return x
    win = np.hanning(2 * k + 1)
    win /= win.sum()
    return np.convolve(np.pad(x, (k, k), mode="edge"), win, mode="valid")


def _parse_art(art):
    """['g-1', 'tr+1'] -> dict(kind -> value)."""
    out = {}
    for a in art or []:
        a = a.strip()
        if not a:
            continue
        for key in ("ftr", "trem", "turn", "fall", "tr", "sl", "sp", "pz", "nv", "vib", "up", "dn", "acc", "g", "m",
                    "h", "d", "s", "cresc", "dim", "swell"):
            if a == key or (a.startswith(key) and a[len(key)] in "+-="):
                rest = a[len(key):]
                out[key] = rest if rest else True
                break
        else:
            raise ValueError(f"violin: unknown articulation '{a}'")
    return out


def _interval(v, default, base_midi=None):
    """'+2' -> 2, '-1' -> -1, '=C#5' -> semitones from base, True -> default."""
    if v is True or v is None or v == "":
        return default
    if isinstance(v, str) and v.startswith("="):
        from hand import note_to_midi
        return note_to_midi(v[1:]) - base_midi
    return float(v)


def violin_line(p, notes, total_n):
    """Render the whole violin track (mono, before the body)."""
    seed = int(p.get("seed", 7))
    rng = np.random.default_rng(seed)
    n_all = total_n
    # control arrays (string A = the melody, string B = double stops)
    L = np.full(n_all, SR / 196.0 - COMP)
    vb = np.zeros(n_all)
    slope = np.full(n_all, 3.0)
    contact = np.zeros(n_all)
    beta = np.full(n_all, p.get("bow_pos", 0.12))
    pluck = np.zeros(n_all)
    LB = np.full(n_all, SR / 293.66 - COMP)
    vbB = np.zeros(n_all)
    contactB = np.zeros(n_all)
    usedB = False
    harm = np.zeros(n_all, dtype=np.float32)

    pressure = float(p.get("pressure", 0.7))
    cold = float(p.get("cold", 0.0))
    vdepth0 = float(p.get("vibrato", 0.28)) * (1 - 0.55 * cold)   # semitones (peak), lăutar vibrato is wide and slow
    vrate0 = float(p.get("vib_rate", 5.4))
    vdelay = float(p.get("vib_delay", 0.12)) * (1 + 0.8 * cold)
    vgrow = float(p.get("vib_grow", 0.3))
    glide_s = float(p.get("glide_ms", 110)) / 1000
    grace_s = float(p.get("grace_ms", 45)) / 1000
    grace_at = p.get("grace_at", "before")
    trill_hz = float(p.get("trill_hz", 13.0))
    trem_hz = float(p.get("trem_hz", 14.0))
    attack0 = float(p.get("attack", 0.03))
    release = float(p.get("release", 0.06))
    ring = float(p.get("ring", 0.5))
    inton = float(p.get("intonation", 0.6))
    bowv = float(p.get("bow_speed", 1.0))

    # log-pitch track: semitone offsets per sample relative to each note
    semis = np.full(n_all, np.nan)
    vibenv = np.zeros(n_all)

    def put_pitch(a, b, midi):
        semis[a:b] = midi

    notes = sorted(notes, key=lambda x: x["t0"])
    midis = [69 + 12 * np.log2(nt["f"] / 440.0) for nt in notes]
    direction = 1.0
    prev_end = -10 ** 9
    for i, nt in enumerate(notes):
        art = _parse_art(nt.get("art"))
        m0 = midis[i]
        s = int(nt["t0"])
        e = s + int(nt["n"])
        nxt = int(notes[i + 1]["t0"]) if i + 1 < len(notes) else None
        if nxt is not None:
            e = min(e, nxt)
        # expressive intonation: leading tones lean up into their resolution, upper neighbours lean down
        if i + 1 < len(notes) and inton > 0 and nxt - e < int(0.25 * SR):
            step = round(midis[i + 1] - m0)
            if step == 1:
                m0 += 0.12 * inton
            elif step == -1:
                m0 -= 0.06 * inton
        g_iv = None
        if "g" in art:
            g_iv = _interval(art["g"], -1, round(m0))
            gl = int(grace_s * SR)
            if grace_at == "before":
                s = max(s - gl, 0)
        s = max(s, 0)
        if s >= n_all:
            break
        e = min(max(e, s + 64), n_all)
        dur = (e - s) / SR
        slurred = ("s" in art) or bool(nt.get("glide"))
        adjacent = s - prev_end < int(0.03 * SR)
        new_stroke = not (slurred and adjacent)
        if new_stroke:
            if "up" in art:
                direction = -1.0
            elif "dn" in art:
                direction = 1.0
            elif adjacent:
                direction = -direction
            else:
                direction = 1.0 if dur > 0.25 or i == 0 else -direction
        # ---- pitch contour
        put_pitch(s, e, m0)
        k = s
        if g_iv is not None:
            gl = min(int(grace_s * SR), (e - s) // 2)
            semis[s:s + gl] = m0 + g_iv
            k = s + gl
        if "sl" in art:
            iv = _interval(art["sl"], -2.0, round(m0))
            sl = min(int(0.075 * SR), (e - k) // 2)
            x = np.linspace(0, 1, sl)
            semis[k:k + sl] = m0 + iv * (1 - x * x * (3 - 2 * x))
        if nt.get("glide") and i > 0:
            gl = min(int(glide_s * SR), (e - s))
            x = np.linspace(0, 1, gl)
            sh = x * x * (3 - 2 * x)          # a finger slide: slow start, fast middle, settle
            semis[s:s + gl] = midis[i - 1] + (m0 - midis[i - 1]) * sh
        if "m" in art:
            iv = _interval(art["m"], 2.0, round(m0))
            a1, a2 = int(0.022 * SR), int(0.028 * SR)
            semis[k + a1:k + a1 + a2] = m0 + iv
        if "turn" in art:
            seg = int(0.03 * SR)
            semis[k:k + seg] = m0 + 2
            semis[k + 2 * seg:k + 3 * seg] = m0 - 1
        if "tr" in art:
            iv = _interval(art["tr"], 2.0, round(m0))
            per = int(SR / trill_hz / 2)
            stop = e - int(0.06 * SR)
            j = k + per
            while j < stop:
                semis[j:min(j + per, stop)] = m0 + iv
                j += 2 * per
        if "fall" in art:
            iv = _interval(art["fall"], -3.0, round(m0))
            fl = min(int(0.12 * SR), (e - s) // 2)
            x = np.linspace(0, 1, fl)
            semis[e - fl:e] = m0 + iv * x ** 2
        # ---- vibrato depth envelope (develops after the onset; short notes get none)
        if not ("nv" in art or "h" in art or "pz" in art or "tr" in art or "sp" in art) and dur > 0.16:
            t = np.arange(e - s) / SR
            depth = vdepth0 * rng.uniform(0.85, 1.15) * (1.35 if "vib" in art else 1.0)
            env = np.clip((t - vdelay) / 0.25, 0, 1) * (1 + vgrow * np.clip((t - vdelay) / 1.5, 0, 1))
            vibenv[s:e] = depth * env
        # ---- bow: velocity, force, contact
        V = (0.035 + 0.11 * nt["vel"]) * bowv      # above ~0.16 the string breaks into higher modes
        acc = ("acc" in art) or nt["vel"] > 0.92
        att = 0.012 if acc else float(nt.get("attack", attack0))  # per-note attack: only set by strings_section
        P = pressure + 0.12 * (nt["vel"] - 0.7) + 0.12 * float(np.clip((m0 - 80) / 10, 0, 1))  # high notes need force
        if "pz" in art:
            pluck[s:s + 24] += np.hanning(24) * (0.4 + 0.6 * nt["vel"])
            contact[s:e] = 0
            prev_end = e
            continue
        if "h" in art:  # flageolet: the finger lightly touches a node; the string sounds a pure partial
            t = np.arange(e - s) / SR
            f = 440 * 2 ** ((m0 - 69) / 12)
            ph = 2 * np.pi * f * t
            env = np.minimum(t / 0.04, 1) * np.minimum((e - s - np.arange(e - s)) / (0.08 * SR), 1)
            hn = np.random.default_rng(seed + i).standard_normal(e - s)
            hn = signal.sosfilt(signal.butter(2, [f * 0.9, min(f * 6, 16000)], btype="band", fs=SR, output="sos"), hn)
            harm[s:e] += ((np.sin(ph) + 0.06 * np.sin(2 * ph) + 0.03 * np.sin(3 * ph) + 0.04 * hn) * env * 0.3
                          * (0.5 + nt["vel"]) * (1 + 0.04 * np.sin(2 * np.pi * 5.0 * t))).astype(np.float32)
            contact[s:e] = 0
            prev_end = e
            continue
        n = e - s
        t = np.arange(n) / SR
        if new_stroke:
            if adjacent and not acc:  # a bow change inside a phrase: the bow reverses quickly
                att = min(att, 0.014)
            up = np.minimum(t / att, 1.0) ** 1.5
        else:
            up = np.ones(n)
        if "sp" in art:  # spiccato: the bow drops, bites and leaves; the string rings on its own
            off = min(n, int(0.055 * SR))
            v = np.zeros(n)
            v[:off] = V * 1.1 * np.sin(np.pi * np.arange(off) / off)
            vb[s:e] = direction * v
            contact[s:s + off] = 1
            slope[s:e] = 5 - 4 * min(P + 0.15, 0.95)
            prev_end = e
            continue
        # a long note breathes (a small swell), a short one decays a little after the attack
        shape = 1 - 0.12 * np.clip(t / max(dur, 0.05), 0, 1) if dur < 0.6 else 1 + 0.08 * np.sin(np.pi * np.clip(t / dur, 0, 1))
        v = V * up * shape
        benv = None
        if "cresc" in art or "dim" in art or "swell" in art:  # a bow-speed and force envelope across the note
            u = np.clip(t / max(dur, 0.05), 0, 1)
            if "cresc" in art:
                benv = 0.3 + 0.7 * u ** 1.5
            elif "dim" in art:
                benv = 1.0 - 0.7 * u ** 0.8
            else:
                benv = 0.3 + 0.7 * np.sin(np.pi * u) ** 1.2
            v = v * benv
        end_adj = nxt is not None and nxt - e < int(0.03 * SR)
        next_slurred = end_adj and i + 1 < len(notes) and (
            "s" in (notes[i + 1].get("art") or []) or notes[i + 1].get("glide"))
        if not next_slurred:
            fade = min(n // 3, int((0.009 if end_adj else release) * SR))
            if fade > 1:
                v[-fade:] *= np.linspace(1, 0, fade) ** (1.0 if end_adj else 1.5)
        if "trem" in art or "ftr" in art:
            hz = trem_hz * (1.15 if "ftr" in art else 1.0)
            ph = np.floor(t * hz)
            v = v * np.where(ph % 2 == 0, 1.0, -1.0) * np.minimum(np.abs(np.sin(np.pi * t * hz)) * 4, 1)
            if "ftr" in art:
                iv = _interval(art["ftr"], 2.0, round(m0))
                touch = (ph % 2 == 1) & ((t * hz) % 1 < 0.35)
                semis[s:e] = np.where(touch, m0 + iv, semis[s:e])
        vb[s:e] = direction * v
        contact[s:e] = 1
        sl_arr = np.full(n, 5 - 4 * float(np.clip(P, 0.05, 0.95)))
        if benv is not None:  # softer bow, lighter force (keeps the Helmholtz motion stable through the swell)
            sl_arr = 5 - 4 * np.clip(P - 0.25 * (1 - benv), 0.05, 0.95)
        if acc and new_stroke:  # bite: more force for the first periods
            sl_arr = sl_arr - 1.2 * np.exp(-t / 0.03)
        slope[s:e] = sl_arr
        # after the note: lift the bow (the string rings) or stop it on the string
        if not end_adj:
            stop_until = min(n_all, e + int(0.05 * SR)) if nxt is None else min(nxt, e + int(0.05 * SR))
            if rng.random() > ring:
                contact[e:stop_until] = 1  # bow resting on the string: a damped stop
                vb[e:stop_until] = 0
        # double stop on string B (same bow)
        if "d" in art:
            iv = _interval(art["d"], -5.0, round(m0))
            LB[s:e] = SR / (440 * 2 ** ((m0 + iv - 69) / 12)) - COMP
            vbB[s:e] = vb[s:e] * 0.9
            contactB[s:e] = 1
            usedB = True
        prev_end = e
    # vibrato: one continuous oscillator whose rate wanders a little; depth from the per-note envelopes
    drift = np.convolve(rng.standard_normal(n_all // 2205 + 12), np.hanning(9) / np.hanning(9).sum(), mode="same")
    rate = vrate0 * (1 + 0.06 * np.interp(np.arange(n_all) / 2205, np.arange(len(drift)), drift))
    vph = 2 * np.pi * np.cumsum(rate) / SR
    idx = np.where(np.isnan(semis), 0, np.arange(n_all))
    np.maximum.accumulate(idx, out=idx)
    semis = semis[idx]
    first = np.flatnonzero(~np.isnan(semis))
    semis = np.where(np.isnan(semis), semis[first[0]] if len(first) else 67.0, semis)
    semis = _smooth(semis, 2.5) + vibenv * np.sin(vph)
    f = 440 * 2 ** ((semis - 69 + (1.5 + float(p.get("tune_cents", 0.0))) / 100) / 12)  # +1.5 c: bow-force flattening
    # bow noise and string losses
    noise_amt = float(p.get("bow_noise", 0.35)) * 0.02
    loss = 0.995 - 0.03 * float(p.get("damp", 0.3))
    pole = 0.35 + 0.3 * float(p.get("dark", 0.3))
    comp = _comp(pole)
    L = SR / f - comp
    LB = LB + COMP - comp
    out = _string(L, beta, _smooth(vb, 1.5), slope, contact, pluck, noise_amt, loss, pole, seed)
    if usedB:
        out = out + _string(LB, beta, _smooth(vbB, 1.5), slope, contactB, np.zeros(n_all), noise_amt, loss, pole,
                            seed + 1)
    out = out * 4.0 + harm
    return np.nan_to_num(out).astype(np.float32)


_BODY = {}


def _shelf(f0, gain_db, slope=0.8):
    """RBJ high shelf as one second-order section."""
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / 2 * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2)
    c = np.cos(w)
    b = [A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * c),
         A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al)]
    a = [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al]
    return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])


def body_ir(variant=0, cold=0.0, warm=0.5):
    """Modal body impulse response (0.35 s): signature modes plus dense higher modes under a bridge hill."""
    key = (int(variant), round(cold, 3), round(warm, 3))
    if key in _BODY:
        return _BODY[key]
    rng = np.random.default_rng(100 + int(variant))
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    # (freq Hz, relative level dB, Q): A0 air mode, CBR, B1-, B1+ (Woodhouse 2014; Bissinger 2008)
    sig = [(275, -8 + 3 * warm - 4 * cold, 12), (425, -11, 15), (470, -6 + 2 * warm - 3 * cold, 16),
           (540, -5 - 2 * cold, 16), (700, -9, 18), (830, -8, 20)]
    modes = list(sig)
    f = 900.0
    while f < 9000:  # dense modes, ~ 4-6 per 1/3 octave, under a bridge hill at 2-3 kHz
        f *= 2 ** rng.uniform(0.04, 0.11)
        hill = 7 * np.exp(-0.5 * (np.log2(f / 2800) / 0.6) ** 2)
        roll = -7 * max(0.0, np.log2(f / 5500))
        comp_q = 10 * np.log10(f / 1000)  # a mode's energy falls with its decay time (Q / pi f): keep bands level
        lvl = -10 + comp_q + hill + roll + rng.normal(0, 3.5) + 3 * cold * (f > 2500 and f < 5000)
        modes.append((f, lvl, rng.uniform(25, 55)))
    ir = np.zeros(n)
    for fr, lv, q in modes:
        ir += 10 ** (lv / 20) * np.exp(-np.pi * fr * t / q) * np.sin(2 * np.pi * fr * t + rng.uniform(0, 2 * np.pi))
    ir[0] += 0.4  # direct bridge drive (keeps the attack crisp)
    # radiation: a violin radiates its upper partials efficiently (the bridge hill and above); lift the modal sum
    ir = signal.sosfilt(_shelf(3000, 8.0), ir)
    ir = signal.sosfilt(_shelf(9000, 5.0), ir)
    ir /= np.sqrt((ir ** 2).sum()) * 6
    _BODY[key] = ir.astype(np.float32)
    return _BODY[key]


def body(p, x):
    """POST processor for a `violin` track: the wooden body, a DC block and the radiation's top roll-off."""
    ir = body_ir(p.get("body", 0), float(p.get("cold", 0.0)), float(p.get("warm", 0.5)))
    y = signal.oaconvolve(x, ir)[:len(x)]
    sos = signal.butter(2, 120, btype="high", fs=SR, output="sos")
    y = signal.sosfilt(sos, y)
    sos = signal.butter(2, 15000 - 4000 * float(p.get("dark", 0.3)), btype="low", fs=SR, output="sos")
    y = signal.sosfilt(sos, y)
    return y.astype(np.float32)
