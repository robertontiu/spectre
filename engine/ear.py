"""The ears: turn a render into pictures and numbers a producer can judge.

Overview (default): arrangement lanes (which track plays where, how loud), mel spectrogram
with section labels, band-energy lanes, loudness curve, per-section stats and warnings.
Zoom (--bars / --section): hi-res spectrogram, onset curve on the beat grid, and a timing
roll showing where each hit really landed against the grid (the hand's humanization).
"""
import os, json, glob
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyloudnorm as pyln

SR = 44100
BANDS = [("sub 20-60", 20, 60), ("low 60-250", 60, 250), ("lowmid 250-2k", 250, 2000),
         ("high 2k-8k", 2000, 8000), ("air 8k+", 8000, 20000)]
KS_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PCN = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
OUT = os.environ.get("BEAT_DIR", os.getcwd())


def stft_mag(x, nfft=4096, hop=1024):
    import librosa
    return np.abs(librosa.stft(x, n_fft=nfft, hop_length=hop)), librosa.fft_frequencies(sr=SR, n_fft=nfft)


def band_energy(S, freqs):
    out = []
    for _, lo, hi in BANDS:
        m = (freqs >= lo) & (freqs < hi)
        out.append(10 * np.log10((S[m] ** 2).sum(0) + 1e-9))
    return np.array(out)


def key_estimate(y):
    import librosa
    ch = librosa.feature.chroma_stft(y=y[::2], sr=SR // 2, hop_length=2048).mean(1)
    best = None
    for r in range(12):
        for prof, q in ((KS_MAJ, "major"), (KS_MIN, "minor")):
            c = np.corrcoef(np.roll(prof, r), ch)[0, 1]
            if best is None or c > best[0]:
                best = (c, f"{PCN[r]} {q}")
    return best[1], round(float(best[0]), 2)


def section_stats(st, sections, meter):
    import librosa
    rows = []
    mono = st.mean(0)
    for s in sections:
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        seg = st[:, a:b]
        m = mono[a:b]
        if len(m) < SR // 2:
            continue
        try:
            L = meter.integrated_loudness(seg.T)
        except Exception:
            L = float("nan")
        S, fr = stft_mag(m, 2048, 1024)
        cent = float((S * fr[:, None]).sum() / (S.sum() + 1e-9))
        be = band_energy(S, fr).mean(1)
        onsets = librosa.onset.onset_detect(y=m, sr=SR, units="time")
        mid = (seg[0] + seg[1]) / 2
        side = (seg[0] - seg[1]) / 2
        width = float(np.sqrt((side ** 2).mean() / ((mid ** 2).mean() + 1e-12)))
        rows.append(dict(name=s["name"], bars=f"{s['bar0']}-{s['bar0'] + s['bars'] - 1}", lufs=round(L, 1),
                         centroid=int(cent), onsets_per_s=round(len(onsets) / (len(m) / SR), 1),
                         width=round(width, 2), bands=[round(float(v), 1) for v in be]))
    return rows


def lanes(ax, meta, t0=None, t1=None):
    st = meta["stems_rms"]
    hop = meta["rms_hop"]
    names = list(st)
    for i, n in enumerate(names):
        e = np.array(st[n])
        if len(e) == 0:
            continue
        t = np.arange(len(e)) * hop
        d = 20 * np.log10(e + 1e-6)
        lvl = np.clip((d + 60) / 50, 0, 1)
        ax.fill_between(t, i - lvl * 0.45, i + lvl * 0.45, step="mid", color=plt.cm.tab10(i % 10), lw=0)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=7)
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_title("arrangement lanes (thickness = level)", fontsize=8, loc="left")


def mark_sections(ax, sections, label=True, t0=0, t1=None):
    for s in sections:
        if t1 is not None and (s["end"] < t0 or s["start"] > t1):
            continue
        ax.axvline(s["start"], color="w" if label == "w" else "k", lw=0.6, alpha=0.6)
        if label:
            ax.text(max(s["start"], t0) + 0.3, ax.get_ylim()[1], s["name"], fontsize=7, va="top",
                    color="w" if label == "w" else "k", alpha=0.9)


