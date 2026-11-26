"""Ears for the ride: tension (`listen --tension`), events (`--events`), loops (`--loops`) and ringing (`--ring`).

Analysis only: reads a render (or any audio file with `--wav`) plus its section map (the render's meta.json, or `--map`
a meta.json or project.json); never changes the render. `--ring` may re-render a short window of the project in memory
to name the stem behind a tone (as `--clarity` does), and writes nothing but its report. The research is in
docs/PRODUCTION.md "4c. Tension, events and repetition"; how to read the output in docs/MANUAL.md "Tension, events,
loops and ringing".

--tension: a per-bar tension curve after Farbood (2012): loudness, pitch height (the top of the notes, and the audio's
brightness), onset frequency (notes per second from the render's events, audio onsets without them), harmonic
tension (the bar's pitch-class content against the track's home profile) and noise sweeps (the noisy top end, the
riser's trace), each standardized over the track and weighted 0.30 / 0.20 / 0.25 / 0.10 / 0.15. Every respiro (a
stretch of four bars or more with the kick out, inside the track) and every section named like a build is measured:
its slope, the rise from its lowest point to its last four bars, the climb (the bars from the last one still in the
bottom quarter of its range to the end) and the step into what follows. A respiro whose curve does not rise into the
drop, or a long one (12 bars or more) that waits at the bottom and climbs over less than 40% of its bars, is flagged in
the DJ genres (a dull breakdown), unless the section says `"tension": "flat"` (a deliberate plateau, explained in the
journal).

--events: what the loop did not predict. Every beat is compared, band by band (24 mel bands, in dB), with the same
beat in the four bars before it (their median: what the listener has learned to expect there); a beat that departs
by more than a hand-tuned step is an event. Short events are the
highlights (six beats or less): freezes (the mix falls away for a beat or more), kick stops, fills, hits and throws;
lasting ones are changes (an entry, an exit, a new section). A beat's departure is the mean of its six largest band
departures, so a hit that lifts only the top of the spectrum still counts. Each freeze and kick stop is read for its approach (a riser or noise
swell, a filter dip, a fill or roll, a hit in the bar before) or reported bare. Flags: the longest stretch without a
highlight, and the longest without any event, against the genre's norm.

--loops: runs of near-identical bars: no beat departs more than a small step (4 dB) from the learned beat, and the bar
stays within 4 dB of the bar eight before (so a slow ramp ends a run after eight bars). The render's notes say whether
the run is one pattern repeating (its period) or notes varying under an unchanging sound. Flags runs longer than the
genre's norm (12 bars in DJ genres, 8 in song genres; DJ intros and outros reported, not flagged), unless the section
says `"loop": "long"`.

--ring: persistent narrowband peaks: a long-window spectrum (0.74 s, 1.3 Hz) on a log-frequency grid, each bin's
prominence over the median of the third of an octave around it, the share of the sounding frames where a bin stands
out, and its A-weighted level against its own third-octave band. A tone that stands out for a long span and carries
much of its band is flagged; its stems are named by a window render (the stem whose energy at that frequency is
largest) and by the notes in the events that sit on it.

All thresholds are hand-tuned (2026-11-26), calibrated on the owner's verdicts on Redline v030 and All Hands v035 and
on the published tracks he liked (016, 017, 018, 007, 008). Flags are candidates to check by ear and by zoom.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import seams as S

FSR = 22050
HOP = 512
OUT = os.environ.get("BEAT_DIR", os.getcwd())

# norms per genre family [H, hand-tuned 2026-11-26 on the calibration set; docs/PRODUCTION.md 4c]
#   highlight: longest stretch (bars) without a highlight event inside the body of the track
#   any:       longest stretch (bars) without any event (highlight or change)
#   loop:      longest run of near-identical bars
#   rise:      a respiro's minimum rise (track z-units) from its lowest point to its last four bars
#   climb:     a respiro of 12 bars or more must climb over at least this share of its bars
NORMS = {"dj": dict(highlight=32, any=16, loop=12, rise=0.6, climb=0.4, check_rise=True),
         "song": dict(highlight=32, any=16, loop=8, rise=0.4, climb=0.3, check_rise=False),
         "default": dict(highlight=32, any=16, loop=12, rise=0.5, climb=0.3, check_rise=False)}
WEIGHTS = dict(loudness=0.30, pitch=0.20, onsets=0.25, harmony=0.10, noise=0.15)
TOP_BANDS = 6      # a beat's departure = the mean of its 6 largest band departures (a quarter of the spectrum) [H]
EVENT_DB = 6.0     # a beat departing this much from the learned beat is an event [H]
LOOP_DB = 4.0      # a loop run continues while no beat departs this much from the learned beat ... [H]
DRIFT_DB = 4.0     # ... and the bar stays within this much of the bar eight earlier (a ramp breaks it) [H]
RING_PROM = 8.0    # dB over the third-octave median: the bin stands out [H]
RING_SHARE = 0.5   # of the sounding frames [H]
RING_EXCESS = -3.0  # dB: the tone's power against the rest of its third-octave band [H]
BUILD_WORDS = ("build", "rise", "riser", "lift", "up", "pre", "bd", "break", "respiro", "pressure", "prs")


def family(genre):
    return S.FAMILY.get(genre, "default")


def _z(x):
    x = np.asarray(x, float)
    med = np.nanmedian(x)
    sp = np.nanpercentile(x, 90) - np.nanpercentile(x, 10)
    # clipped at +-3: a sound heard only once (a riser in a track without noise) must not swamp the curve
    return np.clip((x - med) / (sp / 2.56 + 1e-9), -3, 3) if sp > 0 else np.zeros_like(x)


def _lin(y):
    y = np.asarray(y, float)
    if len(y) < 2:
        return 0.0
    return float(np.polyfit(np.arange(len(y)), y, 1)[0])


# ---------------------------------------------------------------- shared analysis
class Track:
    def __init__(self, a, latest, meta, meta_path):
        import librosa
        self.a, self.latest, self.meta = a, latest, meta
        self.project = S.find_project(latest, meta_path, a)
        self.genre = getattr(a, "genre", None) or (self.project or {}).get("genre")
        self.fam = family(self.genre)
        self.norm = dict(NORMS[self.fam])
        y = S.load_audio(latest)
        self.stereo = y
        mono = librosa.resample(y.mean(0).astype(np.float32), orig_sr=S.SR, target_sr=FSR)
        self.mono = mono
        self.edges = S.bar_edges(meta)
        nb = len(self.edges) - 1
        self.nb = nb
        # beats: each bar split into four
        be = []
        for i in range(nb):
            be += list(np.linspace(self.edges[i], self.edges[i + 1], 5)[:-1])
        be.append(self.edges[-1])
        self.beats = np.array(be)
        Sx = np.abs(librosa.stft(mono, n_fft=2048, hop_length=HOP)) ** 2
        self.S = Sx
        self.fr = librosa.fft_frequencies(sr=FSR, n_fft=2048)
        self.tfr = np.arange(Sx.shape[1]) * HOP / FSR
        mel = librosa.feature.melspectrogram(S=Sx, sr=FSR, n_mels=24, fmin=30, fmax=11000)
        self.mel = mel
        self.on = librosa.onset.onset_strength(S=librosa.power_to_db(librosa.feature.melspectrogram(S=Sx, sr=FSR, n_mels=64)),
                                               sr=FSR, hop_length=HOP)
        self.peaks = librosa.onset.onset_detect(onset_envelope=self.on, sr=FSR, hop_length=HOP, units="time")
        self.chroma = librosa.feature.chroma_stft(S=Sx, sr=FSR)
        self.secs = meta["sections"]
        self.arr = {s["name"]: s for s in (self.project or {}).get("arrangement") or []}
        self.roles = {}
        if self.project:
            for n, t in (self.project.get("tracks") or {}).items():
                self.roles[n] = t.get("role", "")
        self.events = meta.get("events") or {}
        self._beat_features()
        self._bar_section()

    def _bar_section(self):
        self.sec_of_bar = []
        for i in range(self.nb):
            t = (self.edges[i] + self.edges[i + 1]) / 2
            k = max([j for j, s in enumerate(self.secs) if s["start"] <= t + 1e-6] or [0])
            self.sec_of_bar.append(k)
        self.sec_of_bar = np.array(self.sec_of_bar)

    def _beat_features(self):
        nbt = len(self.beats) - 1
        B = np.zeros((nbt, self.mel.shape[0]))
        lvl = np.zeros(nbt)
        for j in range(nbt):
            m = (self.tfr >= self.beats[j]) & (self.tfr < self.beats[j + 1])
            if m.sum() == 0:
                B[j] = 1e-10
                continue
            B[j] = self.mel[:, m].mean(1)
            lvl[j] = self.S[:, m].sum(0).mean()
        ref = 10 * np.log10(B.max() + 1e-12)
        self.bdB = np.maximum(10 * np.log10(B + 1e-12), ref - 70)   # band levels per beat, floor 70 dB down
        self.blevel = 10 * np.log10(lvl + 1e-12)
        self.silent_beat = self.blevel < self.blevel.max() - 45

    # kick presence per beat: from the render's kick events, else the low band's onsets
    def kick_beats(self):
        nbt = len(self.beats) - 1
        kicks = [n for n in self.events if "kick" in n.lower() and self.roles.get(n, "kick") in ("kick", "")]
        if not kicks:
            kicks = [n for n, r in self.roles.items() if r == "kick" and n in self.events]
        pres = np.zeros(nbt, bool)
        if kicks:
            ts = np.sort(np.concatenate([[x["t"] for x in self.events[n] if x.get("v", 1) > 0.05] for n in kicks]))
            for j in range(nbt):
                a, b = self.beats[j], self.beats[j + 1]
                w = (b - a)
                k = np.searchsorted(ts, a - 0.03)
                pres[j] = k < len(ts) and ts[k] < a + 0.3 * w
            # the kick stem's level: a kick faded or filtered to nothing is not there
            st = (self.meta.get("stems_rms") or {})
            hop = self.meta.get("rms_hop", 0.05)
            for n in kicks:
                if n in st:
                    e = np.asarray(st[n])
                    mx = e.max() + 1e-9
                    for j in range(nbt):
                        a, b = int(self.beats[j] / hop), int(self.beats[j + 1] / hop) + 1
                        if pres[j] and (e[a:b].max() if b > a and a < len(e) else 0) < mx * 0.1:  # -20 dB
                            pres[j] = False
            return pres, "events"
        # audio: low-band (30-150 Hz) flux peak in the first third of the beat, against the track's typical kick
        lowb = (self.fr >= 30) & (self.fr < 150)
        fl = np.maximum(np.diff(np.sqrt(self.S[lowb].sum(0)), prepend=0), 0)
        v = np.zeros(nbt)
        for j in range(nbt):
            a, b = self.beats[j], self.beats[j + 1]
            m = (self.tfr >= a - 0.03) & (self.tfr < a + 0.3 * (b - a))
            v[j] = fl[m].max() if m.any() else 0
        thr = 0.25 * np.percentile(v, 90)
        return v > thr, "audio"

    def bar_slice(self, i):
        return (self.tfr >= self.edges[i]) & (self.tfr < self.edges[i + 1])


# ---------------------------------------------------------------- tension
def tension_curve(T):
    nb = T.nb
    loud = np.zeros(nb); bright = np.zeros(nb); rate = np.zeros(nb); noise = np.zeros(nb)
    chroma = np.zeros((nb, 12))
    hf = (T.fr >= 3000) & (T.fr < 11000)
    import librosa
    flat = librosa.feature.spectral_flatness(S=np.sqrt(T.S[hf]))[0]
    for i in range(nb):
        m = T.bar_slice(i)
        if m.sum() < 2:
            continue
        tot = T.S[:, m].sum(0)
        loud[i] = 10 * np.log10(tot.mean() + 1e-12)
        bright[i] = np.log2((T.S[:, m] * T.fr[:, None]).sum() / (tot.sum() + 1e-12) + 1)
        rate[i] = ((T.peaks >= T.edges[i]) & (T.peaks < T.edges[i + 1])).sum() / (T.edges[i + 1] - T.edges[i])
        # noise sweep: the noisy top end's level (risers, white-noise swells), weighted by how noise-like it is
        noise[i] = 10 * np.log10(T.S[hf][:, m].sum(0).mean() + 1e-12) + 10 * np.log10(flat[m].mean() + 1e-6)
        chroma[i] = T.chroma[:, m].mean(1)
    pitch_ev = None
    rate_ev = None
    if T.events:
        pitch_ev = np.full(nb, np.nan)
        rate_ev = np.zeros(nb)
        allt, allm = [], []
        for n, ev in T.events.items():
            for x in ev:
                if x.get("v", 1) <= 0.05:
                    continue
                allt.append(x["t"]); allm.append(np.nan if x.get("m") is None else x["m"])
        allt, allm = np.array(allt), np.array(allm, float)
        for i in range(nb):
            sel = (allt >= T.edges[i]) & (allt < T.edges[i + 1])
            rate_ev[i] = sel.sum() / (T.edges[i + 1] - T.edges[i])
            pm = allm[sel]
            pm = pm[~np.isnan(pm)]
            if len(pm):
                pitch_ev[i] = np.percentile(pm, 90)
        if np.all(np.isnan(pitch_ev)):
            pitch_ev = None
    # harmonic tension: distance of the bar's pitch-class content from the track's home profile (Lerdahl's distance
    # from the tonic, approximated; the pitch-class profile weights what is held as well as what is struck)
    home = chroma[loud > np.percentile(loud, 30)].mean(0) if nb else np.ones(12)
    harm = np.array([1 - S._cos(c, home) if c.any() else 0 for c in chroma])
    comp = {}
    comp["loudness"] = _z(loud)
    zb = _z(bright)
    if pitch_ev is not None:
        pe = np.where(np.isnan(pitch_ev), np.nanmedian(pitch_ev), pitch_ev)
        comp["pitch"] = 0.5 * _z(pe) + 0.5 * zb
    else:
        comp["pitch"] = zb
    comp["onsets"] = 0.5 * _z(np.log2(rate + 0.5)) + (0.5 * _z(np.log2(rate_ev + 0.5)) if rate_ev is not None else 0.5 * _z(np.log2(rate + 0.5)))
    comp["harmony"] = _z(harm)
    comp["noise"] = _z(noise)
    ten = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
    # silence is not tension: bars that are (almost) silent take the track's minimum
    sil = loud < loud.max() - 45
    ten[sil] = np.nanmin(ten)
    return ten, comp


def respiros(T, kick):
    """Stretches inside the track (not the intro or outro) of 4+ bars with the kick out (fewer than a quarter of the
    beats), extended to the end of the section they end in; plus sections named like a build."""
    nb = T.nb
    kb = kick.reshape(-1, 4)[:nb].mean(1) if len(kick) >= nb * 4 else np.zeros(nb)
    off = kb < 0.25
    first_kick = int(np.argmax(kb >= 0.5)) if (kb >= 0.5).any() else 0
    last_kick = nb - 1 - int(np.argmax(kb[::-1] >= 0.5)) if (kb >= 0.5).any() else nb - 1
    out = []
    i = first_kick
    while i <= last_kick:
        if off[i]:
            j = i
            while j + 1 <= last_kick and (off[j + 1] or (j + 2 <= last_kick and off[j + 2] and kb[j + 1] < 0.75)):
                j += 1
            if j - i + 1 >= 4:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    spans = list(out)
    # named builds not already inside a respiro: the build leads to the next section
    for k, s in enumerate(T.secs):
        nm = s["name"].lower()
        if any(w in nm for w in ("build", "rise", "lift")) and s["bars"] >= 3:
            b0 = int(np.argmin(np.abs(T.edges - s["start"])))
            b1 = b0 + s["bars"] - 1
            if not any(a <= b0 and b1 <= b for a, b in spans):
                spans.append((b0, b1))
    # merge overlapping or touching spans, then extend each to the bar before the next kick-on (the drop)
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged, kb


def run_tension(T, kick):
    ten, comp = tension_curve(T)
    spans, kb = respiros(T, kick)
    rows = []
    for a, b in spans:
        seg = ten[a:b + 1]
        n = b - a + 1
        last = seg[-min(4, n):].mean()
        lo_i = int(np.argmin(seg[:max(1, n - 2)]))
        lo = seg[lo_i]
        rise = float(last - lo)
        slope8 = _lin(seg) * 8                      # per 8 bars
        last8 = seg[-min(8, n):]
        slope_end = _lin(last8) * 8
        after = ten[b + 1:b + 5].mean() if b + 1 < T.nb else np.nan
        step = float(after - last) if not np.isnan(after) else np.nan
        # which components rose (last four bars against the lowest four)
        lo_win = slice(a + max(0, lo_i - 1), a + max(0, lo_i - 1) + 4)
        rose = {k: float(comp[k][b - min(4, n) + 1:b + 1].mean() - comp[k][lo_win].mean()) for k in comp}
        names = sorted({T.secs[T.sec_of_bar[i]]["name"] for i in range(a, b + 1)},
                       key=lambda x: [s["name"] for s in T.secs].index(x))
        intended = any((T.arr.get(nm) or {}).get("tension") in ("flat", "intended") for nm in names)
        kickless = kb[a:b + 1].mean() < 0.4
        # the climb: from the last bar still in the lowest quarter of the respiro's range to its end. A long
        # respiro that waits at the bottom and climbs only in its last bars is still dull (the owner, 2026-11-26:
        # "the respiro moments are dull, while in real songs they are used for tension build-up")
        low_q = lo + 0.25 * max(rise, 1e-6)
        climb_from = max([x for x in range(n - 1) if seg[x] <= low_q] or [0])
        climb = n - climb_from - 1
        dull = (rise < T.norm["rise"]) or (slope_end <= 0 and rise < 2 * T.norm["rise"]) or \
            (n >= 12 and climb < T.norm["climb"] * n)
        flag = bool(dull and T.norm["check_rise"] and not intended and n >= 4)
        rows.append(dict(bars=f"{a + 1}-{b + 1}", n=n, sections=names, kickless=bool(kickless), rise=round(rise, 2),
                         climb=int(climb),
                         slope8=round(slope8, 2), slope_last8=round(slope_end, 2),
                         step_into_next=None if np.isnan(step) else round(step, 2),
                         rose={k: round(v, 2) for k, v in rose.items()}, intended=intended, flag=flag))
    return ten, comp, rows


# ---------------------------------------------------------------- events
def beat_deviation(T):
    """Per beat: RMS over the bands (dB) of its departure from the median of the same beat in the four bars before."""
    X = T.bdB
    n = len(X)
    dev = np.zeros(n)
    sgn = np.zeros(n)     # mean signed departure (negative: the mix falls away)
    lowdrop = np.zeros(n)
    for j in range(n):
        refs = [j - 4 * k for k in range(1, 5) if j - 4 * k >= 0]
        if len(refs) < 2:
            continue
        ref = np.median(X[refs], 0)
        d = X[j] - ref
        dev[j] = float(np.sort(np.abs(d))[-TOP_BANDS:].mean())
        sgn[j] = float(d.mean())
        lowdrop[j] = float(d[:4].mean())
    return dev, sgn, lowdrop


def stem_bar_levels(T):
    st = T.meta.get("stems_rms") or {}
    hop = T.meta.get("rms_hop", 0.05)
    out = {}
    for n, e in st.items():
        e = np.asarray(e)
        v = np.zeros(T.nb)
        for i in range(T.nb):
            a, b = int(T.edges[i] / hop), int(T.edges[i + 1] / hop)
            seg = e[a:b]
            v[i] = 10 * np.log10((seg ** 2).mean() + 1e-12) if len(seg) else -120
        out[n] = v
    return out


def run_events(T, kick):
    dev, sgn, lowdrop = beat_deviation(T)
    nbt = len(dev)
    nb = T.nb
    hot = dev >= EVENT_DB
    # group consecutive hot beats into candidate events
    groups = []
    j = 0
    while j < nbt:
        if hot[j]:
            k = j
            while k + 1 < nbt and hot[k + 1]:
                k += 1
            groups.append((j, k))
            j = k + 1
        else:
            j += 1
    # merge events that are a beat apart
    mg = []
    for g in groups:
        if mg and g[0] - mg[-1][1] <= 2:
            mg[-1] = (mg[-1][0], g[1])
        else:
            mg.append(g)
    stems = stem_bar_levels(T)
    sb = {}
    if stems:
        mxall = max(v.max() for v in stems.values())
        for n, v in stems.items():
            sb[n] = v > mxall - 35
    ev = []
    for j0, j1 in mg:
        bar = j0 // 4
        dur = j1 - j0 + 1
        # does the loop resume? the beats 1-2 bars after the event against the beats before it
        after = [x for x in range(j1 + 1, min(j1 + 9, nbt))]
        before = [x for x in range(max(j0 - 8, 0), j0)]
        resumed = False
        if after and before:
            ra = T.bdB[after].mean(0); rb = T.bdB[before].mean(0)
            resumed = float(np.sqrt(((ra - rb) ** 2).mean())) < EVENT_DB * 0.6
        short = dur <= 6
        kinds = []
        lv = T.blevel[j0:j1 + 1]
        ctx = np.median(T.blevel[max(j0 - 8, 0):j0]) if j0 > 0 else lv.max()
        if lv.min() < ctx - 9:
            kinds.append("freeze")
        kgap = (~kick[j0:j1 + 1]).sum() >= 1 and kick[max(j0 - 8, 0):j0].mean() > 0.75 if j0 > 0 else False
        if kgap and "freeze" not in kinds:
            kinds.append("kick stop")
        rate_in = ((T.peaks >= T.beats[j0]) & (T.peaks < T.beats[j1 + 1])).sum() / (T.beats[j1 + 1] - T.beats[j0])
        rate_ctx = ((T.peaks >= T.beats[max(j0 - 16, 0)]) & (T.peaks < T.beats[j0])).sum() / max(T.beats[j0] - T.beats[max(j0 - 16, 0)], 1e-3)
        if rate_in > 1.4 * rate_ctx and sgn[j0:j1 + 1].mean() > -3:
            kinds.append("fill")
        # a stem heard only around here (2 bars or less within the 8 around): a hit or a throw
        hit = []
        for n, on in sb.items():
            b0, b1 = bar, min((j1 // 4), nb - 1)
            if on[b0:b1 + 1].any():
                w = on[max(b0 - 4, 0):min(b1 + 5, nb)]
                if w.sum() <= 2 + (b1 - b0):
                    hit.append(n)
        if hit:
            kinds.append("hit:" + ",".join(hit[:3]))
        if not kinds:
            kinds.append("rise" if sgn[j0:j1 + 1].mean() > 0 else "dip")
        # section boundary?
        at_line = any(abs(T.beats[j0] - s["start"]) < 0.6 * (T.beats[1] - T.beats[0]) * 2 for s in T.secs[1:])
        cls = "highlight" if short else "change"
        approach = None
        if any(k in ("freeze", "kick stop") for k in kinds):
            approach = freeze_approach(T, j0, kick)
        ev.append(dict(beat=int(j0), bar=int(bar + 1), beat_in_bar=int(j0 % 4 + 1), beats=int(dur),
                       time=round(float(T.beats[j0]), 2), dev=round(float(dev[j0:j1 + 1].max()), 1),
                       kinds=kinds, cls=cls, at_line=bool(at_line), approach=approach,
                       section=T.secs[T.sec_of_bar[min(bar, nb - 1)]]["name"]))
    # the body: from the first bar the kick plays to the last (DJ intros and outros are tools, judged apart)
    kb = kick.reshape(-1, 4)[:nb].mean(1)
    on_bars = np.where(kb >= 0.5)[0]
    b_lo, b_hi = (int(on_bars[0]), int(on_bars[-1])) if len(on_bars) else (0, nb - 1)
    if T.fam != "dj":
        b_lo, b_hi = 0, nb - 1

    def drought(sel):
        marks = sorted({e["bar"] - 1 for e in ev if sel(e) and b_lo <= e["bar"] - 1 <= b_hi})
        pts = [b_lo - 1] + marks + [b_hi + 1]
        gaps = [(pts[i] + 1, pts[i + 1] - 1, pts[i + 1] - pts[i] - 1) for i in range(len(pts) - 1)]
        return max(gaps, key=lambda g: g[2]) if gaps else (0, 0, 0)
    hl = drought(lambda e: e["cls"] == "highlight")
    # any event: every bar with a beat over the line (a long change marks all its bars)
    hot_bars = sorted({j // 4 for j in np.where(hot)[0] if b_lo <= j // 4 <= b_hi})
    pts = [b_lo - 1] + hot_bars + [b_hi + 1]
    gi = int(np.argmax(np.diff(pts)))
    an = (pts[gi] + 1, pts[gi + 1] - 1, pts[gi + 1] - pts[gi] - 1)
    # per 16 bars
    per16 = []
    for s in range(0, nb, 16):
        per16.append(dict(bars=f"{s + 1}-{min(s + 16, nb)}",
                          highlight=sum(1 for e in ev if e["cls"] == "highlight" and s <= e["bar"] - 1 < s + 16),
                          change=sum(1 for e in ev if e["cls"] == "change" and s <= e["bar"] - 1 < s + 16)))
    body = max(b_hi - b_lo + 1, 1)
    nh = sum(1 for e in ev if e["cls"] == "highlight" and b_lo <= e["bar"] - 1 <= b_hi)
    fz = [e for e in ev if e["cls"] == "highlight" and any(k in ("freeze", "kick stop") for k in e["kinds"])]
    res = dict(events=ev, body=f"{b_lo + 1}-{b_hi + 1}", highlights_per16=round(nh / body * 16, 2),
               longest_without_highlight=dict(bars=f"{hl[0] + 1}-{hl[1] + 1}", n=int(hl[2])),
               longest_without_event=dict(bars=f"{an[0] + 1}-{an[1] + 1}", n=int(an[2])),
               freezes=len(fz), freezes_bare=sum(1 for e in fz if e["approach"] == "bare"), per16=per16,
               flag_highlight=bool(hl[2] > T.norm["highlight"]), flag_any=bool(an[2] > T.norm["any"]),
               flag_no_freeze=bool(T.fam == "dj" and not fz),
               bare=[f"{e['bar']}.{e['beat_in_bar']}" for e in fz if e["approach"] == "bare"])
    return dev, res


def freeze_approach(T, j0, kick):
    """What prepares a freeze, in the bar before it: a riser or noise swell (the noisy top end rising), a filter dip
    (the brightness falling), a fill or roll (onsets denser), a hit (a beat standing out)."""
    import librosa
    a0 = max(j0 - 4, 0)
    if j0 - a0 < 2:
        return "bare"
    hf = (T.fr >= 3000) & (T.fr < 11000)
    got = []
    t_a, t_b, t_c = T.beats[max(j0 - 8, 0)], T.beats[a0], T.beats[j0]
    m_ref = (T.tfr >= t_a) & (T.tfr < t_b)
    m_pre = (T.tfr >= t_b) & (T.tfr < t_c)
    if m_ref.sum() < 2 or m_pre.sum() < 2:
        return "bare"
    hf_ref = 10 * np.log10(T.S[hf][:, m_ref].sum(0).mean() + 1e-12)
    hf_seq = 10 * np.log10(T.S[hf][:, m_pre].sum(0) + 1e-12)
    if hf_seq[-max(3, len(hf_seq) // 4):].mean() - hf_ref > 3:
        got.append("riser")
    cen = lambda m: (T.S[:, m] * T.fr[:, None]).sum() / (T.S[:, m].sum() + 1e-12)
    if np.log2(cen(m_pre) / (cen(m_ref) + 1e-9)) < -0.3:
        got.append("filter dip")
    r_ref = ((T.peaks >= t_a) & (T.peaks < t_b)).sum() / max(t_b - t_a, 1e-3)
    r_pre = ((T.peaks >= t_b) & (T.peaks < t_c)).sum() / max(t_c - t_b, 1e-3)
    if r_pre > 1.3 * r_ref:
        got.append("fill/roll")
    lv = T.blevel[a0:j0]
    if len(lv) and (lv[-1] - np.median(T.blevel[max(j0 - 8, 0):a0] if a0 > 0 else lv)) > 2:
        got.append("swell")
    return ", ".join(got) if got else "bare"


# ---------------------------------------------------------------- loops
def bar_fingerprints(T):
    if not T.events:
        return None
    fps = [set() for _ in range(T.nb)]
    for n, evs in T.events.items():
        for x in evs:
            if x.get("v", 1) <= 0.05:
                continue
            i = int(np.searchsorted(T.edges, x["t"] + 1e-4, side="right") - 1)
            if 0 <= i < T.nb:
                pos = int(round((x["t"] - T.edges[i]) / (T.edges[i + 1] - T.edges[i]) * 16)) % 16
                fps[i].add((n, pos, x.get("m")))
    return fps


def run_loops(T, dev):
    """Runs of near-identical bars: no beat departs LOOP_DB from the learned beat, and the bar stays within DRIFT_DB
    of the bar eight earlier. The render's notes say whether the run is one pattern repeating (its period)."""
    nb = T.nb
    fps = bar_fingerprints(T)
    Xb = T.bdB[: nb * 4].reshape(nb, 4, -1).mean(1)
    calm = np.array([dev[4 * i:4 * i + 4].max() < LOOP_DB for i in range(nb)])
    drift = np.array([i >= 8 and float(np.sort(np.abs(Xb[i] - Xb[i - 8]))[-TOP_BANDS:].mean()) >= DRIFT_DB
                      for i in range(nb)])
    sil = np.array([T.blevel[4 * i:4 * i + 4].max() < T.blevel.max() - 45 for i in range(nb)])
    runs = []
    i = 0
    while i < nb:
        if calm[i] and not sil[i]:
            k = i
            while k + 1 < nb and calm[k + 1] and not sil[k + 1] and not (drift[k + 1] and k + 1 - i >= 8):
                k += 1
            # the run includes the bar it repeats (the bar before the first calm bar)
            runs.append((max(i - 1, 0), k))
            i = k + 1
        else:
            i += 1
    rows = []
    for s, k in runs:
        n = k - s + 1
        if n < 4:
            continue
        names = sorted({T.secs[T.sec_of_bar[x]]["name"] for x in range(s, k + 1)},
                       key=lambda x: [q["name"] for q in T.secs].index(x))
        period = None
        if fps is not None:
            for p in (1, 2, 4, 8):
                same = [fps[x] == fps[x - p] for x in range(s + p, k + 1) if fps[x]]
                if same and np.mean(same) >= 0.75:
                    period = p
                    break
        intended = any((T.arr.get(nm) or {}).get("loop") in ("long", "intended") for nm in names)
        # DJ intros and outros are mixing tools: a long loop in the first or last 32 bars is reported, not flagged
        dj_end = T.fam == "dj" and (k < 32 or s >= nb - 32)
        rows.append(dict(bars=f"{s + 1}-{k + 1}", n=n, period=period, sections=names, intended=intended,
                         dj_end=dj_end, flag=bool(n > T.norm["loop"] and not intended and not dj_end)))
    rows.sort(key=lambda r: -r["n"])
    over = sum(r["n"] for r in rows if r["flag"])
    return dict(runs=rows, over_share=round(over / max(nb, 1), 2), source="audio (notes for the period)" if fps is not None else "audio")


