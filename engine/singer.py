"""`singer`: a voice that sings words. Non-neural, local, every sound synthesized.

How it works (details and sources in docs/MANUAL.md, "Singer"):
1. Words. Each lyric word is spoken by eSpeak NG (a rule-based formant speech synthesizer, no recordings, no neural
   model; `apt install espeak-ng`) and analysed with the WORLD vocoder (`pip install pyworld`): pitch, spectral
   envelope (the vocal tract: formants and their transitions, consonant noise) and aperiodicity per 5 ms frame.
2. Syllables on notes. A word with hyphens ("a-round") is cut at the energy dips between its vowel nuclei. In each
   syllable the onset consonants keep their spoken length and land just before the note (singers put consonants
   ahead of the beat so the vowel starts on it), the vowel is stretched over the note (lingering on its first part,
   as singers hold the first vowel of a diphthong), and the coda consonants close the note.
3. Voice. The melody's own pitch curve (glides, delayed vibrato, slow drift, jitter, an optional scoop; `tune` pulls
   it toward the exact note; each note's pitch starts with its onset consonant) drives one of two sources through the
   spoken envelope, one level per syllable (set by its vowel, so consonants keep their spoken dip), with the envelope
   smoothed across syllable joins (`coartic_ms`):
   - `breathy` (default): the `vox` character, an additive soft harmonic source plus breath noise, both shaped by
     the word's envelope: soft, breathy, flute-like, but with vowels and consonants you can read;
   - `pulse`: WORLD's own pulse/noise excitation: a brighter, more processed (vocoder-like) voice; with `tune` 1
     and `retune_ms` near 0 it gives the hard-tuned club vocal.
   Formant shift, doubling (a second take, its own timing and pitch wobble, panned), breath and inhales on top.
4. `"source": "tts"` (engine/tts_words.py): the words come from a local neural text-to-speech (Kokoro, Apache 2.0)
   spoken neutrally and cached, instead of eSpeak; the same plan lays them on the notes, and WORLD resynthesizes the
   spoken voice itself (its own envelope and aperiodicity: formants preserved, `formant` shifts them) on the melody's
   pitch. The neural model only samples the words; tuning, timing, breath and doubling are the engine's.
Intelligibility limits (docs/MANUAL.md "Register"): keep sung words at A3-D5 and about 1-3 syllables a second; above E5 the harmonics are too sparse to draw the vowels and syllables become chirps.
"""
import functools
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy import signal

SR = 44100
FP = 5.0  # WORLD frame period, ms
HOP = SR * FP / 1000.0

_WARNED = set()


def _warn(msg):
    if msg not in _WARNED:
        _WARNED.add(msg)
        print("warning: singer: " + msg, file=sys.stderr)


def _seed(*parts):
    h = hashlib.sha1(repr(parts).encode()).digest()
    return int.from_bytes(h[:4], "little")


# ------------------------------------------------------------------ eSpeak NG + WORLD analysis

def _espeak_bin():
    b = shutil.which("espeak-ng") or shutil.which("espeak")
    if b is None:
        raise RuntimeError("singer needs eSpeak NG: apt install espeak-ng")
    return b


@functools.lru_cache(maxsize=4096)
def _speak(text, voice, speed, pitch):
    """eSpeak NG audio for text -> (float64 array, sr)."""
    import soundfile as sf
    fd, path = tempfile.mkstemp(suffix=".wav", prefix="singer_")
    os.close(fd)
    try:
        subprocess.run([_espeak_bin(), "-v", voice, "-s", str(int(speed)), "-p", str(int(pitch)), "-z",
                        "-w", path, text], check=True, capture_output=True)
        x, sr = sf.read(path, dtype="float64")
    finally:
        os.unlink(path)
    if x.ndim > 1:
        x = x.mean(1)
    return x, sr


@functools.lru_cache(maxsize=4096)
def _phonemes(text, voice):
    """eSpeak NG's phoneme mnemonics for text ('' if unavailable)."""
    try:
        r = subprocess.run([_espeak_bin(), "-v", voice, "-q", "-x", text], check=True, capture_output=True, text=True)
        return r.stdout.strip()
    except Exception:  # pragma: no cover
        return ""


@functools.lru_cache(maxsize=4096)
def _analyze(text, voice, speed, pitch):
    """WORLD analysis of a spoken word, trimmed to its sounding part. Returns dict of frame arrays."""
    import pyworld as pw
    x, sr = _speak(text, voice, speed, pitch)
    x = np.ascontiguousarray(x)
    f0, t = pw.harvest(x, sr, frame_period=FP, f0_floor=60, f0_ceil=500)
    sp = pw.cheaptrick(x, f0, t, sr)
    ap = pw.d4c(x, f0, t, sr)
    freqs = np.linspace(0, sr / 2, sp.shape[1])
    band = (freqs > 250) & (freqs < 4000)
    e_db = 10 * np.log10(sp[:, band].mean(1) + 1e-20)
    # frame loudness from the waveform itself (sp is level-normalised per frame in silence)
    hop = int(sr * FP / 1000)
    rms = np.array([np.sqrt(np.mean(x[max(0, i * hop - hop):i * hop + hop] ** 2) + 1e-12) for i in range(len(f0))])
    r_db = 20 * np.log10(rms)
    on = np.where(r_db > r_db.max() - 45)[0]
    a, b = (on[0], on[-1] + 1) if len(on) else (0, len(f0))
    # a word-initial /h/: eSpeak's Klatt voices make it breathy-voiced and WORLD tracks a pitch through it, so it
    # would be sung as a tone (an "ee" glide instead of a breath). Make it breath: unvoiced until the level comes
    # within 12 dB of the word's peak
    if _phonemes(text, voice).lstrip("',%=").startswith("h"):
        k = a
        while k < b and r_db[k] < r_db[a:b].max() - 12:
            k += 1
        f0 = f0.copy()
        f0[a:k] = 0.0
    return dict(f0=f0[a:b], sp=sp[a:b], ap=ap[a:b], e=e_db[a:b], r=r_db[a:b], sr=sr, freqs=freqs)


