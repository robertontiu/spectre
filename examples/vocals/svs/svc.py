"""A male voice by conversion: Hanami sings the line (timing and diction the catalogue trusts, English and Spanish) and
the phrase is made male. The study behind docs/voice/VOICES.md "Male voices from Hanami" (engine/svs_convert.py).

python3 examples/vocals/svs/svc.py audition [route ...]   # voices/svc-<route>.mp3 and svc-<route>-es.mp3, dry
python3 examples/vocals/svs/svc.py mix [route ...]        # the same lines in the standard band mix (male.py's):
                                                          # voices/svc-<route>-mix.mp3, svc-<route>-es-mix.mp3
                                                          # (default routes: synth arctic blend self, and Hanami)
python3 examples/vocals/svs/svc.py takes [route ...]      # Whisper and pitch over seeds 1-8 (default: synth arctic)
python3 examples/vocals/svs/svc.py refs                   # the same measures on hanami, male-light and male-deep
python3 examples/vocals/svs/svc.py sweep                  # gender x formant ratio of the `synth` route (numbers only)

Routes (every one sings the catalogue line an octave under Hanami's, F#3-B3, and the Spanish line "quiero quedarme
aquí contigo" at E3-B3; the letters are the three kinds of target the owner allowed):
  synth        (c) no target person: Hanami sings at her own register, the synthesizer moves the pitch curve down an
               octave before the acoustic model, with the bank's gender setting at -0.2. The voice `hanami-male`
  world        (c) the DSP classic, for comparison only: Hanami's rendered audio through WORLD analysis, pitch an
               octave down, envelope scaled by 0.85, resynthesis. It pitch-shifts rendered audio, which Lotte V's
               terms name as the wrong way to derive a voice: not wired
  arctic       (a) SoulX-Singer-SVC onto CMU ARCTIC `bdl`, a voice talent recorded for speech synthesis databases
               that are "free for use for any purpose (commercial or otherwise)". The voice `male-svc`
  blend        (b) SoulX-Singer-SVC onto a reference made of four ARCTIC male talents, 2.6 s each (nobody's voice
               alone; whether the model blends them was not measured)
  self         (b) SoulX-Singer-SVC onto a synthetic target: a line sung by `hanami-male` (nobody's voice)
  arctic-low   (a) as arctic, but the source is already sung low in the synthesizer and converted without a shift

Measures: the catalogue's (voices.py / male.py: tilt, breathiness, F1/F2 of "are" by LPC, vibrato, pitch per note,
Whisper small.en, energy above 12 kHz) plus
  formants     F1-F4 of the long "are" (Praat Burg, 5 formants under 5 kHz) and the vocal tract length they imply
               (each formant of a uniform tube, averaged over F1-F4): adult men about 16-18 cm, women about 14-15
  tract_ratio  the envelope scaling that best maps Hanami's own render of the line onto this one (1 = her formants;
               0.85 = all formants 15% lower); only meaningful where the timing is hers
  p_male       a speaker-gender classifier's probability of "male" (ECAPA-TDNN fine-tuned on VoxCeleb2 speech by
               J. Huh, MIT; https://github.com/JaesungHuh/voice-gender-classifier; weights and model.py cached in
               ~/.cache/spectre/refs/gender, never in git). It was trained on speech, so read it as a hint
  timing       the fastest 300-3000 Hz level rise near each note start against the same detector on Hanami's own
               render (ms: mean and sd of the difference), and the lag of the whole level envelope
  artefacts    proxies, not ears: harmonics-to-noise ratio (Praat, dB; a buzzy or noisy conversion is lower),
               level flutter (the 8-40 Hz part of the level inside held notes, dB sd: phasey renders flutter) and
               pitch jitter (median 5 ms frame-to-frame f0 step inside held notes, cents: metallic renders jump)
  render_s     seconds for a new phrase on this machine (2 CPU threads), without the cache
Results: voices/svc.json. Scratch goes to /tmp/spectre_svs/svc (deleted).
"""
import json
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
sys.path.insert(0, HERE)
import male as M  # noqa: E402
import spanish as ES  # noqa: E402
import voices as V  # noqa: E402

