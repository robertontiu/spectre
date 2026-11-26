"""Sound descriptors for comparing the engine's dubstep sounds with recorded references (examples/production/
dubstep-v2/README.md). Every sound is trimmed (-50 dB) and peak-normalised to -1 dBFS first, so the numbers describe
the sound, not its level:

  third_db, groups_db       third-octave and six-band shares of the energy (dB re total); groups150_db re the energy
                            above 150 Hz (for bass voices whose lows belong to the sub); tilt_db_oct over 100 Hz-10 kHz
  centroid_*                spectral centroid (median Hz), its movement (std of log2, octaves; p90/p10 range) and the
                            rate of that movement
  flatness, flatness_4k     spectral flatness 100 Hz-8 kHz and 4-16 kHz (noise-likeness), peaks_per_frame
  hnr_db, harmonic_share_db autocorrelation harmonicity (40 ms frames); energy within the harmonics of the yin f0;
  even_odd_db               harmonics 2,4,6,8,10 against 3,5,7,9,11 (distortion character)
  mod_rate_hz, mod_depth_db the dominant level modulation of 300 Hz-6 kHz (the wobble / growl movement), with the
                            nearest note value at the sound's tempo (140 unless its title says otherwise)
  attack_ms, crest_db,      10-90% rise of a 1 ms envelope, peak to RMS, time from each band's peak to -20 dB (low
  decay20_ms, clip_share    <150, mid 150-2.5k, high >2.5k), share of samples within 1 dB of the peak
  side_mid_db               side against mid energy per band (<150, 150-1k, 1-5k, >5k)
  lufs_m_max, lufs_s_max    loudness density: the loudest 400 ms (and 3 s) at a -1 dBFS sample peak
MP3 previews (the references) smear attacks by a few ms and joint stereo can narrow the side a little: the attack
times of the references are not comparable to the engine's and are reported, not used."""
import numpy as np
from scipy import signal

SR = 44100
THIRD = np.array([25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
                  2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000])
GROUPS = [("sub <60", 20, 60), ("low 60-150", 60, 150), ("lowmid 150-500", 150, 500), ("mid 500-2k", 500, 2000),
          ("pres 2-5k", 2000, 5000), ("air 5-16k", 5000, 16000)]
WBANDS = [("<150", 20, 150), ("150-1k", 150, 1000), ("1-5k", 1000, 5000), (">5k", 5000, 18000)]
NOTEVALS = {"1/1": 4, "1/2": 2, "1/4": 1, "1/4t": 2 / 3, "1/8d": 0.75, "1/8": 0.5, "1/8t": 1 / 3, "1/16d": 0.375,
            "1/16": 0.25, "1/16t": 1 / 6, "1/32": 0.125}


def db(x):
    return 10 * np.log10(np.maximum(x, 1e-20))


def trim(x, thr_db=-50):
    m = np.abs(x).max(0)
    if m.max() <= 0:
        return x
    idx = np.where(m > m.max() * 10 ** (thr_db / 20))[0]
    return x[:, idx[0]:idx[-1] + 1]


def norm_peak(x, peak_db=-1.0):
    return x * (10 ** (peak_db / 20) / (np.abs(x).max() + 1e-12))


def band_energy(X2, f, lo, hi):
    return X2[(f >= lo) & (f < hi)].sum()


def note_value(hz, bpm):
    beat = 60.0 / bpm
    best = min(NOTEVALS.items(), key=lambda kv: abs(np.log2((1 / (kv[1] * beat)) / hz)))
    err = 100 * ((1 / (best[1] * beat)) / hz - 1)
    return best[0], round(float(err), 1)


def env_db(x, lo, hi, hop=220):
    y = signal.sosfilt(signal.butter(4, [lo, min(hi, SR * 0.45)], btype="band", fs=SR, output="sos"), x)
    e = np.sqrt(np.convolve(y ** 2, np.ones(hop) / hop, mode="same")[::hop])
    return 20 * np.log10(e + 1e-9), SR / hop


def mod_spectrum_peak(e, fps, lo=0.7, hi=40.0):
    """Dominant modulation rate of a dB envelope (detrended over 1 s), its depth (p90-p10 dB)."""
    if len(e) < fps * 0.6:
        return None, None
    k = max(3, int(fps * 1.0) | 1)
    trend = np.convolve(e, np.ones(k) / k, mode="same") if len(e) > k else np.full(len(e), e.mean())
    d = e - trend
    w = np.hanning(len(d))
    nfft = 1 << int(np.ceil(np.log2(len(d) * 8)))
    S = np.abs(np.fft.rfft(d * w, nfft))
    fr = np.fft.rfftfreq(nfft, 1 / fps)
    sel = (fr >= lo) & (fr <= hi)
    if not sel.any():
        return None, None
    pk = fr[sel][np.argmax(S[sel])]
    return float(pk), float(np.percentile(e, 90) - np.percentile(e, 10))