def _nuclei(w, n_syl):
    """Split an analysed word into n_syl syllables at the energy dips between voiced peaks.
    Returns list of (start, end) frame ranges, or None."""
    voiced = w["f0"] > 0
    r = np.where(voiced, w["r"], w["r"].min())
    if n_syl == 1:
        return [(0, len(r))]
    k = 9
    rs = np.convolve(r, np.ones(k) / k, mode="same")
    peaks, _ = signal.find_peaks(rs, distance=8, prominence=2.0)
    if len(peaks) < n_syl:
        return None
    peaks = np.sort(peaks[np.argsort(rs[peaks])[-n_syl:]])
    cuts = [0]
    for p0, p1 in zip(peaks[:-1], peaks[1:]):
        cuts.append(p0 + int(np.argmin(rs[p0:p1 + 1])))
    cuts.append(len(r))
    return list(zip(cuts[:-1], cuts[1:]))


def _parts(w, a, b, thresh_db=7.0):
    """Onset, nucleus, coda frame ranges inside [a, b): the nucleus is the voiced stretch within thresh_db of the
    syllable's loudest voiced frame."""
    f0, r = w["f0"][a:b], w["r"][a:b]
    v = np.where(f0 > 0)[0]
    if len(v) == 0:
        m = a + (b - a) // 2
        return (a, m), (m, m + 1), (m + 1, b)
    top = r[v].max()
    core = v[r[v] > top - thresh_db]
    n0, n1 = a + core[0], a + core[-1] + 1
    return (a, n0), (n0, n1), (n1, b)


def _syllables(word, n_syl, voice, speed, pitch):
    """Analysed syllables of one lyric word (hyphens split it). Each: dict(w=analysis, on, nu, co ranges)."""
    pieces = [s for s in word.split("-") if s]
    clean = "".join(pieces)
    w = _analyze(clean, voice, speed, pitch)
    rng = _nuclei(w, len(pieces)) if len(w["f0"]) > 4 else None
    out = []
    if rng is not None:
        for a, b in rng:
            on, nu, co = _parts(w, a, b)
            out.append(dict(w=w, on=on, nu=nu, co=co))
        return out
    for s in pieces:  # fallback: speak each syllable on its own
        ws = _analyze(s, voice, speed, pitch)
        on, nu, co = _parts(ws, 0, len(ws["f0"]))
        out.append(dict(w=ws, on=on, nu=nu, co=co))
    return out


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

VOICES = {  # name -> (eSpeak NG voice, formant shift semitones); Klatt variants sound the least buzzy
    "female": ("en-us+klatt3", 1.5), "male": ("en-us+klatt3", 0.0), "female2": ("en-us+f3", 1.0),
}