SR = 44100
OUT = os.path.join(HERE, "voices")
TMP = "/tmp/spectre_svs/svc"
M.TMP = TMP
ES_LYRICS, ES_MELODY = ES.LINES[1]  # "quiero quedarme aquí contigo", B4 ... E4; sung an octave down
ROUTES = {  # route -> instrument params; a "voice" here is a catalogue id (its Spanish twin is <id>-es), the others
    # ride on hanami / hanami-es with the conversion given on the instrument
    "synth": {"voice": "hanami-male"},
    "arctic": {"voice": "male-svc"},
    "blend": {"svs_convert": {"route": "svc", "sing": 12, "target": "arctic-blend"}},
    "self": {"svs_convert": {"route": "svc", "sing": 12, "target": "hanami-male"}},
    "arctic-low": {"gender": -0.2, "svs_convert": {"route": "svc", "sing": 12, "source_low": True,
                                                   "target": "arctic-bdl"}},
}
WORLD = {"semitones": -12, "ratio": 0.85}  # the `world` route is done here, not in the engine
_G = {}


# ------------------------------------------------------------------------------------------------ lines
def line(lang, transpose=-12):
    """(notes, total samples, lyrics, bpm) of the audition line: English (the catalogue's) or Spanish."""
    if lang == "es":
        from hand import note_to_midi
        q = 60.0 / ES.BPM / 4
        t, out = 0.3, []
        for tok in ES_MELODY.split():
            n, ln = tok.split(":")
            out.append(dict(t0=int(t * SR), n=int(float(ln) * q * 0.95 * SR), vel=0.9, glide=False,
                            f=440 * 2 ** ((note_to_midi(n) + transpose - 69) / 12)))
            t += float(ln) * q
        return out, int((t + 0.8) * SR), ES_LYRICS, ES.BPM
    ns, n = V.notes(transpose)
    return ns, n, V.LINE, 100


def sing(route, lang, transpose=-12):
    """(wave, notes, seconds) of a route's dry line. A fresh render: the phrase cache is bypassed by a scratch dir."""
    import singer
    import svs
    ns, n, lyrics, _ = line(lang, transpose)
    voice = "hanami-es" if lang == "es" else "hanami"
    params = dict(ROUTES.get(route, {}))
    if "voice" in params:
        voice = params.pop("voice") + ("-es" if lang == "es" else "")
    t = time.time()
    if route == "hanami":  # her own render of the line, an octave up: the timing and formant reference
        ns, n, lyrics, _ = line(lang, transpose + 12)
        y = singer.sing({"source": "svs", "voice": voice, "lyrics": lyrics, "seed": 1}, ns, n)
    elif route == "world":
        import svs_convert
        up, n, lyrics, _ = line(lang, transpose + 12)
        y = singer.sing({"source": "svs", "voice": voice, "lyrics": lyrics, "seed": 1}, up, n)
        y = svs_convert.world_shift(y, WORLD["semitones"], WORLD["ratio"])
    elif route in ROUTES:
        keep = svs.PHRASES
        svs.PHRASES = os.path.join(TMP, "phrases")  # time a real render, and leave the user's cache alone
        try:
            y = singer.sing(dict({"source": "svs", "voice": voice, "lyrics": lyrics, "seed": 1}, **params), ns, n)
        finally:
            svs.PHRASES = keep
    else:  # a catalogue voice (male-light, male-deep), from the cache if it is there
        y = singer.sing({"source": "svs", "voice": route, "lyrics": lyrics, "seed": 1}, ns, n)
    return np.asarray(y, dtype=np.float32), ns, time.time() - t


# ------------------------------------------------------------------------------------------------ measures
def praat_formants(y, ns, k=2):
    """F1-F4 (Hz, medians over the middle 300 ms of note k, the long "are") and the vocal tract length they imply."""
    import parselmouth
    nt = ns[k]
    mid = (nt["t0"] + nt["n"] // 2) / SR
    snd = parselmouth.Sound(np.asarray(y, dtype=np.float64), SR)
    fm = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5000)
    out = []
    for i in range(1, 5):
        v = [fm.get_value_at_time(i, t) for t in np.arange(mid - 0.15, mid + 0.15, 0.01)]
        v = [x for x in v if x == x]
        out.append(float(np.median(v)) if v else None)
    vtl = [(2 * i - 1) * 35000 / (4 * f) for i, f in enumerate(out, 1) if f]
    return [round(f) if f else None for f in out], round(float(np.mean(vtl)), 1) if vtl else None