def listen(a, renders):
    import librosa
    import librosa.display
    latest = a.wav or json.load(open(os.path.join(renders, "latest.json")))["wav"]
    mp = latest.replace(".wav", ".meta.json")
    if not os.path.exists(mp):  # e.g. vNNN.master.wav: use the render's own meta
        mp = latest.replace(".master.wav", ".meta.json").replace(".premaster.wav", ".meta.json")
    meta = json.load(open(mp))
    if getattr(a, "clarity", False):  # stems: re-rendered from the render's project file (no audio file needed)
        import clarity
        return clarity.run(a, renders, latest, meta)
    y, sr = sf.read(latest, always_2d=True)
    if getattr(a, "phone", False):
        return phone_listen(a, latest, meta, y)
    st = y.T.astype(np.float32)
    if a.mono:
        st = np.stack([st.mean(0)] * 2)
    if a.lowpass:
        import pedalboard as pb
        st = pb.Pedalboard([pb.LowpassFilter(800)])(st, SR)
    sections = meta["sections"]
    beat = 60 / meta["bpm"]
    bar = beat * 4
    t0, t1 = 0.0, meta["duration"]
    zoom = False
    if a.section:
        s = next((s for s in sections if s["name"] == a.section), None)
        if not s:
            raise SystemExit(f"no section '{a.section}'. Have: {[s['name'] for s in sections]}")
        t0, t1, zoom = s["start"], s["end"], True
    if a.bars:
        b0, b1 = [int(v) for v in a.bars.split("-")]
        t0, t1, zoom = (b0 - 1) * bar, b1 * bar, True
        if meta.get("grid16"):  # tempo-mapped render: bars start where the tempo map puts them
            g = meta["grid16"]
            t0, t1 = g[min((b0 - 1) * 16, len(g) - 1)], g[min(b1 * 16, len(g) - 1)]
    meter = pyln.Meter(SR)
    mono = st.mean(0)
    tag = ("_mono" if a.mono else "") + ("_lowpass" if a.lowpass else "")
    if not zoom:
        fig, axs = plt.subplots(4, 1, figsize=(15, 13), gridspec_kw=dict(height_ratios=[1.3, 2.2, 1.2, 0.8]))
        lanes(axs[0], meta)
        axs[0].set_xlim(0, meta["duration"])
        mark_sections(axs[0], sections)
        M = librosa.feature.melspectrogram(y=mono, sr=SR, n_fft=4096, hop_length=2048, n_mels=128, fmax=16000)
        librosa.display.specshow(librosa.power_to_db(M, ref=np.max), sr=SR, hop_length=2048, x_axis="time", y_axis="mel",
                                 fmax=16000, ax=axs[1], cmap="magma")
        axs[1].set_title("mel spectrogram (whole beat)", fontsize=8, loc="left")
        mark_sections(axs[1], sections, label="w")
        S, fr = stft_mag(mono, 4096, 2048)
        be = band_energy(S, fr)
        tt = np.arange(be.shape[1]) * 2048 / SR
        for i, (nm, _, _) in enumerate(BANDS):
            axs[2].plot(tt, be[i], lw=0.8, label=nm)
        axs[2].legend(fontsize=7, ncol=5, loc="lower left")
        axs[2].set_xlim(0, meta["duration"])
        axs[2].set_title("band energy (dB)", fontsize=8, loc="left")
        mark_sections(axs[2], sections, label=False)
        w = int(0.4 * SR)
        # the 400 ms moving average at the plotted points only, from a cumulative sum (speed pass 2026-11-26: the
        # direct np.convolve with a 17,640-sample window took minutes on a long track; same values to float rounding)
        c = np.concatenate([[0.0], np.cumsum(np.asarray(mono, dtype=np.float64) ** 2)])
        i = np.arange(0, len(mono), 4410)
        hi = np.minimum(i + (w - 1) // 2, len(mono) - 1)
        lo = np.maximum(i + (w - 1) // 2 - w + 1, 0)
        r = np.sqrt(np.maximum((c[hi + 1] - c[lo]) / w, 0.0))
        axs[3].plot(np.arange(len(r)) * 0.1, 20 * np.log10(r + 1e-6), lw=0.8, color="k")
        axs[3].set_xlim(0, meta["duration"])
        axs[3].set_ylim(-45, 0)
        axs[3].set_title("loudness (RMS dB, 400 ms)", fontsize=8, loc="left")
        mark_sections(axs[3], sections, label=False)
        for ax in axs:
            ax.tick_params(labelsize=7)
        fig.tight_layout()
        path = os.path.join(OUT, f"ear{tag}.png")
        fig.savefig(path, dpi=80)
        plt.close(fig)
        L = meter.integrated_loudness(st.T)
        peak = 20 * np.log10(np.abs(st).max() + 1e-9)
        key, kc = key_estimate(mono)
        tempo, _ = librosa.beat.beat_track(y=mono[::2], sr=SR // 2)
        mid = (st[0] + st[1]) / 2
        side = (st[0] - st[1]) / 2
        corr = float(np.corrcoef(st[0], st[1])[0, 1])
        m, s_ = divmod(meta["duration"], 60)
        print(f"EAR: {os.path.basename(latest)}  length {int(m)}:{s_:04.1f}  integrated {L:.1f} LUFS  peak {peak:.1f} dBFS  "
              f"L/R corr {corr:.2f}  key~{key} (conf {kc})  tempo~{float(np.atleast_1d(tempo)[0]):.0f} (project {meta['bpm']})")
        rows = section_stats(st, sections, meter)
        print("section        bars     LUFS  centroid  onsets/s  width   bands[sub,low,lowmid,high,air] dB")
        prev = None
        warns = []
        for rw in rows:
            print(f"{rw['name'][:13]:13s}  {rw['bars']:7s} {rw['lufs']:6.1f}  {rw['centroid']:7d}  {rw['onsets_per_s']:7.1f}  "
                  f"{rw['width']:5.2f}   {rw['bands']}")
            if prev is not None:
                diff = np.abs(np.array(rw["bands"]) - np.array(prev["bands"])).mean()
                if diff < 0.8 and abs(rw["lufs"] - prev["lufs"]) < 0.8 and abs(rw["onsets_per_s"] - prev["onsets_per_s"]) < 0.5:
                    warns.append(f"'{rw['name']}' sounds almost identical to '{prev['name']}' (no contrast)")
            prev = rw
            if rw["bands"][0] - rw["bands"][2] > 8:
                warns.append(f"'{rw['name']}': sub is very dominant vs mids (+{rw['bands'][0] - rw['bands'][2]:.0f} dB)")
        if peak > -0.3:
            warns.append("peaks near 0 dBFS: limiter working hard")
        if corr < 0.2:
            warns.append("low L/R correlation: mono compatibility risk")
        for w_ in warns:
            print("WARN:", w_)
        print(f"image: {path}")
        return
    # ---------------- zoom
    a_, b_ = int(t0 * SR), int(min(t1, len(mono) / SR) * SR)
    seg = mono[a_:b_]
    fig, axs = plt.subplots(3, 1, figsize=(15, 11), gridspec_kw=dict(height_ratios=[2.2, 0.9, 2.0]))
    M = librosa.feature.melspectrogram(y=seg, sr=SR, n_fft=2048, hop_length=256, n_mels=160, fmax=16000)
    librosa.display.specshow(librosa.power_to_db(M, ref=np.max), sr=SR, hop_length=256, x_axis="time", y_axis="mel",
                             fmax=16000, ax=axs[0], cmap="magma")
    if meta.get("grid16"):  # tempo-mapped: bar numbers from the real grid
        g16 = np.asarray(meta["grid16"])
        bar_lbl = f"{int(np.argmin(np.abs(g16 - t0))) // 16 + 1}-{int(np.argmin(np.abs(g16 - t1))) // 16}"
    else:
        bar_lbl = f"{int(t0 / bar) + 1}-{int(round(t1 / bar))}"
    axs[0].set_title(f"mel spectrogram {t0:.1f}-{t1:.1f}s (bars {bar_lbl})", fontsize=8, loc="left")
    on = librosa.onset.onset_strength(y=seg, sr=SR, hop_length=256)
    tt = np.arange(len(on)) * 256 / SR
    axs[1].plot(tt, on, lw=0.7, color="k")
    for k, x in _grid(meta, t0, t1, beat):
        axs[1].axvline(x, color="r" if k % 16 == 0 else "b" if k % 4 == 0 else "0.8", lw=1.2 if k % 16 == 0 else 0.6 if k % 4 == 0 else 0.3)
    axs[1].set_xlim(0, t1 - t0)
    axs[1].set_title("onset strength over the grid (red = bar, blue = beat, grey = 16th)", fontsize=8, loc="left")
    ev = meta["events"]
    names = [n for n in ev if any(t0 <= e["t"] < t1 for e in ev[n])]
    for i, n in enumerate(names):
        es = [e for e in ev[n] if t0 <= e["t"] < t1]
        xs = [e["t"] - t0 for e in es]
        if es and es[0].get("m") is not None:
            ms = np.array([e["m"] for e in es])
            yy = i + 0.8 * (ms - ms.min()) / max(ms.max() - ms.min(), 1) - 0.4
        else:
            yy = np.full(len(es), i)
        axs[2].scatter(xs, yy, s=[10 + 60 * e["v"] for e in es], color=plt.cm.tab10(i % 10), alpha=0.8)
    for k, x in _grid(meta, t0, t1, beat):
        axs[2].axvline(x, color="r" if k % 16 == 0 else "b" if k % 4 == 0 else "0.85", lw=1 if k % 16 == 0 else 0.5 if k % 4 == 0 else 0.3, zorder=0)
    axs[2].set_yticks(range(len(names)))
    axs[2].set_yticklabels(names, fontsize=7)
    axs[2].set_xlim(0, t1 - t0)
    axs[2].set_title("timing roll: every event the hand played (dot size = velocity; pitched tracks drawn by pitch)", fontsize=8, loc="left")
    for ax in axs:
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    path = os.path.join(OUT, f"ear_zoom{tag}.png")
    fig.savefig(path, dpi=80)
    plt.close(fig)
    L = meter.integrated_loudness(st[:, a_:b_].T) if b_ - a_ > SR else float("nan")
    print(f"ZOOM {t0:.1f}-{t1:.1f}s  LUFS {L:.1f}")
    for n in names:
        es = [e for e in ev[n] if t0 <= e["t"] < t1]
        offs = []
        for e in es:
            if meta.get("grid16"):  # tempo-mapped: nearest 16th of the real grid
                gg = np.asarray(meta["grid16"])
                g = gg[np.argmin(np.abs(gg - e["t"]))]
            else:
                g = round(e["t"] / (beat / 4)) * (beat / 4)
            offs.append((e["t"] - g) * 1000)
        vs = [e["v"] for e in es]
        print(f"  {n:10s} {len(es):4d} events  timing vs 16th grid: mean {np.mean(offs):+5.1f} ms, spread {np.std(offs):4.1f} ms  "
              f"velocity {min(vs):.2f}-{max(vs):.2f}")
    print(f"image: {path}")


def _grid(meta, t0, t1, beat):
    """(index, x) of the 16th-grid lines in a zoom window; follows the tempo map of a tempo-mapped render."""
    if meta.get("grid16"):
        return [(k, g - t0) for k, g in enumerate(meta["grid16"]) if t0 - 1e-6 <= g <= t1 + 1e-6]
    return [(k, k * beat / 4) for k in range(int((t1 - t0) / (beat / 4)) + 1)]


def phone_listen(a, path, meta, y):
    """`listen --phone`: how the track's top end reads on a phone speaker (master.phone_check)."""
    import master as M
    genre = a.genre or "hiphop"
    target = M.load_genres()[genre]["master"]["target"] if genre in M.load_genres() else genre
    sections = meta["sections"]
    x = y.T.astype(np.float64)
    if a.section or a.bars:
        beat = 60 / meta["bpm"]
        if a.section:
            s = next((s for s in sections if s["name"] == a.section), None)
            if not s:
                raise SystemExit(f"no section '{a.section}'. Have: {[s['name'] for s in sections]}")
            t0, t1 = s["start"], s["end"]
        else:
            b0, b1 = [int(v) for v in a.bars.split("-")]
            t0, t1 = (b0 - 1) * beat * 4, b1 * beat * 4
            if meta.get("grid16"):
                g = meta["grid16"]
                t0, t1 = g[min((b0 - 1) * 16, len(g) - 1)], g[min(b1 * 16, len(g) - 1)]
        x = x[:, int(t0 * SR):int(t1 * SR)]
        sections = [dict(s, start=max(s["start"], t0) - t0, end=min(s["end"], t1) - t0) for s in sections
                    if s["end"] > t0 and s["start"] < t1]
    r = M.phone_check(x, target, sections)
    ww = r["worst_window"]
    print(f"PHONE: {os.path.basename(path)}  speaker model: {r['model']}  target: {target} (genre {genre})")
    print(f"  6-12 kHz vs 1-2.8 kHz {r['air_6_12k_vs_mid_db']} dB = {r['air_excess_db']:+} dB vs the target   "
          f"5-16 kHz {r['top_excess_db']:+} dB vs the target   flatness 4-16 kHz {r['flatness_4_16k']} (1 = white noise)   "
          f"noise-likeness 4-16 kHz {r['noise_likeness_4_16k']} (slope removed; 1 = noise, 0 = tones)")
    print(f"  worst 3 s at {ww['start_s']} s: 6-12 kHz {ww['air_excess_db']:+} dB vs the target, flatness {ww['flatness_4_16k']}")
    print("  section        level  6-12k vs target  flatness")
    for s in r.get("sections", []):
        flag = "  <- hissy" if (s["air_excess_db"] > 3 and s["flatness_4_16k"] > 0.2) else (
            "  <- bright" if s["air_excess_db"] > 3 else "")
        print(f"  {s['name'][:13]:13s} {s['level_db']:6.1f}  {s['air_excess_db']:+10.1f}       {s['flatness_4_16k']:5.2f}{flag}")
    for n in r["notes"]:
        print("PHONE NOTE:", n)