def _plan(p, notes, total_n, rng, time_jit=0.0, with_ids=False, extra=None):
    """Build the output frame plan: per frame a source (analysis, frame index) or silence, plus a target pitch."""
    voice_name = p.get("espeak", VOICES.get(p.get("voice", "female"), VOICES["female"])[0])
    speed = p.get("speed", 140)
    epitch = p.get("espeak_pitch", 50)
    toks = list(p.get("_lyrics") or [])
    nF = int(total_n / HOP) + 2
    src_w = [None] * nF
    src_i = np.zeros(nF)
    tgt = np.zeros(nF)  # target note Hz per frame (0 = none)
    vel = np.zeros(nF)
    start = np.zeros(nF, dtype=bool)  # first frame of a fresh (non-glide) note's vowel
    cons = np.zeros(nF, dtype=bool)  # onset/coda (consonant) frames
    fresh = np.zeros(nF, dtype=bool)  # frame belongs to a non-glide note
    # group notes into syllables
    groups = []
    for i, nt in enumerate(notes):
        tok = nt.get("syl")
        if tok is None:
            tok = toks[i] if i < len(toks) else "_"
        if tok == "_" and groups:
            groups[-1]["notes"].append(nt)
        else:
            if tok == "_":
                tok = ("oo", 0, 1)
                _warn("a melisma '_' with no syllable before it sings 'oo'")
            groups.append(dict(tok=tok, notes=[nt]))
    if p.get("source") == "tts" and p.get("tts_mode", "phrase") == "phrase":
        _phrase_syllables(p, groups)
    wcache = {}
    for g in groups:
        if "syl" in g:  # set by phrase mode
            continue
        wd, si, n = g["tok"]
        if (wd, n) not in wcache:
            try:
                if p.get("source") == "tts":
                    import tts_words
                    wcache[(wd, n)] = tts_words.syllables(wd, n, p)
                else:
                    wcache[(wd, n)] = _syllables(wd, n, voice_name, speed, epitch)
            except Exception as e:  # pragma: no cover
                _warn(f"could not speak '{wd}': {e}")
                wcache[(wd, n)] = None
        sy = wcache[(wd, n)]
        g["syl"] = sy[min(si, len(sy) - 1)] if sy else None
    jit = time_jit
    sid = np.full(nF, -1)  # syllable index per frame (for the per-syllable level)
    vowel = np.zeros(nF, dtype=bool)  # vowel (nucleus) frames
    lead_ms = p.get("pitch_lead_ms")  # None: the pitch moves where the onset consonant starts (see below)
    recs = []  # `tts`: per syllable, where it ends and starts (for releases and attacks)
    # note times with the timing jitter, drawn up front in the same order as before (t0, then t_end, per syllable)
    T0, TE = [], []
    for g in groups:
        T0.append(g["notes"][0]["t0"] / HOP + (rng.normal(0, jit) if jit else 0))
        TE.append((g["notes"][-1]["t0"] + g["notes"][-1]["n"]) / HOP + (rng.normal(0, jit) if jit else 0))
    max_on = p.get("max_onset_ms", 160) / FP
    keep_joins = p.get("source") == "tts" and bool(p.get("keep_joins", True))
    gap_f = float(p.get("phrase_gap_s", 0.3)) * 1000 / FP

    ob = float(p.get("onset_beat", 0) or 0) if p.get("source") == "tts" else 0.0

    def split_onset(k):
        """`onset_beat` > 0: syllable k's onset frames before and after its note start. Human singers start the
        word's consonants on the beat and let the vowel follow (GTSinger: the score grid fits syllable starts best,
        docs/voice/GENERAL.md "Timing"); `onset_beat` is the share of the onset sung after the note start, at most half
        the note; the rest stays before it, within the old room rule."""
        sk = groups[k]["syl"]
        pk = groups[k - 1]["notes"][0]["t0"] / HOP if k > 0 else -1e9
        n = sk["on"][1] - sk["on"][0]
        if p.get("onset_fit") and n > 0:
            # how long a singer makes a spoken onset (GTSinger paired speech, same singer and words): about
            # 59 ms + 0.54 x the spoken length; applied only to lengthen
            n = max(n, int(round((59.0 + 0.54 * n * FP) / FP)))
        n = min(n, int(max_on))
        post = min(int(round(ob * n)), int(0.5 * (TE[k] - T0[k])))
        pre = min(n - post, int(max(2.0, 0.45 * (T0[k] - pk))))
        return pre, post

    def onset_frames(k):
        """How many frames syllable k's onset takes before its note (the same rule as below)."""
        sk = groups[k]["syl"]
        if sk is None:
            return 0
        if ob > 0:
            return split_onset(k)[0]
        pk = groups[k - 1]["notes"][0]["t0"] / HOP if k > 0 else -1e9
        return min(sk["on"][1] - sk["on"][0], int(min(max_on, max(2.0, 0.45 * (T0[k] - pk)))))

    for gi, g in enumerate(groups):
        s = g["syl"]
        ns = g["notes"]
        t0, t_end = T0[gi], TE[gi]
        if keep_joins and gi + 1 < len(groups) and T0[gi + 1] - t_end < gap_f:
            # `tts`: when the next syllable follows closely, this one ends exactly where the next onset begins, so
            # the consonants at the join keep their spoken length (the next onset used to be written over this
            # syllable's coda: "hold on" lost its /l/) and the next vowel still starts on its note
            t_end = T0[gi + 1] - onset_frames(gi + 1)
        nxt0 = groups[gi + 1]["notes"][0]["t0"] / HOP if gi + 1 < len(groups) else nF
        n_on = 0
        n_pre = n_post = 0
        if s is not None:
            on, nu, co = s["on"], s["nu"], s["co"]
            n_on, n_nu, n_co = on[1] - on[0], nu[1] - nu[0], co[1] - co[0]
            # onset room: at most max_onset_ms, and at most 45% of the gap since the previous syllable started, so a
            # consonant cluster before a fast note is spoken faster instead of swallowing the previous vowel
            prev0 = groups[gi - 1]["notes"][0]["t0"] / HOP if gi > 0 else -1e9
            n_room = int(min(p.get("max_onset_ms", 160) / FP, max(2.0, 0.45 * (t0 - prev0))))
            n_src_on = n_on
            if ob > 0:
                n_pre, n_post = split_onset(gi)
                n_on = n_pre + n_post
            else:
                n_on = min(n_on, n_room)
                n_pre = n_on
        vs0 = t0 + n_post  # where the vowel starts: on the note, or after the part of the onset sung on the beat
        # pitch targets. The new note's pitch starts with its onset consonant (singers change pitch on the consonant,
        # so the previous vowel keeps its own note to the end). `pitch_lead_ms` sets a fixed lead instead (the first
        # version used 200 ms, which moved the pitch inside the previous vowel: on short notes most of a syllable was
        # sung on the next syllable's note).
        lead = int(round(lead_ms / FP)) if lead_ms is not None else int(round(n_pre))
        ge = float(p.get("glide_early", 0) or 0)
        if ge > 0 and float(p.get("portamento_ms", 0) or 0) > 0:
            # `tts`: start the pitch move earlier, so it passes through the consonants of the join instead of landing
            # in the next vowel (measured: 75-100% of the move happened after the next vowel had started)
            tn = float(np.clip(p.get("tune", 0.3), 0, 1))
            Tf = (float(p["portamento_ms"]) * (1 - tn) + float(p.get("retune_ms", 15)) * tn) / FP
            lead += int(round(ge * Tf))
        for k, nt in enumerate(ns):
            a = int(round(nt["t0"] / HOP))
            b = int(round(ns[k + 1]["t0"] / HOP)) if k + 1 < len(ns) else int(round(t_end)) + 1
            b2 = int(round(nxt0)) if k + 1 == len(ns) else b
            a0 = max(a - lead, 0) if k == 0 else a
            tgt[a0:min(b2, nF)] = nt["f"]
            vel[a0:min(b2, nF)] = nt["vel"]
            fresh[a0:min(b2, nF)] = not nt.get("glide")
            if 0 <= a < nF and (k > 0 or not nt.get("glide")):
                start[a] = not nt.get("glide")
        if s is None:
            continue
        avail = t_end - vs0
        # coda: natural length, squeezed if the note is short (keep at least 40% of the note for the vowel)
        c_len = min(n_co, max(1.0, avail * 0.45))
        v_len = max(avail - c_len, 1.0)
        # onset before the note
        for j in range(n_on):
            f = int(round(t0 - n_pre + j))
            if 0 <= f < nF:
                src_w[f], src_i[f] = s["w"], on[0] + n_src_on * j / max(n_on, 1)
                cons[f] = True
                sid[f] = gi
                if extra is not None:
                    extra.setdefault("onset", np.zeros(nF, dtype=bool))[f] = True
        # vowel: linger on the first part (u**1.6)
        L = int(np.ceil(v_len))
        if keep_joins:  # whole frames, so the coda ends exactly where the next onset starts
            L = max(1, int(round(t_end)) - int(round(vs0)) - int(np.ceil(c_len)))
        core = p.get("stretch") == "core" and L > n_nu
        if core:
            # stretch only the vowel's steady core: its first and last `trans_ms` (the transitions from the onset and
            # into the coda) keep their spoken speed, as concatenative singing synthesis keeps phoneme transitions as
            # recorded and sustains only the stationary vowel (Kenmochi & Ohshita 2007)
            tr_f = int(round(float(p.get("trans_ms", 40)) / FP))
            hd = tl = min(tr_f, n_nu // 3)
            c_src = max(n_nu - hd - tl, 1)
            c_out = max(L - hd - tl, 1)
        for j in range(L):
            f = int(round(vs0)) + j
            if 0 <= f < nF:
                if core and j < hd:
                    idx = nu[0] + j
                elif core and j >= L - tl:
                    idx = nu[1] - (L - j)
                elif core:
                    u = (j - hd) / max(c_out - 1, 1)
                    idx = nu[0] + hd + (c_src - 1) * u ** p.get("linger", 1.6)
                else:
                    u = j / max(L - 1, 1)
                    idx = nu[0] + (n_nu - 1) * u ** p.get("linger", 1.6)
                src_w[f], src_i[f] = s["w"], idx
                sid[f], vowel[f] = gi, True
        C = int(np.ceil(c_len))
        tail = min(int(s.get("tail", 0)), n_co, C)  # `tts`: a final stop's closure and release keep natural speed
        for j in range(C):
            f = int(round(vs0)) + L + j
            if 0 <= f < nF:
                if tail and j >= C - tail:
                    src_w[f], src_i[f] = s["w"], co[1] - (C - j)
                elif tail:
                    src_w[f], src_i[f] = s["w"], co[0] + (n_co - tail - 1) * j / max(C - tail - 1, 1)
                else:
                    src_w[f], src_i[f] = s["w"], co[0] + (n_co - 1) * j / max(C - 1, 1) if n_co else nu[1] - 1
                cons[f] = n_co > 0
                sid[f] = gi
        if extra is not None:
            recs.append(dict(gi=gi, w=s["w"], co1=co[1] if n_co else nu[1], last=bool(s.get("last")),
                             end_f=int(round(vs0)) + L + C, first_f=int(round(t0 - n_pre)), n_on=n_on,
                             voiced_on=bool((s["w"]["f0"][on[0]:on[0] + 3] > 0).all()),
                             vel=ns[-1]["vel"]))
    if extra is not None:
        extra["gain"] = _edges(p, recs, src_w, src_i, sid, vel, nF)
    if with_ids:
        return src_w, src_i, tgt, vel, start, fresh, groups, cons, sid, vowel
    return src_w, src_i, tgt, vel, start, fresh, groups, cons


def _edges(p, recs, src_w, src_i, sid, vel, nF):
    """`tts`: no hard edges. Every syllable followed by silence releases into it (`tts_words.release`: the spoken
    tail and decay when it ends its word or phrase, else a ~100 ms fade of its last frame), for up to `release_ms`
    (200), only into frames nothing else uses; if the next onset or the limit cuts it short, it fades out over
    `cutfade_ms` (40). A short gap between two syllables of one phrase (under `phrase_gap_s`) is bridged instead:
    the frame where they meet in the spoken phrase is held at full level. Every syllable that starts after silence
    gets an attack ramp: `attack_ms` (12) on an unvoiced consonant onset, `attack_ms_vowel` (40) when it starts
    voiced (a vowel, or l, r, m, n, w, y).
    Returns a per-frame level multiplier."""
    import tts_words
    rg = np.ones(nF)
    rel_max = int(float(p.get("release_ms", 200)) / FP)
    cut = int(float(p.get("cutfade_ms", 40)) / FP)
    gap = int(float(p.get("phrase_gap_s", 0.3)) * 1000 / FP)
    for r in recs:
        f = r["end_f"]
        if not (0 <= f < nF) or src_w[f] is not None or rel_max <= 0:
            continue
        run = 0
        while f + run < nF and src_w[f + run] is None and run <= gap:
            run += 1
        if not r["last"] and f + run < nF and src_w[f + run] is not None and run < gap:
            # a short gap inside a phrase (between two notes, not a rest): bridge it by holding the frame where this
            # syllable meets the next one in the spoken phrase, at full level: no fade, no attack, no stitch
            j = max(r["co1"] - 1, 0)
            for k in range(run):
                src_w[f + k], src_i[f + k] = r["w"], j
                sid[f + k] = r["gi"]
                vel[f + k] = r["vel"]
            continue
        wr = tts_words.release(r["w"], r["co1"], r["last"])
        n = len(wr["f0"])
        k = 0
        while k < min(rel_max, n) and f + k < nF and src_w[f + k] is None:
            src_w[f + k], src_i[f + k] = wr, k
            sid[f + k] = r["gi"]
            vel[f + k] = r["vel"]
            k += 1
        if k < n:  # cut short: fade out (equal-power curve)
            m = min(k, cut)
            if m:
                rg[f + k - m:f + k] *= np.cos(np.linspace(0, np.pi / 2, m + 1)[1:]) ** 2
    for r in recs:
        fs = r["first_f"]
        if not (0 < fs < nF) or not (src_w[fs - 1] is None or rg[fs - 1] < 0.1):
            continue
        A = max(1, int(round(float(p.get("attack_ms_vowel", 40) if r["voiced_on"] else p.get("attack_ms", 12)) / FP)))
        m = min(A, nF - fs)
        rg[fs:fs + m] *= np.sin(np.linspace(0, np.pi / 2, A + 1)[1:m + 1]) ** 2
    return rg


def _phrase_syllables(p, groups):
    """`tts` phrase mode: split the sung syllables into phrases at rests of at least `phrase_gap_s` (0.3 s; only
    between words), have the TTS speak each phrase in one go, and give each syllable its segment of the phrase.
    A phrase that doesn't segment cleanly falls back to word mode (with a warning)."""
    import tts_words
    gap = float(p.get("phrase_gap_s", 0.3)) * SR
    phrases, cur, prev_end = [], [], None
    for gi, g in enumerate(groups):
        si = g["tok"][1]
        g0 = g["notes"][0]["t0"]
        if cur and si == 0 and prev_end is not None and g0 - prev_end >= gap:
            phrases.append(cur)
            cur = []
        cur.append(gi)
        prev_end = g["notes"][-1]["t0"] + g["notes"][-1]["n"]
    if cur:
        phrases.append(cur)
    for ph in phrases:
        toks = [groups[gi]["tok"] for gi in ph]
        if toks[0][1] != 0 or toks[-1][1] != toks[-1][2] - 1:
            continue  # a phrase must hold whole words
        words = [t[0] for t in toks if t[1] == 0]
        try:
            sy = tts_words.phrase_syllables(words, p)
        except Exception as e:  # pragma: no cover
            _warn(f"phrase mode failed for '{' '.join(words)}': {e}")
            sy = None
        if sy is None or len(sy) != len(ph):
            _warn(f"couldn't cut the spoken phrase '{' '.join(words)}' into {len(ph)} syllables; singing it word by "
                  "word")
            continue
        for gi, s_ in zip(ph, sy):
            groups[gi]["syl"] = s_


def _pitch_curve(p, tgt, start, fresh, rng, detune_cents=0.0):
    """Sung pitch per frame (Hz) from the note targets: scoop, glide, vibrato, drift, jitter; `tune` pulls toward
    the exact note."""
    nF = len(tgt)
    tune = float(np.clip(p.get("tune", 0.3), 0, 1))
    midi = np.where(tgt > 0, 69 + 12 * np.log2(np.maximum(tgt, 1) / 440.0), 0.0)
    # fill gaps with the last note so glides and onsets have a pitch
    last = 0.0
    filled = midi.copy()
    for i in range(nF):
        if filled[i] > 0:
            last = filled[i]
        else:
            filled[i] = last
    if (filled > 0).any():
        first = filled[filled > 0][0]
        filled[filled == 0] = first
    # transition smoothing: natural portamento (glide_ms) vs hard-tune (retune_ms); a fresh (non-glide) note
    # jumps to its pitch (then scoops), a `~` note glides from the previous one
    glide_ms = p.get("glide_ms", 70) * (1 - tune) + p.get("retune_ms", 15) * tune
    port = float(p.get("portamento_ms", 0) or 0)
    rng2 = np.random.default_rng(_seed("sung", p.get("seed", 1), detune_cents))  # only the options below draw from it
    if port > 0:
        # sung transitions: every note change glides like a singer's (a damped second-order move, so the pitch can
        # overshoot a little and settle) over about portamento_ms (blended toward retune_ms by `tune`)
        T = (port * (1 - tune) + p.get("retune_ms", 15) * tune) / 1000.0
        os_ = float(np.clip(p.get("overshoot", 0.08), 1e-3, 0.5))
        zeta = -np.log(os_) / np.sqrt(np.pi ** 2 + np.log(os_) ** 2)
        # a short note can't spend its length gliding: each glide takes at most 35% of its note
        Tn = np.full(nF, T)
        ch = [0] + [i for i in range(1, nF) if filled[i] != filled[i - 1]] + [nF]
        for a_, b_ in zip(ch[:-1], ch[1:]):
            Tn[a_:b_] = min(T, 0.35 * (b_ - a_) * FP / 1000)
        wn_ = 1.8 / np.maximum(Tn, 0.01)
        dt = FP / 1000
        sm = filled.copy()
        x, v = filled[0], 0.0
        for i in range(nF):
            wn = wn_[i]
            v += dt * (wn * wn * (filled[i] - x) - 2 * zeta * wn * v)
            x += dt * v
            sm[i] = x
    else:
        a1 = 1.0 / max(1.0, glide_ms / FP)
        sm = filled.copy()
        for i in range(1, nF):
            if filled[i] != filled[i - 1] and fresh[i]:
                sm[i] = filled[i]
            else:
                sm[i] = sm[i - 1] + a1 * (filled[i] - sm[i - 1])
    # scoop up into fresh notes (off by default: a scoop on every syllable, together with the formant sweep of the
    # onset consonant, reads as a bird-like chirp on high notes; use it on a few long notes)
    scoop = p.get("scoop", 0.0) * (1 - tune)
    env = np.zeros(nF)
    idx = np.where(start)[0]
    tt = np.arange(nF) * FP / 1000
    some = float(p.get("scoop_some", 1.0))  # the share of notes that get the scoop (chosen at random)
    for a in idx:
        L = min(nF - a, int(0.25 / (FP / 1000)))
        wgt = 1.0 if some >= 1 else float(rng2.random() < some)
        env[a:a + L] = np.maximum(env[a:a + L], wgt * np.exp(-tt[:L] / 0.05))
    # vibrato, delayed after each fresh note
    since = np.zeros(nF)
    c = 1e9
    for i in range(nF):
        c = 0 if start[i] else c + FP / 1000
        since[i] = c
    vdepth, vrate, vdelay = p.get("vibrato", 0.25), p.get("vib_rate", 5.2), p.get("vib_delay", 0.25)
    rate = vrate * (1 + 0.06 * np.interp(tt, np.linspace(0, tt[-1] + 1e-3, 16), rng.normal(0, 1, 16)))
    vmin, vary, vlate = float(p.get("vib_min_s", 0)), float(p.get("vib_vary", 0)), float(p.get("vib_late", 0))
    venv = None
    if vmin > 0 or vary > 0 or vlate > 0:
        # sung vibrato: only on notes at least vib_min_s long, starting late (after vib_delay or vib_late of the
        # note, whichever is later) and easing in over 0.3 s, each note with its own depth and rate (vib_vary)
        venv = np.zeros(nF)
        rmul = np.ones(nF)
        bounds = list(idx) + [nF]
        for k, a in enumerate(idx):
            b = bounds[k + 1]
            z = np.where(tgt[a:b] <= 0)[0]
            e = a + (int(z[0]) if len(z) else b - a)
            dur = (e - a) * FP / 1000
            depth = 1.0 + vary * rng2.uniform(-1, 1)
            rmul[a:b] = 1.0 + 0.12 * vary * rng2.uniform(-1, 1)
            if dur < vmin:
                continue
            d0 = max(vdelay, vlate * dur)
            tl = (np.arange(e - a) * FP / 1000 - d0) / 0.3
            venv[a:e] = depth * np.clip(tl, 0, 1)
        rate = rate * rmul
    vph = 2 * np.pi * np.cumsum(rate) * FP / 1000 + rng.random() * 6
    if venv is None:
        vib = vdepth * np.sin(vph) * np.clip((since - vdelay) / 0.4, 0, 1)
    else:
        vib = vdepth * np.sin(vph) * venv
    drift = np.interp(tt, np.linspace(0, tt[-1] + 1e-3, max(4, int(tt[-1] * 2))),
                      rng.normal(0, 0.08, max(4, int(tt[-1] * 2)))) * (1 - tune)
    dc = float(p.get("drift_cents", 0))
    if dc > 0:  # a slow wander of its own (about 0.7 points a second), scaled by 1 - `tune`
        k = max(4, int(tt[-1] * 0.7) + 2)
        drift = drift + np.interp(tt, np.linspace(0, tt[-1] + 1e-3, k), rng2.normal(0, dc / 100.0, k)) * (1 - tune)
    jit = signal.lfilter([0.3], [1, -0.7], rng.normal(0, p.get("jitter", 0.04), nF))
    m = sm - scoop * env + vib + drift + jit + detune_cents / 100.0
    return 440.0 * 2 ** ((m - 69) / 12)


def _interp_frames(src_w, src_i, nbins_out, fs_out, shift, coartic_ms=0.0):
    """Spectral envelope, aperiodicity and voicing per output frame, resampled to the output frequency grid with a
    formant shift (ratio). `coartic_ms` > 0 smooths the envelope across the joins between syllables (where the frames
    jump to another word or to another part of the same word), so the vocal tract moves from one syllable into the
    next instead of switching between frames: each word is spoken on its own by eSpeak, so without this there is
    no coarticulation across syllables."""
    nF = len(src_w)
    f_out = np.linspace(0, fs_out / 2, nbins_out)
    sp = np.full((nF, nbins_out), 1e-12)
    ap = np.ones((nF, nbins_out))
    voiced = np.zeros(nF)
    live = np.zeros(nF, dtype=bool)
    cache = {}
    for f in range(nF):
        w = src_w[f]
        if w is None:
            continue
        x = src_i[f]
        i0 = int(np.floor(x))
        i1 = min(i0 + 1, len(w["f0"]) - 1)
        i0 = min(max(i0, 0), len(w["f0"]) - 1)
        a = x - np.floor(x)
        key = id(w)
        if key not in cache:
            cache[key] = (np.log(w["sp"] + 1e-20), w["ap"], w["freqs"])
        lsp, wap, fr = cache[key]
        l = (1 - a) * lsp[i0] + a * lsp[i1]
        q = (1 - a) * wap[i0] + a * wap[i1]
        src_f = f_out / shift
        sp[f] = np.exp(np.interp(src_f, fr, l, right=l[-1] - 12))
        ap[f] = np.interp(src_f, fr, q, right=1.0)
        voiced[f] = 1.0 if (w["f0"][i0] > 0 or w["f0"][i1] > 0) else 0.0
        live[f] = True
    K = int(round(coartic_ms / FP / 2))
    if K >= 1:
        joins = [f for f in range(1, nF) if live[f] and live[f - 1] and voiced[f] > 0 and voiced[f - 1] > 0
                 and (src_w[f] is not src_w[f - 1] or abs(src_i[f] - src_i[f - 1]) > 2.5)]
        if joins:
            lsp = np.log(sp)
            out = lsp.copy()
            for j in joins:
                a, b = max(j - K, 0), min(j + K, nF)
                if not (live[a:b].all() and (voiced[a:b] > 0).all()):
                    a, b = j - 1, j + 1  # don't smear into silence or into an unvoiced consonant
                    if a < 0 or b > nF:
                        continue
                # a linear path in log-envelope from the frame before the window to the frame after it, blended in
                # with a raised-cosine weight that is 1 at the join
                left, right = lsp[max(a - 1, 0)], lsp[min(b, nF - 1)]
                for f in range(a, b):
                    u = (f - a + 0.5) / (b - a)
                    wgt = 0.5 * (1 + np.cos(np.pi * (f - (j - 0.5)) / max(K + 0.5, 1)))
                    out[f] = (1 - wgt) * lsp[f] + wgt * ((1 - u) * left + u * right)
            sp = np.exp(out)
    return sp, ap, voiced, live, f_out


def _take(p, notes, total_n, seed, time_jit_ms=0.0, detune_cents=0.0):
    import pyworld as pw
    rng = np.random.default_rng(seed)
    ex = {} if p.get("source") == "tts" else None
    src_w, src_i, tgt, vel, start, fresh, groups, cons, sid, vowel = _plan(p, notes, total_n, rng,
                                                                           time_jit=time_jit_ms / FP, with_ids=True,
                                                                           extra=ex)
    f0 = _pitch_curve(p, tgt, start, fresh, rng, detune_cents)
    fft = pw.get_cheaptrick_fft_size(SR)
    mode = p.get("source", "breathy")
    fdef = 0.0 if mode == "tts" else VOICES.get(p.get("voice", "female"), VOICES["female"])[1]
    shift = 2 ** (p.get("formant", fdef) / 12)
    sp, ap, voiced, live, f_out = _interp_frames(src_w, src_i, fft // 2 + 1, SR, shift,
                                                 coartic_ms=float(p.get("coartic_ms", 40)))
    tr = p.get("_trace")
    if isinstance(tr, dict) and "src_w" not in tr:  # tools/joincheck.py: which source frame went where
        tr.update(src_w=list(src_w), src_i=np.array(src_i), groups=groups, sid=np.array(sid), f0=np.array(f0),
                  voiced=np.array(voiced), tgt=np.array(tgt))
    nF = len(src_w)
    # smooth voicing so consonant/vowel edges cross-fade over ~15 ms
    vs = np.convolve(voiced, np.ones(3) / 3, mode="same")
    # per-syllable level: bring every vowel to the same loudness (singers sustain evenly), keep consonants relative
    lvl = np.zeros(nF)
    band = (f_out > 250) & (f_out < 4000)
    e = sp[:, band].mean(1)
    gain = np.ones(nF)
    on = np.where(live)[0]
    level_mode = p.get("level", "syllable")
    if len(on) and level_mode == "syllable":
        # one gain per syllable, set by its vowel: the vowels sit level and every consonant keeps its spoken level
        # against its own vowel (the first version followed the level frame by frame over 60 ms, which lifted
        # nasals, glides and /h/ to vowel level: consonants came out 0-3 dB above the vowel instead of 6-9 dB below,
        # so syllables lost their edges)
        ref = np.percentile(e[on][voiced[on] > 0], 75) if (voiced[on] > 0).any() else e[on].max()
        for gi in np.unique(sid[sid >= 0]):
            fr = (sid == gi)
            vf = fr & vowel & (voiced > 0)
            ev = np.percentile(e[vf], 75) if vf.any() else (e[fr].max() if fr.any() else ref)
            gain[fr] = np.clip(np.sqrt(ref / max(ev, ref * 1e-3)), 0.3, 3.0)
    elif len(on):
        ref = np.percentile(e[on][voiced[on] > 0], 75) if (voiced[on] > 0).any() else e[on].max()
        # slow level follower over vowels (60 ms), so plosive/fricative frames keep their natural level
        ev = np.where(voiced > 0, e, 0)
        cnt = np.convolve((voiced > 0).astype(float), np.ones(12), mode="same")
        sm = np.convolve(ev, np.ones(12), mode="same") / np.maximum(cnt, 1)
        gain = np.where(sm > 0, np.sqrt(ref / np.maximum(sm, ref * 1e-3)), 1.0)
        gain = np.clip(gain, 0.3, 3.0)
    pros = float(p.get("prosody", 0) or 0) if ex is not None else 0.0
    acc = np.zeros(nF)
    if pros > 0:
        # `tts`: the melody sets the emphasis, not the spoken phrase: each syllable's spectral tilt and onset force
        # move toward the same syllable spoken alone (its citation form), by `prosody`; spoken pitch accents are
        # left out of `micro` on accented syllables
        shape = np.clip(np.log2(np.maximum(f_out, 1) / 1000.0) / 2.0, 0, 1)
        ons = ex.get("onset", np.zeros(nF, dtype=bool))
        for gi in np.unique(sid[sid >= 0]):
            sy = groups[gi].get("syl") or {}
            fr = sid == gi
            tf = float(sy.get("tilt_fix", 0.0)) * pros / 0.85
            if tf:
                sp[fr] = sp[fr] * (10 ** (tf * shape / 10))[None, :]
            of = float(sy.get("onf_fix", 0.0)) * pros
            if of:
                gain[fr & ons] *= 10 ** (of / 20)
            if float(sy.get("accent", 0.0)) > 1.0:
                acc[fr] = 1.0
    if isinstance(tr, dict) and "env_tilt" not in tr:  # tools/joincheck.py: tilt of the envelope actually sung
        hb, lb = (f_out >= 2000) & (f_out < 8000), (f_out >= 100) & (f_out < 1000)
        tr["env_tilt"] = 10 * np.log10((sp[:, hb].sum(1) + 1e-20) / (sp[:, lb].sum(1) + 1e-20))
    lvl = gain * np.where(live, 1.0, 0.0) * np.maximum(vel, 0.0)
    if ex is not None:
        lvl = lvl * ex["gain"]
    lvl = lvl * np.where(cons, 10 ** (12 * (float(p.get("diction", 0.5)) - 0.5) / 20), 1.0)  # +-6 dB consonants
    lvl = np.convolve(lvl, np.ones(4) / 4, mode="same")
    breath = float(p.get("breath", 0.3))
    shimmer = 1 + p.get("shimmer", 0.05) * signal.lfilter([0.3], [1, -0.7], rng.normal(0, 1, nF))
    if mode == "tts":
        y = _tts_voice(p, f0, sp, ap, voiced, lvl * shimmer, f_out, src_w, src_i, total_n, acc_drop=pros * acc)
        if p.get("inhale", 0.15) > 0:
            y += _inhales(p, groups, total_n, rng) * p.get("inhale", 0.15)
        return y
    # ---- noise part: consonant frication + breath, shaped by the word's envelope (WORLD, f0 = 0 -> all noise)
    hi = np.clip((f_out - 1200) / 2500, 0, 1)
    # `whisper` 0-1: an aspiration layer with the full vocal-tract shape (not high-passed like `breath`). On high
    # notes the harmonics are too sparse to draw the formants; breath noise through the same envelope still draws
    # them (whispered speech is intelligible), so the vowels and glides stay readable under the soft tone
    whisper = float(p.get("whisper", 0.25))
    nw = np.where(vs[:, None] > 0.5, np.clip(ap, 0, 1) ** 2 * 0.5 + breath * (0.15 + 0.85 * hi[None, :]) * 0.25
                  + whisper * 0.5, 1.0)
    sp_n = sp * nw * (lvl ** 2)[:, None] + 1e-16
    noise = pw.synthesize(np.zeros(nF), np.ascontiguousarray(sp_n), np.ones_like(sp), SR, FP)
    if mode == "pulse":
        ap_v = np.maximum(ap, breath * 0.25 * hi[None, :])
        f0v = np.where(vs > 0.3, f0, 0.0)
        sp_v = sp * ((lvl * shimmer) ** 2)[:, None] * (vs[:, None] ** 2) + 1e-16
        harm = pw.synthesize(np.ascontiguousarray(f0v), np.ascontiguousarray(sp_v), np.ascontiguousarray(ap_v),
                             SR, FP)
        y = harm[:total_n] + 0.6 * noise[:total_n]
    else:
        y = _additive(p, f0, sp, ap, vs * lvl * shimmer, f_out, total_n) + noise[:total_n] * p.get("air", 0.8)
    y = np.pad(y, (0, max(0, total_n - len(y))))[:total_n]
    if p.get("inhale", 0.25) > 0:
        y += _inhales(p, groups, total_n, rng) * p.get("inhale", 0.25)
    return y


def _micro(w):
    """The spoken word's own small pitch movements (semitones): its f0 minus a 100 ms running median, voiced frames
    only, clipped to +-0.6. Added back (scaled by `micro` and by 1 - `tune`) they keep a little of the human wobble that
    a flat target pitch removes."""
    if "micro" not in w:
        f0 = w["f0"]
        st = np.where(f0 > 0, 12 * np.log2(np.maximum(f0, 1) / 440.0), np.nan)
        med = np.array([np.nanmedian(st[max(0, i - 10):i + 11]) if np.isfinite(st[i]) else 0.0
                        for i in range(len(st))])
        w["micro"] = np.clip(np.nan_to_num(st - med), -0.6, 0.6)
    return w["micro"]


def _tts_voice(p, f0, sp, ap, voiced, amp, f_out, src_w, src_i, total_n, acc_drop=None):
    """`source: "tts"`: WORLD resynthesis of the spoken (TTS) voice itself on the sung pitch: its own spectral envelope
    (formants preserved, or moved by `formant`) and aperiodicity (so consonants and breathiness stay natural), voiced
    where the spoken word was voiced, one level per syllable, plus `breath` noise in the upper bands."""
    import pyworld as pw
    nF = len(f0)
    tune = float(np.clip(p.get("tune", 0.7), 0, 1))
    micro = float(p.get("micro", 0.5)) * (1 - tune)
    dev = np.zeros(nF)
    if micro > 0:
        for f in range(nF):
            w = src_w[f]
            if w is not None:
                dev[f] = _micro(w)[min(int(round(src_i[f])), len(w["f0"]) - 1)]
        if acc_drop is not None:
            dev = dev * (1 - acc_drop)
        dev = np.convolve(dev, np.ones(3) / 3, mode="same") * micro
    f0v = np.where(voiced > 0, f0 * 2 ** (dev / 12), 0.0)
    hi = np.clip((f_out - 1500) / 3000, 0, 1)
    ap_v = np.maximum(ap, float(p.get("breath", 0.15)) * 0.35 * hi[None, :])
    sp_v = sp * (amp ** 2)[:, None] + 1e-16
    y = pw.synthesize(np.ascontiguousarray(f0v), np.ascontiguousarray(sp_v), np.ascontiguousarray(ap_v), SR, FP)
    return np.pad(y, (0, max(0, total_n - len(y))))[:total_n]


TTS_DEFAULTS = {  # `source: "tts"`: sung, not tuned (the first defaults, which read as autotune, are TTS_TUNED)
    "tune": 0.3, "retune_ms": 120, "portamento_ms": 80, "overshoot": 0.08, "scoop": 0.35, "scoop_some": 0.35,
    "vibrato": 0.28, "vib_delay": 0.3, "vib_late": 0.35, "vib_min_s": 0.45, "vib_vary": 0.35, "drift_cents": 6,
    "micro": 0.8, "loose_ms": 12, "jitter": 0.01, "shimmer": 0.02, "breath": 0.15, "inhale": 0.15, "linger": 1.4,
    "coartic_ms": 40, "glide_early": 0.8, "prosody": 0.7, "stretch": "core", "trans_ms": 40,
    "onset_beat": 1.0, "onset_fit": True,
}
TTS_TUNED = {  # the first `tts` defaults (2026-11-24): fast retune, flat held notes; for a deliberately tuned vocal
    "tune": 0.7, "retune_ms": 40, "portamento_ms": 0, "scoop": 0.0, "scoop_some": 1.0, "vibrato": 0.18,
    "vib_delay": 0.25, "vib_late": 0, "vib_min_s": 0, "vib_vary": 0, "drift_cents": 0, "micro": 0.5, "loose_ms": 0,
    "release_ms": 0, "attack_ms": 0, "attack_ms_vowel": 0, "coartic_ms": 30, "keep_joins": False,
    "glide_early": 0, "prosody": 0, "stretch": "linger", "onset_beat": 0, "onset_fit": False,
}


def _additive(p, f0, sp, ap, amp, f_out, total_n):
    """The breathy source: a sum of harmonics whose amplitudes follow the word's envelope at k*f0, with the soft
    spectral tilt of `vox` (`soft` 0-1 = more flute-like) and weaker harmonics where WORLD found noise."""
    nF = len(f0)
    soft = float(p.get("soft", 0.5))
    tilt = 0.6 * soft  # extra roll-off per harmonic on top of the spoken envelope (which has the glottal tilt)
    t_f = np.arange(nF) * HOP
    n = min(total_n, int(nF * HOP))
    ts = np.arange(n)
    f0s = np.interp(ts, t_f, f0)
    ph = 2 * np.pi * np.cumsum(f0s) / SR
    K = int(min(60, 9000 / max(f0.min(), 50)))
    out = np.zeros(n)
    df = f_out[1] - f_out[0]
    rows = np.arange(nF)
    act = amp > 1e-4
    if not act.any():
        return out
    ring = p.get("ring", 0.4)
    for k in range(1, K + 1):
        fk = k * f0
        valid = fk < min(9000, SR / 2 - 500)
        if not valid.any():
            break
        bi = np.clip(fk / df, 0, len(f_out) - 1).astype(int)
        a = np.sqrt(sp[rows, bi]) * np.sqrt(np.clip(1 - ap[rows, bi] ** 2, 0.02, 1)) * k ** -tilt
        a *= 1 + ring * 2.5 * np.exp(-((fk - 2900) / 600) ** 2)
        a = a * amp * valid
        out += np.interp(ts, t_f, a) * np.sin(k * ph)
    return out * 0.5


def _inhales(p, groups, total_n, rng):
    """A short breath in before each phrase that follows a rest of at least 0.4 s."""
    out = np.zeros(total_n)
    prev_end = -1e9
    for g in groups:
        a = g["notes"][0]["t0"]
        if a - prev_end > 0.4 * SR:
            L = int(0.28 * SR)
            s = max(0, a - L - int(0.05 * SR))
            m = min(L, total_n - s)
            if m > 32:
                nz = rng.normal(0, 1, m)
                nz = signal.sosfilt(signal.butter(2, [900, 5500], "bandpass", fs=SR, output="sos"), nz)
                env = np.sin(np.linspace(0, np.pi, m)) ** 2
                out[s:s + m] += nz * env * 0.02
        prev_end = g["notes"][-1]["t0"] + g["notes"][-1]["n"]
    return out


def sing(p, notes, total_n):
    """Render a sung line. notes: list of dict(t0, n, f, vel, glide[, syl]). Returns mono, or stereo (2, N) when
    `double` > 0."""
    p = dict(p)
    if "lyrics" in p and not p.get("_lyrics"):
        p["_lyrics"] = parse_lyrics(p["lyrics"])
    seed = p.get("seed", 1)
    hi = [nt for nt in notes if nt["f"] > 660.0]  # above E5
    if p.get("source") == "tts":
        for k, v in TTS_DEFAULTS.items():
            p.setdefault(k, v)
        if hi:
            _warn(f"{len(hi)} of {len(notes)} sung notes are above E5: the spoken voice is moved up more than an octave "
                  "there and its vowels thin into whistles; keep words at A3-D5")
    elif notes and len(hi) > 0.25 * len(notes):
        _warn(f"{len(hi)} of {len(notes)} sung notes are above E5: up there the harmonics are too far apart to carry "
              "the vowels, so words turn into chirps; sing the line an octave lower (A3-D5 reads best)")
    main = _take(p, notes, total_n, _seed("singer", seed, 0), time_jit_ms=float(p.get("loose_ms", 0)))
    norm = _norm(main)
    dbl = float(p.get("double", 0.0))
    if dbl <= 0:
        return (main * norm).astype(np.float32)
    # a double: another take, a little late or early, its own wobble and a few cents off, panned opposite
    take2 = _take(p, notes, total_n, _seed("singer", seed, 1), time_jit_ms=p.get("double_ms", 12),
                  detune_cents=p.get("double_cents", 7))
    sp_ = float(p.get("double_pan", 0.5))
    a = (sp_ + 1) * np.pi / 4
    b = (-sp_ + 1) * np.pi / 4
    L = main * np.cos(b) + dbl * take2 * np.cos(a)
    R = main * np.sin(b) + dbl * take2 * np.sin(a)
    st = np.stack([L, R]) / (1 + dbl)
    return (st * norm).astype(np.float32)


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
# A from-scratch voice (no eSpeak) for wordless lines and chops. Over `vox` it adds:
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