def tract_ratio(y, ref):
    """The frequency scaling r that best maps the reference's spectral envelopes onto this render's (same timing):
    env(f) ~ ref_env(f / r), searched over 0.70-1.15 on voiced frames, 300-5000 Hz."""
    import pyworld as pw
    n = min(len(y), len(ref))
    env = []
    for x in (y[:n], ref[:n]):
        x = np.asarray(x, dtype=np.float64)
        f0, t = pw.harvest(x, SR, f0_floor=60.0, f0_ceil=1100.0, frame_period=10.0)
        env.append((f0, 10 * np.log10(pw.cheaptrick(x, f0, t, SR) + 1e-16)))
    (fa, a), (fb, b) = env
    m = min(len(fa), len(fb))
    v = (fa[:m] > 0) & (fb[:m] > 0)
    fr = np.linspace(0, SR / 2, a.shape[1])
    grid = np.linspace(300, 5000, 200)
    best = (-2.0, 1.0)
    for r in np.arange(0.70, 1.151, 0.01):
        cs = []
        for i in np.where(v)[0][::2]:
            p, q = np.interp(grid, fr, a[i]), np.interp(grid / r, fr, b[i])
            p, q = p - np.polyval(np.polyfit(grid, p, 1), grid), q - np.polyval(np.polyfit(grid, q, 1), grid)
            cs.append(float(np.corrcoef(p, q)[0, 1]))
        c = float(np.mean(cs)) if cs else -2.0
        if c > best[0]:
            best = (c, float(r))
    return round(best[1], 2), round(best[0], 2)


