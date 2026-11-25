"""`acid`: a monophonic 303-style bass line (docs/TRANCE.md "Modern trance production", G 4 and I 3; docs/MANUAL.md
"Acid voice"). Additive: used only when a track's instrument is `acid`; it draws no random numbers.

What makes the TB-303 line (Roland TB-303 owner's manual and service notes; Stinchcombe 2008, "Analysis of the
Moog transistor ladder and derivative filters", for the diode ladder; Whittle, "TB-303 accent and slide", Firstpr
pages; Zavalishin 2018, "The Art of VA Filter Design", for the zero-delay ladder used here):
  - one saw (or square) oscillator into a resonant ladder low-pass: the 303's diode ladder is a 4-pole filter whose
    poles are not equal, heard as about 18 dB/oct; `slope` 18 (three equal poles) or 24 (four);
  - a filter envelope that only decays (`decay`), scaled by `env_mod`, retriggered on every note that does not slide;
  - accent: an accented note is louder and its envelope is forced to the shortest decay, and the accented envelope
    also charges a capacitor that adds to the cutoff and discharges slowly, so accents in a row climb ("the wow");
  - slide: a note tied into the next (`~` on the next note) holds the gate, does not retrigger the envelope, and its
    pitch moves on an RC lag of about 60 ms;
  - the VCA: a fast attack, held while the gate is up, a few ms of release when it falls.
The ladder is a zero-delay-feedback model with a tanh at its input, so high resonance compresses the low end the way
the hardware does and very high `reso` self-oscillates.
"""
import numpy as np

SR = 44100

try:
    from numba import njit
except Exception:  # pragma: no cover
    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


@njit(cache=True)
def _acid_kernel(tlf, gate, onset, trig, acc, slide, cut, envm, reso, dec, accamt, drive, vel, square, poles, slide_tau,
                 acc_decay, acc_rel, amp_att, amp_rel):
    n = len(tlf)
    y = np.zeros(n)
    lf = tlf[0]
    ph = 0.0
    fe = 0.0
    acs = 0.0     # the accent capacitor
    acs_s = 0.0   # its slewed value (the wow sweeps, it does not jump)
    amp = 0.0
    accg = 0.0
    s = np.zeros(4)
    a_sl = np.exp(-1.0 / (slide_tau * SR))
    a_acr = np.exp(-1.0 / (acc_rel * SR))
    a_slew = np.exp(-1.0 / (0.012 * SR))
    a_att = 1.0 / max(amp_att * SR, 1.0)
    a_rel = np.exp(-1.0 / max(amp_rel * SR, 1.0))
    cur_acc = 0.0
    for t in range(n):
        if onset[t] > 0:
            cur_acc = acc[t]
            if cur_acc > 0:
                acs = acs + accamt[t] * (1.0 - 0.5 * acs)
            if trig[t] > 0:
                fe = 1.0
        if slide[t] > 0:
            lf = tlf[t] + (lf - tlf[t]) * a_sl
        else:
            lf = tlf[t]
        # filter envelope: accented notes take the shortest decay
        d = acc_decay if cur_acc > 0 else dec[t]
        fe *= np.exp(-2.3 / (max(d, 0.005) * SR))
        acs *= a_acr
        acs_s = acs + (acs_s - acs) * a_slew
        # oscillator (polyBLEP saw; square = two saws half a period apart)
        f = 2.0 ** lf
        dt = f / SR
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
        x = 2.0 * ph - 1.0
        if ph < dt:
            u = ph / dt
            x -= u + u - u * u - 1.0
        elif ph > 1.0 - dt:
            u = (ph - 1.0) / dt
            x -= u * u + u + u + 1.0
        if square > 0:
            p2 = ph + 0.5
            if p2 >= 1.0:
                p2 -= 1.0
            x2 = 2.0 * p2 - 1.0
            if p2 < dt:
                u = p2 / dt
                x2 -= u + u - u * u - 1.0
            elif p2 > 1.0 - dt:
                u = (p2 - 1.0) / dt
                x2 -= u * u + u + u + 1.0
            x = 0.5 * (x - x2) * 1.4
        # cutoff: base x 2^(env_mod x 4 octaves x env + accent x 2 octaves x capacitor)
        fc = cut[t] * 2.0 ** (envm[t] * 4.0 * fe + 2.0 * acs_s)
        if fc > 0.42 * SR:
            fc = 0.42 * SR
        if fc < 20.0:
            fc = 20.0
        g = np.tan(np.pi * fc / SR)
        G = g / (1.0 + g)
        kmax = 4.0 if poles == 4 else 8.0
        k = reso[t] * kmax * 0.985
        # zero-delay ladder: solve the feedback, tanh at the input
        S = 0.0
        Gp = 1.0
        for i in range(poles - 1, -1, -1):
            S += Gp * s[i] / (1.0 + g)
            Gp *= G
        uin = (x * (1.0 + 0.25 * k) - k * S) / (1.0 + k * Gp)
        uin = np.tanh(uin)
        out = 0.0
        for i in range(poles):
            v = (uin - s[i]) * G
            out = v + s[i]
            s[i] = out + v
            uin = out
        # VCA: gate with a short attack and release; accent louder
        if gate[t] > 0:
            amp = amp + a_att if amp + a_att < 1.0 else 1.0
        else:
            amp *= a_rel
        accg_t = 1.0 + 0.9 * accamt[t] * (1.0 if cur_acc > 0 else 0.0)
        accg = accg_t + (accg - accg_t) * a_slew
        z = out * amp * accg * vel[t]
        dr = drive[t]
        if dr > 0:
            kk = 1.0 + dr * 9.0
            z = np.tanh(z * kk) / np.tanh(kk) * (1.0 + dr)
        y[t] = z
    return y