def describe(x, bpm=140.0, sustained=True):
    """x (2, n) float, any level. Returns a dict of descriptors (level-independent, peak-normalised to -1 dBFS)."""
    import pyloudnorm as pyln
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x])
    x = trim(x)
    x = norm_peak(x)
    if x.shape[1] < 8192:
        x = np.concatenate([x, np.zeros((2, 8192 - x.shape[1]))], axis=1)
    n = x.shape[1]
    m = x.mean(0)
    out = {"dur_s": round(n / SR, 2)}
    # spectrum
    X2 = np.abs(np.fft.rfft(m * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, 1 / SR)
    tot = X2[(f >= 20) & (f < 18000)].sum()
    third = [db(band_energy(X2, f, c * 2 ** (-1 / 6), c * 2 ** (1 / 6)) / tot) for c in THIRD]
    out["third_db"] = [round(float(v), 1) for v in third]
    out["groups_db"] = {g: round(float(db(band_energy(X2, f, lo, hi) / tot)), 1) for g, lo, hi in GROUPS}
    t150 = X2[(f >= 150) & (f < 16000)].sum()
    out["groups150_db"] = {g: round(float(db(band_energy(X2, f, lo, hi) / t150)), 1) for g, lo, hi in GROUPS[2:]}
    sel = (THIRD >= 100) & (THIRD <= 10000)
    out["tilt_db_oct"] = round(float(np.polyfit(np.log2(THIRD[sel]), np.array(third)[sel], 1)[0]), 2)
    # STFT descriptors
    F, T, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - 512)
    P = np.abs(Z) ** 2
    fe = P.sum(0)
    act = fe > fe.max() * 10 ** (-30 / 10)
    band = (F >= 30) & (F <= 16000)
    cen = (F[band, None] * P[band]).sum(0) / (P[band].sum(0) + 1e-20)
    c = cen[act]
    out["centroid_hz"] = round(float(np.median(c)), 0)
    out["centroid_move_oct"] = round(float(np.std(np.log2(c + 1))), 2)
    out["centroid_range_oct"] = round(float(np.log2((np.percentile(c, 90) + 1) / (np.percentile(c, 10) + 1))), 2)
    cr, _ = mod_spectrum_peak(np.log2(cen + 1) * 20, SR / 512) if act.sum() > 40 else (None, None)
    out["centroid_rate_hz"] = None if cr is None else round(cr, 2)
    fl = (F >= 100) & (F <= 8000)
    flat = np.exp(np.mean(np.log(P[fl] + 1e-20), 0)) / (np.mean(P[fl], 0) + 1e-20)
    out["flatness"] = round(float(np.median(flat[act])), 3)
    fh = (F >= 4000) & (F <= 16000)
    flath = np.exp(np.mean(np.log(P[fh] + 1e-20), 0)) / (np.mean(P[fh], 0) + 1e-20)
    out["flatness_4k"] = round(float(np.median(flath[act])), 3)
    # peak density: spectral peaks within 50 dB of the frame max, 50 Hz-8 kHz
    fd = (F >= 50) & (F <= 8000)
    cnt = []
    for j in np.where(act)[0][::4]:
        s = db(P[fd, j])
        pk, _ = signal.find_peaks(s, height=s.max() - 50, prominence=6)
        cnt.append(len(pk))
    out["peaks_per_frame"] = int(np.median(cnt)) if cnt else 0
    # harmonicity (normalised autocorrelation, 40 ms frames) -> HNR proxy
    L = int(0.04 * SR)
    hn = []
    for s0 in range(0, n - L, L):
        fr = m[s0:s0 + L]
        if np.sqrt(np.mean(fr ** 2)) < 10 ** (-40 / 20):
            continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, "full")[L - 1:]
        ac = ac / (ac[0] + 1e-12)
        a0, a1 = int(SR / 500), int(SR / 30)
        r = float(np.clip(ac[a0:a1].max(), 1e-4, 0.9999))
        hn.append(10 * np.log10(r / (1 - r)))
    out["hnr_db"] = round(float(np.median(hn)), 1) if hn else None
    # f0, harmonic share, even/odd
    if sustained and n > SR * 0.2:
        try:
            import librosa
            f0 = librosa.yin(m.astype(np.float32), fmin=30, fmax=800, sr=SR, frame_length=4096)
            f0 = float(np.median(f0))
            out["f0_hz"] = round(f0, 1)
            Xh = X2
            harm = 0.0
            amps = []
            for k in range(1, 400):
                fk = k * f0
                if fk > 8000:
                    break
                hw = min(0.03 * fk, 0.25 * f0)
                e = band_energy(Xh, f, fk - hw, fk + hw)
                harm += e
                if k <= 12:
                    amps.append(e)
            rest = band_energy(Xh, f, f0 * 0.9, 8000)
            out["harmonic_share_db"] = round(float(db(harm / (rest + 1e-20))), 1)
            amps = np.array(amps)
            if len(amps) >= 6:
                out["even_odd_db"] = round(float(db(amps[1::2][:5].sum() / (amps[2::2][:5].sum() + 1e-20))), 1)
        except Exception:
            pass
    # level modulation (wobble / growl movement) in 300 Hz-6 kHz
    e, fps = env_db(m, 300, 6000)
    ea = e[e > e.max() - 40]
    r, d = mod_spectrum_peak(e, fps)
    out["mod_rate_hz"] = None if r is None else round(r, 2)
    out["mod_depth_db"] = None if d is None else round(d, 1)
    if r:
        out["mod_note"] = note_value(r, bpm)
    # transient
    a = np.abs(m)
    env1 = np.sqrt(np.convolve(m ** 2, np.ones(44) / 44, mode="same"))
    pk_i = int(np.argmax(env1))
    pk = env1[pk_i]
    i10 = np.where(env1[:pk_i + 1] >= 0.1 * pk)[0]
    i90 = np.where(env1[:pk_i + 1] >= 0.9 * pk)[0]
    out["attack_ms"] = round(float((i90[0] - i10[0]) / SR * 1000), 1) if len(i10) and len(i90) else None
    seg = m[:min(n, int(0.5 * SR))] if not sustained else m
    out["crest_db"] = round(float(20 * np.log10(np.abs(seg).max() / (np.sqrt(np.mean(seg ** 2)) + 1e-12))), 1)
    dec = {}
    for nm, lo, hi in (("low", 30, 150), ("mid", 150, 2500), ("high", 2500, 16000)):
        y = signal.sosfilt(signal.butter(4, [lo, hi], btype="band", fs=SR, output="sos"), m)
        ev = np.sqrt(np.convolve(y ** 2, np.ones(441) / 441, mode="same"))
        j = int(np.argmax(ev))
        below = np.where(ev[j:] < ev[j] * 0.1)[0]
        dec[nm] = round(float(below[0] / SR * 1000), 0) if len(below) else round((n - j) / SR * 1000, 0)
    out["decay20_ms"] = dec
    out["clip_share"] = round(float(np.mean(a > 10 ** (-2 / 20))), 4)   # samples within 1 dB of the -1 dB peak
    # width per band: side/mid energy (dB)
    S = (x[0] - x[1]) / 2
    W = {}
    for nm, lo, hi in WBANDS:
        sos = signal.butter(4, [max(lo, 20), min(hi, 20000)], btype="band", fs=SR, output="sos")
        mm = signal.sosfilt(sos, m)
        ss = signal.sosfilt(sos, S)
        W[nm] = round(float(db(np.sum(ss ** 2) / (np.sum(mm ** 2) + 1e-20))), 1)
    out["side_mid_db"] = W
    # loudness density at -1 dBFS peak
    meter = pyln.Meter(SR, block_size=0.4)
    xx = x.T
    if n < int(0.45 * SR):
        xx = np.concatenate([xx, np.zeros((int(0.45 * SR) - n, 2))])
    # momentary max (400 ms) and, if long enough, short-term max (3 s)
    hop = int(0.1 * SR)
    mom = []
    for s0 in range(0, max(1, xx.shape[0] - int(0.4 * SR)) + 1, hop):
        blk = xx[s0:s0 + int(0.4 * SR)]
        if len(blk) >= int(0.4 * SR):
            mom.append(meter.integrated_loudness(blk))
    out["lufs_m_max"] = round(float(np.max(mom)), 1) if mom else None
    if xx.shape[0] >= 3 * SR:
        st = []
        for s0 in range(0, xx.shape[0] - 3 * SR + 1, hop):
            st.append(meter.integrated_loudness(xx[s0:s0 + 3 * SR]))
        out["lufs_s_max"] = round(float(np.max(st)), 1)
    return out