def p_male(y):
    import importlib.util
    import librosa
    import torch
    if "gender" not in _G:
        d = os.path.expanduser("~/.cache/spectre/refs/gender")
        if not os.path.exists(os.path.join(d, "model.safetensors")):
            _G["gender"] = None
        else:
            from safetensors.torch import load_file
            spec = importlib.util.spec_from_file_location("gender_model", os.path.join(d, "model.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            net = mod.ECAPA_gender(C=1024)
            net.load_state_dict(load_file(os.path.join(d, "model.safetensors")))
            _G["gender"] = net.eval()
    if _G["gender"] is None:
        return None
    x = librosa.resample(np.asarray(y, dtype=np.float32), orig_sr=SR, target_sr=16000)
    with torch.no_grad():
        p = torch.softmax(_G["gender"](torch.from_numpy(x)[None, :]), -1)[0, 0]
    return round(float(p), 3)


def rises(y, ns):
    """The fastest rise of the 300-3000 Hz level within 150 ms of each written note start (ms from the start)."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, [300, 3000], btype="band", fs=SR, output="sos")
    env = np.convolve(sosfiltfilt(sos, y.astype(np.float64)) ** 2, np.hanning(882) / 441, "same")
    d = np.gradient(np.convolve(10 * np.log10(env + 1e-10), np.ones(441) / 441, "same"))
    w = int(0.15 * SR)
    return [(max(0, nt["t0"] - w) + int(np.argmax(d[max(0, nt["t0"] - w):nt["t0"] + w])) - nt["t0"]) / 44.1
            for nt in ns]


def note_lags(y, ns, ref, win_ms=(150, 250), max_ms=80):
    """Per note: the lag (ms, positive = later than the reference) at which this render's level onsets around the
    note start line up best with the reference's (cross-correlation of the rectified rise of the broadband level,
    1 ms steps, searched over +-80 ms)."""
    def onset(x):
        lev = 10 * np.log10(np.convolve(np.asarray(x, dtype=np.float64) ** 2, np.ones(441) / 441, "same")[::44] + 1e-9)
        lev = np.maximum(lev, lev.max() - 50)
        return np.maximum(np.gradient(np.convolve(lev, np.hanning(15) / 7.0, "same")), 0)
    oa, ob = onset(y), onset(ref)
    out = []
    for nt in ns:
        c = int(nt["t0"] / 44)
        a, b = max(0, c - win_ms[0]), min(len(oa), len(ob), c + win_ms[1])
        p, q = oa[a:b], ob[a:b]
        best = (-1.0, 0)
        for k in range(-max_ms, max_ms + 1):
            pp, qq = p[max(0, k):len(p) + min(0, k)], q[max(0, -k):len(q) + min(0, -k)]
            v = float(np.dot(pp, qq) / (np.linalg.norm(pp) * np.linalg.norm(qq) + 1e-12))
            if v > best[0]:
                best = (v, k)
        out.append(best[1] * 44 / 44.1)
    return out


def timing(y, ns, ref):
    """Against Hanami's own render of the line: per-note onset lag (note_lags; ms, mean and sd), the lag of the
    whole level envelope (positive = later than her), and the older rise detector's difference for comparison (it
    reads a 300-3000 Hz band, so an octave change alone moves it: the `synth` route has her timing by construction
    and still shows about 25 ms sd there)."""
    lg = np.array(note_lags(y, ns, ref))
    a, b = rises(y, ns), rises(ref, ns)
    d = np.array(a) - np.array(b)
    ea, eb = (np.convolve(np.abs(x[:min(len(y), len(ref))]).astype(np.float64), np.ones(441) / 441, "same")[::44]
              for x in (y, ref))
    ea, eb = ea - ea.mean(), eb - eb.mean()
    lags = np.arange(-150, 151)
    cc = [float(np.dot(ea[max(0, k):len(ea) + min(0, k)], eb[max(0, -k):len(eb) + min(0, -k)])) for k in lags]
    return dict(note_lag_ms=[round(float(x)) for x in lg], lag_mean_ms=round(float(lg.mean()), 1),
                lag_sd_ms=round(float(lg.std()), 1), rise_detector_diff_ms=[round(float(x)) for x in d],
                rise_detector_sd_ms=round(float(d.std()), 1), envelope_lag_ms=round(float(lags[int(np.argmax(cc))] * 44 / 44.1), 1))


def artefacts(y, ns):
    import parselmouth
    import pyworld as pw
    from scipy.signal import butter, sosfiltfilt
    x = np.asarray(y, dtype=np.float64)
    h = parselmouth.Sound(x, SR).to_harmonicity_cc(time_step=0.01, minimum_pitch=75.0)
    hv = h.values[h.values > -100]
    f0, _ = pw.harvest(x, SR, f0_floor=60, f0_ceil=1100, frame_period=5.0)
    lev = 10 * np.log10(np.convolve(x ** 2, np.ones(441) / 441, "same")[::220] + 1e-12)  # 200 frames a second
    sos = butter(2, [8, 40], btype="band", fs=200, output="sos")
    fl, jit = [], []
    for nt in ns:
        if nt["n"] < 0.3 * SR:
            continue
        a, b = int((nt["t0"] + 0.3 * nt["n"]) / SR * 200), int((nt["t0"] + 0.9 * nt["n"]) / SR * 200)
        if b - a > 30:
            fl.append(float(np.std(sosfiltfilt(sos, lev[a:b]))))
        v = f0[a:b]
        if (v > 0).sum() > 10 and (v > 0).all():
            jit.append(float(np.median(np.abs(np.diff(1200 * np.log2(v))))))
    return dict(hnr_db=round(float(np.mean(hv)), 1) if len(hv) else None,
                flutter_db=round(float(np.mean(fl)), 2) if fl else None,
                jitter_cents=round(float(np.mean(jit)), 2) if jit else None)


def measure(y, ns, lang, ref=None, ref_same_timing=True):
    if lang == "es":
        m = V.measure(y, ns)
        pc = M.pitch_cents(y, ns)
        text, det, prob = ES.whisper(y)
        m.update(pitch_cents=pc, pitch_mean_abs_cents=round(float(np.mean([abs(p) for p in pc if p is not None])), 1),
                 whisper=text, whisper_words=round(float(ES.word_accuracy(ES_LYRICS, text)), 2),
                 whisper_detected=f"{det} {prob:.2f}", above_12k_db=M.above_12k_db(y))
        for k in ("F1", "F2"):  # the LPC pair is taken on note 3, which is the long "are" only in the English line
            m.pop(k, None)
    else:
        m = M.measure(y, ns)
        f, vtl = praat_formants(y, ns)
        m.update(formants_are=f, tract_cm=vtl)
    m.update(artefacts(y, ns), p_male=p_male(y))
    if ref is not None:
        m.update(timing=timing(y, ns, ref))
        if ref_same_timing:
            m["tract_ratio"], m["tract_ratio_corr"] = tract_ratio(y, ref)
    return m


def save(res):
    path = os.path.join(OUT, "svc.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, "w"), indent=1, ensure_ascii=False)


def _routes(args):
    return args or ["synth", "world", "arctic", "blend", "self", "arctic-low"]


# ------------------------------------------------------------------------------------------------ commands
def audition(args):
    res = {}
    shutil.rmtree(TMP, ignore_errors=True)
    for lang in ("en", "es"):
        ref, _, _ = sing("hanami", lang)
        for r in _routes(args):
            y, ns, sec = sing(r, lang)
            key = f"svc-{r}" + ("-es" if lang == "es" else "")
            res[key] = dict(measure(y, ns, lang, ref), render_s=round(sec),
                            what=f"route {r}, {'Spanish line, E3-B3' if lang == 'es' else 'the catalogue line, F#3-B3'}, dry")
            M.mp3(y, os.path.join(OUT, key + ".mp3"))
            print(key, json.dumps(res[key], ensure_ascii=False))
            save(res)


def refs(args):
    res = {}
    for lang in ("en", "es"):
        ref, ns_up, _ = sing("hanami", lang)
        ns_up = line(lang, 0)[0]
        key = "ref-hanami" + ("-es" if lang == "es" else "")
        res[key] = dict(measure(ref, ns_up, lang), what="Hanami's own render of the line, an octave above the routes")
        print(key, json.dumps(res[key], ensure_ascii=False))
    for vid in args or ["male-light", "male-deep"]:  # English only; other timing, so no timing or tract ratio
        y, ns, _ = sing(vid, "en")
        res[f"ref-{vid}"] = dict(measure(y, ns, "en"), what=f"{vid} (SoulX-Singer, VocalSet prompt), the same line")
        print(vid, json.dumps(res[f"ref-{vid}"]))
    save(res)


def sweep(args):
    """The `synth` route over gender and formant ratio: numbers only (Whisper, tract, p_male, tilt)."""
    import singer
    ns, n, lyrics, _ = line("en")
    ref, _, _ = sing("hanami", "en")
    res = {}
    for g in (0.0, -0.2, -0.3, -0.4):
        for fr in (1.0, 0.92, 0.88, 0.84, 0.80):
            p = {"source": "svs", "voice": "hanami", "lyrics": lyrics, "seed": 1, "gender": g,
                 "svs_convert": {"route": "synth", "sing": 12, "formant": fr}}
            y = np.asarray(singer.sing(p, ns, n), dtype=np.float32)
            text, acc = M.whisper(y)
            f, vtl = praat_formants(y, ns)
            tr, _ = tract_ratio(y, ref)
            m = V.measure(y, ns)
            res[f"sweep-g{g}-f{fr}"] = dict(whisper=text, whisper_words=round(acc, 2), formants_are=f, tract_cm=vtl,
                                             tract_ratio=tr, p_male=p_male(y), tilt_db=m["tilt_db"],
                                             breathiness=m["breathiness"], **artefacts(y, ns))
            print(g, fr, json.dumps(res[f"sweep-g{g}-f{fr}"]))
    save(res)


def takes(args):
    """How often a take reads: the English line with seeds 1-8 (another seed is another performance of the source
    and another draw of the converter), Whisper words and pitch per take. `hanami` is her own line an octave up."""
    import singer
    res = {}
    for r in args or ["synth", "arctic", "hanami"]:
        params = dict(ROUTES.get(r, {}))
        voice = params.pop("voice", "hanami")
        ns, n, lyrics, _ = line("en", 0 if r == "hanami" else -12)
        rows = []
        for seed in range(1, 9):
            y = np.asarray(singer.sing(dict({"source": "svs", "voice": voice, "lyrics": lyrics, "seed": seed},
                                            **params), ns, n), dtype=np.float32)
            text, acc = M.whisper(y)
            pc = M.pitch_cents(y, ns)
            rows.append(dict(seed=seed, whisper=text, words=round(acc, 2),
                             pitch_mean_abs_cents=round(float(np.mean([abs(p) for p in pc if p is not None])), 1)))
            print(r, json.dumps(rows[-1]))
        res[f"takes-{r}"] = dict(takes=rows, all_words=sum(x["words"] == 1.0 for x in rows), of=len(rows),
                                 what=f"route {r}: the catalogue line over seeds 1-8, dry")
        save(res)


def project(lang, extra, gain_db, mute=False, transpose=-12):
    """male.py's four-bar band (a bar of band, the two-bar line over electric piano, bass and drums, a bar of tail)
    with the vocal chain of docs/voice/MIXING.md section 2; the Spanish line gets its own tempo and chords."""
    extra = dict(extra)
    voice = extra.pop("voice", "hanami") + ("-es" if lang == "es" else "")
    pj = M.project(voice, transpose, gain_db, mute)
    pj["tracks"]["vox"]["inst"].update(extra)
    if lang == "es":
        import librosa
        from hand import note_to_midi
        steps, t = [], 0
        for tok in ES_MELODY.split():
            n, ln = tok.split(":")
            steps.append(f"{t}:{librosa.midi_to_note(note_to_midi(n) + transpose, unicode=False)}:{ln}")
            t += int(ln)
        pj["bpm"] = ES.BPM
        pj["patterns"]["band"] = {"bars": 2, "keys": {"chords": "Em7:16 Cmaj7:8 D:8", "style": "sustain",
                                                      "register": "A3", "vel": 0.6},
                                  "bass": "0:E2:6 6:E2:2 8:B1:8 16:C2:6 22:C2:2 24:D2:8"}
        pj["patterns"]["tail"] = {"bars": 1, "keys": {"chords": "Em7:16", "style": "sustain", "register": "A3",
                                                      "vel": 0.5}, "bass": "0:E2:12"}
        pj["patterns"]["line"] = {"bars": 2, "vox": {"notes": " ".join(steps), "lyrics": ES_LYRICS}}
    return pj


def mix_check(lang, extra, name, transpose=-12):
    """male.mix_check for any instrument params: the vocal set about 1 LU under the band, Whisper on the hook bars of
    the quick master and on the vocal alone (premaster minus the vocal-muted render)."""
    bpm = ES.BPM if lang == "es" else 100
    bar = int(4 * 60 / bpm * SR)
    a, b = bar - SR // 2, 3 * bar + SR // 2
    gain = 0.0
    for _ in range(4):
        full, quick = M.render(project(lang, extra, gain, transpose=transpose), f"{name}-full")
        band, _ = M.render(project(lang, extra, gain, mute=True, transpose=transpose), f"{name}-band")
        n = min(full.shape[1], band.shape[1])
        vocal = full[:, :n] - band[:, :n]
        lu = M.lufs(vocal[:, bar:3 * bar]) - M.lufs(band[:, bar:3 * bar])
        if abs(lu + 1.0) < 0.5:
            break
        gain += -1.0 - lu

    def words(x):
        if lang == "es":
            text, _, _ = ES.whisper(x)
            return text, float(ES.word_accuracy(ES_LYRICS, text))
        return M.whisper(x)
    text, acc = words(quick[:, a:b].mean(0))
    stext, sacc = words(vocal[:, a:b].mean(0))
    return dict(vocal_vs_band_lu=round(lu, 1), vocal_gain_db=round(gain, 1), whisper_mix=text,
                whisper_mix_words=round(acc, 2), whisper_stem=stext, whisper_stem_words=round(sacc, 2)), quick


def mix(args):
    res = {}
    for lang in os.environ.get("SVC_LANGS", "en,es").split(","):  # SVC_LANGS=es: one language only
        for r in [x for x in (args or ["synth", "arctic", "blend", "self"]) if x != "world"] + (
                ["hanami"] if not args else []):
            extra = ROUTES.get(r, {})
            name = f"svc-{r}" + ("-es" if lang == "es" else "")
            if r == "hanami":  # the reference: her own line an octave up in the same band, levelled the same way
                m, _ = mix_check(lang, {}, name, transpose=0)
                res[f"ref-hanami{'-es' if lang == 'es' else ''}-mix"] = dict(
                    m, what="Hanami an octave above the routes in the same band and chain")
                print("ref", lang, json.dumps(m, ensure_ascii=False))
                continue
            m, quick = mix_check(lang, extra, name)
            res[name + "-mix"] = dict(m, what="the line in a small band (ep, bass, drums) through the standing vocal "
                                              "chain, quick master")
            M.mp3(quick, os.path.join(OUT, name + "-mix.mp3"))
            print(name + "-mix", json.dumps(res[name + "-mix"], ensure_ascii=False))
            save(res)
    save(res)


if __name__ == "__main__":
    try:
        open("/proc/self/oom_score_adj", "w").write("1000")
    except OSError:
        pass
    cmd, rest = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("audition", [])
    {"audition": audition, "mix": mix, "refs": refs, "sweep": sweep, "takes": takes}[cmd](rest)
    shutil.rmtree(TMP, ignore_errors=True)