# ---------------------------------------------------------------- ring
def run_ring(T, stems_render=True):
    import librosa
    y = T.mono
    nfft = 16384
    hop = 8192
    Sx = np.abs(librosa.stft(y, n_fft=nfft, hop_length=hop)) ** 2
    fr = librosa.fft_frequencies(sr=FSR, n_fft=nfft)
    # log-frequency grid, 48 bins per octave, 40 Hz-10 kHz
    lf = 40 * 2 ** (np.arange(0, np.log2(10000 / 40) * 48) / 48)
    idx = np.searchsorted(fr, lf)
    # each log bin takes the max of the linear bins it covers (a narrow peak keeps its height)
    edges = np.searchsorted(fr, 40 * 2 ** ((np.arange(len(lf) + 1) - 0.5) / 48))
    L = np.zeros((len(lf), Sx.shape[1]))
    for k in range(len(lf)):
        a, b = edges[k], max(edges[k + 1], edges[k] + 1)
        L[k] = Sx[a:b].max(0)
    LdB = 10 * np.log10(L + 1e-12)
    from scipy.ndimage import median_filter
    med = median_filter(LdB, size=(17, 1), mode="nearest")    # +-1/6 octave
    prom = LdB - med
    frame_lvl = 10 * np.log10(Sx.sum(0) + 1e-12)
    sounding = frame_lvl > frame_lvl.max() - 30
    st = prom[:, sounding] >= RING_PROM
    share = st.mean(1)
    # A-weighting and the tone's power against the rest of its third-octave band
    def aw(f):
        f2 = f ** 2
        ra = (12194 ** 2 * f2 ** 2) / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
        return 20 * np.log10(ra) + 2.0
    A = aw(lf)
    tone_p = L[:, sounding]
    band = np.array([L[max(k - 8, 0):k + 9, :][:, sounding].sum(0) for k in range(len(lf))])
    excess = 10 * np.log10(np.median(tone_p, 1) + 1e-12) - 10 * np.log10(np.median(band - tone_p, 1) + 1e-12)
    # level of the tone against the whole mix (A-weighted), median over the sounding frames
    mixA = 10 * np.log10((Sx[:, sounding] * 10 ** (aw(np.maximum(fr, 10))[:, None] / 10)).sum(0) + 1e-12)
    toneA = 10 * np.log10(tone_p + 1e-12) + A[:, None]
    rel = np.median(toneA - mixA[None], 1)
    # candidates: local maxima of the share
    cands = []
    for k in range(1, len(lf) - 1):
        if share[k] >= RING_SHARE * 0.6 and share[k] >= share[k - 1] and share[k] >= share[k + 1]:
            cands.append(k)
    rows = []
    tfr = np.arange(Sx.shape[1]) * hop / FSR
    for k in sorted(cands, key=lambda k: -share[k])[:12]:
        on = prom[k] >= RING_PROM
        # where it stands out: the 8-bar blocks in which it does in at least half the frames
        blocks = []
        for b0 in range(0, T.nb, 8):
            t0, t1 = T.edges[b0], T.edges[min(b0 + 8, T.nb)]
            mm = (tfr >= t0) & (tfr < t1) & sounding
            if mm.sum() >= 3 and on[mm].mean() >= 0.5:
                blocks.append(b0)
        f = float(lf[k])
        # refine the frequency on the linear grid
        a, b = edges[k], max(edges[k + 1], edges[k] + 1)
        f = float(fr[a + int(np.argmax(np.median(Sx[a:b][:, sounding], 1)))])
        midi = 69 + 12 * np.log2(f / 440)
        note = librosa.midi_to_note(int(round(midi)))
        nblk = max(1, int(np.ceil(T.nb / 8)))
        flag = bool(share[k] >= RING_SHARE and excess[k] >= RING_EXCESS and f >= 150 and len(blocks) >= max(3, nblk // 3))
        rows.append(dict(hz=round(f, 1), note=f"{note}{'+' if midi - round(midi) > 0.15 else '-' if midi - round(midi) < -0.15 else ''}",
                         share=round(float(share[k]), 2), prominence_db=round(float(np.median(prom[k, sounding])), 1),
                         excess_db=round(float(excess[k]), 1), rel_mix_dba=round(float(rel[k]), 1),
                         span=(f"{len(blocks)}/{nblk} 8-bar blocks, bars {blocks[0] + 1}-{min(blocks[-1] + 8, T.nb)}"
                               if blocks else "no 8-bar block"), blocks=blocks,
                         flag=flag, k=int(k)))
    # merge harmonics-of-one-another? keep, but attribute
    for r in rows:
        r["notes_on_it"] = notes_on(T, r["hz"])
    flagged = [r for r in rows if r["flag"]]
    if stems_render and flagged and T.project is not None:
        try:
            attrib = stem_energy_at(T, [r["hz"] for r in flagged], flagged, tfr)
            for r in flagged:
                r["stems"] = attrib.get(r["hz"])
        except Exception as e:  # the attribution is a bonus; the measurement stands without it
            for r in flagged:
                r["stems"] = f"(window render failed: {e})"
    return dict(rows=rows, lf=lf, share=share, prom=prom, sounding=sounding, tfr=tfr)


def notes_on(T, hz, tol=0.35):
    """Tracks whose notes (fundamental or a harmonic up to the 8th) sit on hz, with the share of the track's notes."""
    out = []
    for n, ev in T.events.items():
        ms = np.array([x["m"] for x in ev if x.get("m") is not None], float)
        if not len(ms):
            continue
        f0 = 440 * 2 ** ((ms - 69) / 12)
        hit = np.zeros(len(ms), bool)
        for h in range(1, 9):
            hit |= np.abs(12 * np.log2(f0 * h / hz)) < tol
        if hit.mean() >= 0.2:
            out.append(f"{n} {hit.mean():.0%}")
    # tuned drums and fixed-pitch instruments (a bongo at 659 Hz has no note numbers in the events)
    for n, tr in ((T.project or {}).get("tracks") or {}).items():
        insts = [tr.get("inst") or {}] + [l.get("inst") or {} for l in tr.get("layers") or []]
        for ins in insts:
            tu = ins.get("tune")
            if isinstance(tu, (int, float)) and tu > 20 and any(abs(12 * np.log2(tu * h / hz)) < tol for h in (1, 2, 3)):
                out.append(f"{n} (tuned {tu:g} Hz)")
    return out


def stem_energy_at(T, freqs, rows, tfr):
    """Re-render a 4-bar window where the flagged tones are strongest and measure each stem's narrowband energy at
    each frequency (+-1/6 semitone) against the mix's."""
    import studio as ST
    import librosa
    P = T.project
    # the window: the 4 bars in the middle of the first flagged tone's span
    bl = rows[0]["blocks"] or [T.nb // 2]
    i = int(np.clip(bl[len(bl) // 2] + 2, 0, T.nb - 4))
    t0, t1 = T.edges[i], T.edges[i + 4]
    stems = {}
    span = {}
    pre = 2 * 4 * 60.0 / P["bpm"]
    off = max(0.0, t0 - pre)
    span["a0"], span["a1"] = int(round((t0 - off) * S.SR)), int(round((t1 - off) * S.SR))

    def hook(name, st):
        x = ((st[0, span["a0"]:span["a1"]] + st[1, span["a0"]:span["a1"]]) * 0.5).astype(np.float32)
        stems[name] = stems.get(name, 0) + x if name in stems else x
    _, m = ST.render(P, window=(t0, t1), stem_hook=hook, pre_roll=pre)
    mix = m["_premaster"]
    mix = ((mix[0, span["a0"]:span["a1"]] + mix[1, span["a0"]:span["a1"]]) * 0.5).astype(np.float32)
    nfft = 32768
    def spec(x):
        return np.abs(librosa.stft(x, n_fft=nfft, hop_length=nfft // 2)) ** 2
    fr = librosa.fft_frequencies(sr=S.SR, n_fft=nfft)
    Mx = spec(mix).mean(1)
    out = {}
    for f in freqs:
        band = (fr > f * 2 ** (-1 / 72)) & (fr < f * 2 ** (1 / 72))
        mxv = Mx[band].sum() + 1e-15
        lst = []
        for n, x in stems.items():
            if len(x) < nfft:
                continue
            v = spec(x).mean(1)[band].sum()
            lst.append((10 * np.log10(v / mxv + 1e-15), n))
        lst.sort(reverse=True)
        out[f] = [f"{n} {db:+.1f} dB" for db, n in lst[:4] if db > -20] + [f"(bars {i + 1}-{i + 4})"]
    return out


# ---------------------------------------------------------------- output
def run(a, renders, latest, meta_path):
    mp = getattr(a, "map", None) or meta_path
    if mp is None or not os.path.exists(mp):
        raise SystemExit("no section map: give --map renders/vNNN.meta.json (or a project.json)")
    meta = S.load_map(mp)
    T = Track(a, latest, meta, mp)
    kick, ksrc = T.kick_beats()
    want = {k: getattr(a, k, False) for k in ("tension", "events", "loops", "ring")}
    print(f"RIDE: {os.path.basename(latest)}  {T.nb} bars  genre {T.genre or '-'} ({T.fam}); kick from {ksrc}; "
          f"norms [H]: highlight every <= {T.norm['highlight']} bars, any event <= {T.norm['any']}, loop runs <= "
          f"{T.norm['loop']}" + (f", respiro rise >= {T.norm['rise']}" if T.norm["check_rise"] else ""))
    out = {}
    panels = []
    if want["tension"]:
        ten, comp, rows = run_tension(T, kick)
        out["tension"] = dict(curve=np.round(ten, 2).tolist(), respiros=rows)
        print("\nTENSION (per bar, Farbood-style: 0.30 loudness + 0.20 pitch/brightness + 0.25 onsets + 0.10 harmony + "
              "0.15 noise sweep; track z-units)")
        print(f"{'bars':>9s} {'n':>3s} {'rise':>5s} {'climb':>5s} {'slope/8':>7s} {'end/8':>6s} {'step':>5s}  sections / what rose")
        for r in rows:
            rose = ", ".join(f"{k} {v:+.1f}" for k, v in sorted(r["rose"].items(), key=lambda kv: -kv[1]) if abs(v) >= 0.3)
            print(f"{r['bars']:>9s} {r['n']:3d} {r['rise']:5.2f} {r['climb']:5d} {r['slope8']:7.2f} {r['slope_last8']:6.2f} "
                  f"{'-' if r['step_into_next'] is None else format(r['step_into_next'], '5.2f'):>5s}  "
                  f"{'FLAG dull ' if r['flag'] else ('flat (intended) ' if r['intended'] else '')}"
                  f"{'respiro' if r['kickless'] else 'build'} {','.join(r['sections'])} | {rose or 'nothing rose'}")
        for r in rows:
            if r["flag"]:
                print(f"FLAG dull respiro bars {r['bars']} ({','.join(r['sections'])}): tension rises {r['rise']:.2f} "
                      f"(norm >= {T.norm['rise']}), climbing over its last {r['climb']} of {r['n']} bars (norm >= "
                      f"{T.norm['climb']:.0%} of a respiro of 12 bars or more), last 8 bars {r['slope_last8']:+.2f} per 8. Build it as tension: "
                      "rising pitch or filter, a riser or noise swell, a roll that accelerates, chords or pads swelling, "
                      "a held suspension, a voice; or mark the section `\"tension\": \"flat\"` with a reason.")
        if not any(r["flag"] for r in rows):
            print("no dull respiro flagged" if T.norm["check_rise"] else "(respiro rise reported, not flagged outside DJ genres)")
        panels.append(("tension", ten, comp, rows))
    if want["events"] or want["loops"]:
        dev, ev = run_events(T, kick)
    if want["events"]:
        out["events"] = ev
        print(f"\nEVENTS (beats departing >= {EVENT_DB} dB from the same beat in the 4 bars before; highlight = gone "
              f"within a bar and the loop resumes; body {ev['body']})")
        for e in ev["events"]:
            mk = "*" if e["cls"] == "highlight" else " "
            print(f" {mk} bar {e['bar']:3d}.{e['beat_in_bar']} {e['beats']:2d} beats {e['dev']:4.1f} dB  {e['section'][:10]:10s} "
                  f"{e['cls']:9s} {', '.join(e['kinds'])}" + (f"  approach: {e['approach']}" if e["approach"] else "")
                  + ("  (on a section line)" if e["at_line"] else ""))
        print("per 16 bars (highlights/changes): " + "  ".join(f"{p['bars']}: {p['highlight']}/{p['change']}" for p in ev["per16"]))
        print(f"highlights per 16 bars in the body: {ev['highlights_per16']}; longest without a highlight: "
              f"{ev['longest_without_highlight']['n']} bars ({ev['longest_without_highlight']['bars']}); without any "
              f"event: {ev['longest_without_event']['n']} bars ({ev['longest_without_event']['bars']}); freezes/kick "
              f"stops: {ev['freezes']} ({ev['freezes_bare']} bare)")
        if ev["flag_highlight"]:
            print(f"FLAG event drought: {ev['longest_without_highlight']['n']} bars without a highlight (norm <= "
                  f"{T.norm['highlight']}). Plan events: a 1-beat freeze or kick stop approached by a transition, a fill, a "
                  "hit or throw, a one-bar variation every 4-8 bars.")
        if ev["flag_any"]:
            print(f"FLAG nothing happens for {ev['longest_without_event']['n']} bars ({ev['longest_without_event']['bars']}; "
                  f"norm <= {T.norm['any']}).")
        if ev["flag_no_freeze"]:
            print("FLAG no freeze or kick stop anywhere in the body: the genre's quickest highlight is missing.")
        if ev["bare"]:
            print(f"FLAG bare freeze at bar {', '.join(ev['bare'])}: nothing leads into it. Approach it (a riser or "
                  "reverse cymbal, a filter dip, a roll, a vocal tag or a hit in the beat before), or keep it bare on "
                  "purpose and say so in the journal.")
        if not (ev["flag_highlight"] or ev["flag_any"] or ev["flag_no_freeze"] or ev["bare"]):
            print("no event drought flagged")
        panels.append(("events", dev, ev))
    if want["loops"]:
        lp = run_loops(T, dev)
        out["loops"] = lp
        print(f"\nLOOPS (runs of near-identical bars, from {lp['source']}; norm <= {T.norm['loop']} bars)")
        for r in lp["runs"][:10]:
            print(f"  {'FLAG ' if r['flag'] else ('long, intended ' if r['intended'] else ('DJ end ' if r.get('dj_end') and r['n'] > T.norm['loop'] else '     '))}bars {r['bars']:>9s} "
                  f"{r['n']:3d} bars" + (f" (notes repeat every {r['period']})" if r["period"] else " (notes vary)")
                  + f"  {','.join(r['sections'])}")
        fl = [r for r in lp["runs"] if r["flag"]]
        if fl:
            print(f"FLAG {len(fl)} loop runs over {T.norm['loop']} bars without a variation (longest {fl[0]['n']}; "
                  f"{lp['over_share']:.0%} of the track's bars in them). "
                  "Vary every 4-8 bars (a fill, a dropped beat, a filter move, a note), change every 8-16; or mark the "
                  "section `\"loop\": \"long\"` with a reason.")
        else:
            print("no long loop flagged")
        panels.append(("loops", lp))
    if want["ring"]:
        rg = run_ring(T, stems_render=not getattr(a, "no_stems", False))
        out["ring"] = [{k: v for k, v in r.items() if k != "k"} for r in rg["rows"]]
        print(f"\nRING (persistent narrowband peaks: share of sounding frames >= {RING_PROM} dB over the third-octave "
              f"median; excess = the tone against the rest of its band; FLAG share >= {RING_SHARE}, excess >= "
              f"{RING_EXCESS} dB, >= 150 Hz, standing out in a third or more of the 8-bar blocks)")
        for r in rg["rows"]:
            print(f"  {'FLAG ' if r['flag'] else '     '}{r['hz']:7.1f} Hz {r['note']:5s} share {r['share']:.2f} prom "
                  f"{r['prominence_db']:4.1f} dB excess {r['excess_db']:+5.1f} dB  {r['rel_mix_dba']:+5.1f} dBA vs mix  "
                  f"span {r['span']}" + (f"  notes: {'; '.join(r['notes_on_it'])}" if r["notes_on_it"] else "")
                  + (f"  stems: {'; '.join(r['stems']) if isinstance(r.get('stems'), list) else r.get('stems')}" if r.get("stems") else ""))
        if not any(r["flag"] for r in rg["rows"]):
            print("no ringing flagged")
        panels.append(("ring", rg))
    draw(T, panels)
    json.dump(out, open(os.path.join(OUT, "ride.json"), "w"), indent=1, default=float)
    print(f"-> {os.path.join(OUT, 'ride.png')}, ride.json")


def draw(T, panels):
    if not panels:
        return
    fig, axs = plt.subplots(len(panels), 1, figsize=(15, 2.8 * len(panels) + 0.6), squeeze=False)
    x = np.arange(T.nb) + 1
    for ax, p in zip(axs[:, 0], panels):
        kind = p[0]
        if kind == "tension":
            _, ten, comp, rows = p
            for k, c in comp.items():
                ax.plot(x, c, lw=0.6, alpha=0.5, label=k)
            ax.plot(x, ten, color="k", lw=1.8, label="tension")
            for r in rows:
                a, b = [int(v) for v in r["bars"].split("-")]
                ax.axvspan(a - 0.5, b + 0.5, color="r" if r["flag"] else "tab:green", alpha=0.12)
                ax.text(a, ax.get_ylim()[1] if False else 2.6, ("DULL " if r["flag"] else "") + f"rise {r['rise']:.1f}",
                        fontsize=7, color="r" if r["flag"] else "g")
            ax.set_ylim(-3, 3)
            ax.legend(fontsize=6, ncol=6, loc="lower left")
            ax.set_title("tension per bar (black; components thin); shaded: respiros and builds (red = dull)", fontsize=8, loc="left")
        elif kind == "events":
            _, dev, ev = p
            xb = np.arange(len(dev)) / 4 + 1
            ax.plot(xb, dev, lw=0.5, color="gray")
            ax.axhline(EVENT_DB, color="r", lw=0.5, ls="--")
            for e in ev["events"]:
                c = "tab:red" if any(k in ("freeze", "kick stop") for k in e["kinds"]) else (
                    "tab:orange" if e["cls"] == "highlight" else "tab:blue")
                ax.plot(e["bar"] + (e["beat_in_bar"] - 1) / 4, min(e["dev"], 24), "v", color=c, ms=5)
            lh = ev["longest_without_highlight"]
            a, b = [int(v) for v in lh["bars"].split("-")]
            ax.axvspan(a - 0.5, b + 0.5, color="r" if ev["flag_highlight"] else "y", alpha=0.1)
            ax.set_ylim(0, 25)
            ax.set_title("events: departure from the learned beat (dB); red = freeze/kick stop, orange = highlight, blue = "
                         "change; shaded: the longest stretch without a highlight", fontsize=8, loc="left")
        elif kind == "loops":
            _, lp = p
            for r in lp["runs"]:
                a, b = [int(v) for v in r["bars"].split("-")]
                ax.barh(0, b - a + 1, left=a - 0.5, color="r" if r["flag"] else "tab:gray", height=0.6)
                if r["n"] >= 8:
                    ax.text((a + b) / 2, 0.4, str(r["n"]), ha="center", fontsize=7)
            ax.set_ylim(-1, 1)
            ax.set_yticks([])
            ax.set_title(f"loop runs (bars of near-identical repetition); red: longer than {T.norm['loop']}", fontsize=8, loc="left")
        elif kind == "ring":
            _, rg = p
            lf, prom, tfr = rg["lf"], rg["prom"], rg["tfr"]
            ax.imshow(np.clip(prom, 0, 20), aspect="auto", origin="lower", cmap="magma",
                      extent=[tfr[0], tfr[-1], 0, len(lf)])
            ticks = [k for k in range(0, len(lf), 48)]
            ax.set_yticks(ticks)
            ax.set_yticklabels([f"{lf[k]:.0f}" for k in ticks], fontsize=7)
            for r in rg["rows"]:
                if r["flag"]:
                    ax.axhline(r["k"], color="c", lw=0.8, ls="--")
                    ax.text(tfr[-1], r["k"], f" {r['hz']:.0f} Hz", color="c", fontsize=7, va="center")
            ax.set_title("ring: prominence over the third-octave median (dB, 0-20), time (s) x frequency (Hz); cyan: "
                         "flagged tones", fontsize=8, loc="left")
            continue
        for s in T.secs:
            ax.axvline(np.argmin(np.abs(T.edges - s["start"])) + 0.5, color="k", lw=0.4, alpha=0.4)
        ax.set_xlim(0.5, T.nb + 0.5)
        ax.set_xlabel("bar", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "ride.png"), dpi=75)
    plt.close(fig)