def acid_line(p, notes, total_n):
    """notes: dicts t0 (sample), n (samples held), f (Hz), vel, glide (slides into this note from the previous),
    acc (accent: `!` on the note, or vel >= `accent_vel` when that is set), pa (per-note parameter values from section
    automation). Returns a mono (total_n,) float32 line."""
    out_n = total_n
    tlf = np.zeros(out_n)
    gate = np.zeros(out_n, dtype=np.int64)
    trig = np.zeros(out_n, dtype=np.int64)
    onset = np.zeros(out_n, dtype=np.int64)
    acc = np.zeros(out_n)
    slide = np.zeros(out_n, dtype=np.int64)
    keys = ("cutoff", "env_mod", "reso", "decay", "accent", "drive")
    dflt = dict(cutoff=320.0, env_mod=0.55, reso=0.75, decay=0.45, accent=0.6, drive=0.0)
    arr = {k: np.full(out_n, float(p.get(k, dflt[k]))) for k in keys}
    vel = np.zeros(out_n)
    acc_vel = p.get("accent_vel")
    notes = sorted(notes, key=lambda nt: nt["t0"])
    if not notes:
        return np.zeros(total_n, dtype=np.float32)
    tlf[:] = np.log2(notes[0]["f"])
    for i, nt in enumerate(notes):
        a = int(nt["t0"])
        if a >= out_n:
            break
        nxt = int(notes[i + 1]["t0"]) if i + 1 < len(notes) else out_n
        nxt_slides = i + 1 < len(notes) and notes[i + 1].get("glide")
        end_gate = nxt if nxt_slides else min(a + int(nt["n"]), nxt)
        span_end = min(nxt, out_n)
        tlf[a:] = np.log2(nt["f"])
        gate[a:min(end_gate, out_n)] = 1
        is_slide = bool(nt.get("glide")) and i > 0
        onset[a] = 1
        if is_slide:  # no new envelope; the pitch lags into the note
            slide[a:span_end] = 1
        else:
            trig[a] = 1
        if bool(nt.get("acc")) or (acc_vel is not None and nt["vel"] >= float(acc_vel)):
            acc[a] = 1.0
        vel[a:] = nt["vel"]
        pa = nt.get("pa") or {}
        for k in keys:
            if k in pa:
                arr[k][a:] = float(pa[k])
            elif i > 0 and k in (notes[i - 1].get("pa") or {}):
                arr[k][a:] = float(p.get(k, dflt[k]))
    poles = 4 if int(p.get("slope", 18)) >= 24 else 3
    y = _acid_kernel(tlf, gate, onset, trig, acc, slide, arr["cutoff"], np.clip(arr["env_mod"], 0, 1.5),
                     np.clip(arr["reso"], 0, 1.05), arr["decay"], np.clip(arr["accent"], 0, 1.5),
                     np.clip(arr["drive"], 0, 1), vel, 1 if p.get("wave", "saw") == "square" else 0, poles,
                     float(p.get("slide_ms", 60.0)) / 1000 / 2.3, float(p.get("accent_decay", 0.2)),
                     float(p.get("accent_release", 0.35)), float(p.get("attack", 0.003)),
                     float(p.get("release", 0.008)))
    return (y * 0.45).astype(np.float32)
