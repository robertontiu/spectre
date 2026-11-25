"""Ears for stems: `studio.py listen --clarity` (docs/PRODUCTION.md section 2, "A clarity analysis for listen").

The engine renders every track separately before summing, so the stems are free: a section is re-rendered in memory
(a window render, `studio.render(..., window=...)`, with two bars of pre-roll) and every track, plus the reverb,
delay and transition-fx returns, is caught as it goes into the mix. Each stem's mid signal is cut into 93 ms Hann
frames (hop 46 ms) and summed into the 28 third-octave bands of engine/master.py (31.5 Hz-16 kHz). From those
time-frequency cells:

  census      per region (sub 20-60, bass 60-150, low-mid 150-400, mid 400-2k, presence 2-6k, air 6-18k Hz): the
              region's share of the section's energy and the stems within 10 dB of the loudest stem there
  occupancy   per region: the number of stems within 6 dB of the loudest stem in a cell, averaged over the cells
              weighted by their energy (about 1 = one sound at a time, 2-3 a blend, more a wash)
  masked      per stem: the share of its A-weighted energy in cells where all other stems together are at least
              6 dB above it, and the stem that contributes most to that masking; `own` is the share in cells where
              it is the loudest stem. A simplified, time-resolved masker-to-signal ratio: no spreading function or
              tonality term, so it under-reads upward masking; the 6 dB margin and the A-weighting are hand-tuned.
              Read with Aichinger et al. (AES 2011): a stem over about 90% masked is, in practice, not in the mix.
  build-up    the section mix's 100-250 Hz (and 315-400 Hz) level against the genre's target curve, with the curve
              laid over the mix at its level around 1 kHz (as the master does)
  crest       per region, peak over RMS of the mix's 10 ms band envelope: transient definition per band
  EQ map      per stem with a role (a track's "role", else inferred from its name and instrument, marked *): its
              energy under the map's high-pass point (and over its low-pass), and its level per third octave in the
              regions the map says to cut against the region the role owns, relative to the same balance in the
              genre's target curve (0 = balanced like the genre's average record; engine/eqmaps.json)
  flags       core roles empty in a peak section, regions with a single source in a peak section, stems over 90%
              masked, more than four sources within 10 dB at 150-400 Hz, low-mid build-up over +3 dB, EQ map
              deviations. Thresholds are hand-tuned [H], to be tuned against listening verdicts (docs/LESSONS.md).

What it cannot do: say that a mix is good (Hafezi and Reiss 2015: objective masking measures are poorly suited to
quantifying perceived masking). Numbers find the candidates; ears confirm.
"""
import json
import os
import re
import sys
import time

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import master as MA  # noqa: E402

SR = 44100
THIRD = MA.THIRD
NFFT, HOP = 4096, 2048
REGIONS = [("sub", 20, 60), ("bass", 60, 150), ("lowmid", 150, 400), ("mid", 400, 2000), ("presence", 2000, 6000),
           ("air", 6000, 18000)]
EQMAPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eqmaps.json")
MASK_DB, WITHIN_DB, CENSUS_DB = 6.0, 6.0, 10.0      # [H]
SOUNDING_DB = 45.0                                  # a stem more than 45 dB under the loudest is not sounding [H]
FLAG_MASKED, FLAG_CROWD, FLAG_BUILDUP, FLAG_HP = 0.90, 4, 3.0, 0.10   # [H]

# ------------------------------------------------------------------ roles

TYPE_ROLE = {
    "kick": "kick", "clubkick": "kick", "kitkick": "kick", "toba": "kick", "808": "808",
    "snare": "snare", "kitsnare": "snare", "clap": "clap", "handclap": "clap", "snap": "clap",
    "hat": "hats", "openhat": "hats", "kithat": "hats", "shaker": "hats", "kitride": "cymbals", "kitcrash": "cymbals",
    "crash": "cymbals", "rim": "perc", "tom": "perc", "kittom": "perc", "cowbell": "perc", "darbuka": "perc",
    "bass": "bass", "trancebass": "bass", "ebass": "bass", "sine": "sub", "supersaw": "lead", "lead": "lead",
    "ep": "keys", "piano": "keys", "pad": "pad", "strings": "strings", "strings_section": "strings",
    "viola": "low-strings", "cello": "low-strings", "choir": "choir", "bell": "bells", "musicbox": "bells",
    "celesta": "bells", "glockenspiel": "bells", "vibraphone": "bells", "pluck": "pluck", "organ": "organ",
    "vinyl": "texture", "tape": "texture", "rain": "texture", "eguitar": "guitar", "cleanguitar": "acoustic",
    "acguitar": "acoustic", "vox": "vocal", "vox2": "vocal", "singer": "vocal", "violin": "lead", "fiddle": "lead",
    "kokle": "pluck", "cimbalom": "pluck", "oud": "pluck", "lira": "pluck", "nai": "lead", "ney": "lead",
    "dudas": "lead", "trembita": "lead", "tridksnis": "perc",
    "acid": "upper-bass", "snare909": "snare", "clap909": "clap", "ride909": "cymbals",
}
# name keywords (checked in order); `drums` ones may also re-label a drum-type track (a "cinel" played on a toba)
NAME_ROLE = [(r"cinel|cymbal|ride|crash", "cymbals", True), (r"rim", "perc", True), (r"tom", "perc", True),
             (r"tamb|shak|hat|hh|chh", "hats", True), (r"clap", "clap", True), (r"snare", "snare", True),
             (r"808", "808", False), (r"sub", "sub", False), (r"kick", "kick", False), (r"bass", "bass", False),
             (r"pad", "pad", False), (r"pluck", "pluck", False), (r"arp", "arp", False),
             (r"saws|stab|chord|gate", "support", False), (r"air", "air", False), (r"lead", "lead", False),
             (r"vox|voc|voz|voice", "vocal", False), (r"choir", "choir", False), (r"organ|pedal", "organ", False),
             (r"piano", "keys", False), (r"string|vln|vla", "strings", False), (r"bell|glock", "bells", False),
             (r"riser|sweep|impact|fx", "fx", False)]


def role_of(name, tr, drum_types):
    if tr.get("role"):
        return tr["role"], False
    typ = (tr.get("inst") or tr["layers"][0]["inst"])["type"]  # a stack without inst: its first layer
    n = name.lower()
    for pat, role, drums in NAME_ROLE:
        if re.search(pat, n) and (drums or typ not in drum_types):
            return role, True
    return TYPE_ROLE.get(typ, "other"), True


def load_eqmap(genre):
    if not genre:
        return None, None
    d = json.load(open(EQMAPS_PATH))
    g = d.get("_aliases", {}).get(genre, genre)
    if g not in d:
        return None, g
    m = dict(d[g])
    roles = dict(d[m["inherit"]]["roles"]) if m.get("inherit") else {}
    roles.update(m["roles"])
    m["roles"] = roles
    return m, g


# ------------------------------------------------------------------ analysis

def _band_matrix():
    f = np.fft.rfftfreq(NFFT, 1 / SR)
    B = np.zeros((len(f), len(THIRD)), dtype=np.float32)
    for j, c in enumerate(THIRD):
        B[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6)), j] = 1
    return B


BANDS = _band_matrix()
WIN = np.hanning(NFFT + 1)[:-1].astype(np.float32)


def a_weight_db(f):
    f2 = np.asarray(f, dtype=float) ** 2
    ra = 12194 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    return 20 * np.log10(ra) + 2.0


AW = 10 ** (a_weight_db(THIRD) / 10)
REGION_OF = np.array([next((i for i, (_, lo, hi) in enumerate(REGIONS) if lo <= c < hi), len(REGIONS) - 1)
                      for c in THIRD])


def band_power(x):
    """x: mono float32. (28, frames) power per third-octave band per frame."""
    n = (len(x) - NFFT) // HOP + 1
    if n < 1:
        return np.zeros((len(THIRD), 0), dtype=np.float32)
    idx = np.arange(n)[:, None] * HOP + np.arange(NFFT)[None, :]
    out = np.empty((n, len(THIRD)), dtype=np.float32)
    for s in range(0, n, 256):
        X = np.fft.rfft(x[idx[s:s + 256]] * WIN, axis=1)
        out[s:s + 256] = (np.abs(X) ** 2).astype(np.float32) @ BANDS
    return out.T


def _db(v):
    return 10 * np.log10(np.asarray(v, dtype=float) + 1e-20)


def analyse(stems, roles, mix, target, eqmap, peak, layers=None):
    """stems: {name: (28, frames) power}; roles: {name: (role, inferred)}; mix: mono premaster of the span;
    layers: {stack: {layer: (role, (28, frames) power)}} for the stack view."""
    names = list(stems)
    P = np.stack([stems[n] for n in names])                          # (S, 28, T)
    tot = P.sum(axis=(1, 2))
    loud = tot.max() if len(tot) else 1.0
    keep = tot > loud * 10 ** (-SOUNDING_DB / 10)
    names = [n for n, k in zip(names, keep) if k]
    P = P[keep]
    S = len(names)
    out = dict(sounding=names)
    tcurve = MA.target_curve(THIRD, target) if target else None
    cell = P.sum(0)                                                  # (28, T) energy of all stems
    allE = cell.sum()
    # census and occupancy
    mx = P.max(0)
    within = (P >= mx[None] * 10 ** (-WITHIN_DB / 10)).sum(0)       # (28, T)
    census = []
    for r, (rn, lo, hi) in enumerate(REGIONS):
        bm = REGION_OF == r
        Er = P[:, bm, :].sum(axis=(1, 2))
        share = Er.sum() / (allE + 1e-20)
        top = Er.max() if S else 0
        srcs = sorted([(names[i], round(float(_db(Er[i]) - _db(top)), 1)) for i in range(S)
                       if Er[i] > 0 and Er[i] >= top * 10 ** (-CENSUS_DB / 10)], key=lambda t: -t[1])
        w = cell[bm]
        occ = float((within[bm] * w).sum() / (w.sum() + 1e-20)) if w.sum() > 0 else 0.0
        census.append(dict(region=rn, hz=[lo, hi], share=round(float(share), 3), within_10db=srcs,
                           occupancy=round(occ, 2)))
    out["census"] = census
    # masked and own share per stem, the main masker, level
    PA = P * AW[None, :, None]
    stems_out = []
    for i, n in enumerate(names):
        s = P[i]
        others = cell - s
        masked = others >= s * 10 ** (MASK_DB / 10)
        own = s >= mx - 1e-30
        eA = PA[i].sum()
        msh = float(PA[i][masked].sum() / (eA + 1e-20))
        osh = float(PA[i][own].sum() / (eA + 1e-20))
        # who masks it: each other stem's share of the masking energy, weighted by this stem's energy in the cell
        wcell = np.where(masked, s / (others + 1e-30), 0.0)
        contrib = np.array([(P[j] * wcell).sum() if j != i else 0.0 for j in range(S)])
        mk = names[int(np.argmax(contrib))] if contrib.sum() > 0 and msh > 0.05 else None
        mk_share = float(contrib.max() / contrib.sum()) if mk else None
        role, inferred = roles.get(n, ("other", True))
        spec = _db(s.sum(1))                                          # dB per third octave over the span
        rr = dict(name=n, role=role, inferred=inferred, level_db=round(float(_db(eA) - _db(PA.sum())), 1),
                  masked=round(msh, 2), own=round(osh, 2), masker=mk,
                  masker_share=round(mk_share, 2) if mk_share is not None else None)
        rr["eq"] = eq_check(s, spec, role, eqmap, masked, tcurve) if n not in (layers or {}) else None  # a stack:
        # its layers are checked one by one (stack view)
        stems_out.append(rr)
    out["stems"] = sorted(stems_out, key=lambda r: -r["level_db"])
    # crest per region (mix, 10 ms envelope)
    crest = {}
    for rn, lo, hi in REGIONS:
        b = signal.sosfilt(signal.butter(4, [lo, min(hi, SR / 2 - 200)], "band", fs=SR, output="sos"), mix)
        m = len(b) // 441
        if m < 10:
            continue
        env = np.sqrt((b[:m * 441].reshape(m, 441) ** 2).mean(1) + 1e-20)
        crest[rn] = round(float(20 * np.log10(env.max() / np.sqrt((env ** 2).mean()))), 1)
    out["crest_db"] = crest
    # low-mid build-up against the target
    if target and len(mix) > 2 * SR:
        tb = MA.third_octave(mix.astype(np.float64))
        dev = tb - MA.target_curve(THIRD, target)
        dev -= MA.ref_offset(dev, 2)
        sel = lambda lo, hi: float(np.mean(dev[(THIRD >= lo) & (THIRD <= hi)]))  # noqa: E731
        out["vs_target"] = dict(target=target, kick_sub_50_80=round(sel(50, 80), 1),
                                buildup_100_250=round(sel(100, 250), 1), lowmid_315_400=round(sel(315, 400), 1),
                                presence_2k_5k=round(sel(2000, 5000), 1), air_8k_12k=round(sel(8000, 12500), 1))
    if layers:
        out["stacks"] = stack_view(layers, eqmap, tcurve)
    out["flags"] = flags(out, eqmap, peak)
    return out


def stack_view(layers, eqmap, tcurve):
    """Per stack: each layer's share of the stack's energy per region and overall, its level against the stack's
    loudest layer, and its EQ map check under its own role (docs/PRODUCTION.md section 2, item c: a layer that adds
    nothing shows up here)."""
    res = []
    for stack, L in layers.items():
        names = list(L)
        P = np.stack([L[n][1] for n in names])                       # (K, 28, T)
        tot = P.sum(0)
        rows = []
        E = P.sum(axis=(1, 2))
        for i, n in enumerate(names):
            role = L[n][0] or "other"
            reg = {}
            for r, (rn, lo, hi) in enumerate(REGIONS):
                bm = REGION_OF == r
                den = tot[bm].sum()
                reg[rn] = round(float(P[i][bm].sum() / den), 2) if den > 0 else 0.0
            # where the layer leads the stack: its share of the cells (energy-weighted) it is loudest in
            lead = P[i] >= P.max(0) - 1e-30
            row = dict(layer=n, role=role, level_db=round(float(_db(E[i]) - _db(E.max())), 1),
                       share=round(float(E[i] / (E.sum() + 1e-20)), 3), regions=reg,
                       leads=round(float(P[i][lead].sum() / (E[i] + 1e-20)), 2))
            spec = _db(P[i].sum(1))
            uniq = sum(1 for m in names if (L[m][0] or "other") == role) == 1  # layers sharing a role split its job
            row["eq"] = (eq_check(P[i], spec, role, eqmap, np.zeros_like(P[i], bool), tcurve)
                         if eqmap and uniq else None)
            if row["eq"] and row["eq"].get("cut_over_own_db") is not None:
                row["eq"]["cut_over_own_db"] = max(row["eq"]["cut_over_own_db"], -30.0)
            rows.append(row)
        res.append(dict(stack=stack, layers=rows))
    return res


def eq_check(s, spec, role, eqmap, masked, tcurve=None):
    """A stem against its role's row in the genre's EQ map. `cut_over_own_db`: the stem's mean level per third octave
    in the regions to cut minus that in the region it owns (the loudest of its own regions), relative to the same
    difference in the genre's target curve when there is one: 0 = the stem balances those regions like the genre's
    average record, positive = it is heavier where the map says to cut."""
    if eqmap is None:
        return None
    row = eqmap["roles"].get(role)
    if row is None:
        return None if role in ("fx", "other") else dict(note=f"no map entry for role {role}")
    tot = s.sum()
    res = {}
    if row.get("hp") and row["hp"][0] >= 40:
        lo = row["hp"][0]
        res["below_hp"] = round(float(s[THIRD * 2 ** (1 / 6) <= lo].sum() / (tot + 1e-20)), 2)
        res["hp"] = row["hp"][0]
    if row.get("lp"):
        hi = row["lp"][1]
        res["above_lp"] = round(float(s[THIRD / 2 ** (1 / 6) >= hi].sum() / (tot + 1e-20)), 2)
        res["lp"] = hi

    def lvl(ranges, sp):
        m = np.zeros(len(THIRD), bool)
        for a, b in ranges:
            m |= (THIRD >= a) & (THIRD <= b) if b / a >= 1.26 else (np.abs(np.log2(THIRD / np.sqrt(a * b))) < 1 / 6)
        return float(_db(np.mean(10 ** (sp[m] / 10)))) if m.any() else None
    if row.get("cut") and row.get("own"):
        c = lvl(row["cut"], spec)
        owns = [(lvl([r], spec), r) for r in row["own"] if lvl([r], spec) is not None]
        if c is not None and owns:
            o, r_own = max(owns)
            ref = 0.0
            if tcurve is not None:
                ref = lvl(row["cut"], tcurve) - lvl([r_own], tcurve)
            res["cut_over_own_db"] = round(c - o - ref, 1)
    if row.get("own"):
        m = np.zeros(len(THIRD), bool)
        for a, b in row["own"]:
            m |= (THIRD >= a) & (THIRD <= b)
        e = s[m].sum()
        if e > 0:
            res["own_region_masked"] = round(float(s[m][masked[m]].sum() / e), 2)
    return res


def flags(out, eqmap, peak):
    f = []
    tol = (eqmap or {}).get("tolerance_db", 6.0)
    for r in out["stems"]:
        nm = f"{r['name']} ({r['role']}{'*' if r['inferred'] else ''})"
        if r["masked"] > FLAG_MASKED:
            f.append(f"{nm} is {r['masked']:.0%} masked" + (f", mostly by {r['masker']}" if r["masker"] else "")
                     + ": in practice not in the mix")
        e = r.get("eq") or {}
        if e.get("below_hp", 0) > FLAG_HP:
            f.append(f"{nm}: {e['below_hp']:.0%} of its energy under the map's high-pass point ({e['hp']} Hz)")
        if e.get("above_lp", 0) > FLAG_HP:
            f.append(f"{nm}: {e['above_lp']:.0%} of its energy over the map's low-pass point ({e['lp']} Hz)")
        if e.get("cut_over_own_db") is not None and e["cut_over_own_db"] > tol:
            f.append(f"{nm}: {e['cut_over_own_db']:+.1f} dB heavier in the region the map cuts than in the region it "
                     f"owns, against the genre curve's balance (map tolerance {tol:g} dB)")
    lm = next(c for c in out["census"] if c["region"] == "lowmid")
    if len(lm["within_10db"]) > FLAG_CROWD:
        f.append(f"low-mid crowd: {len(lm['within_10db'])} sources within 10 dB at 150-400 Hz")
    vt = out.get("vs_target")
    if vt and vt["buildup_100_250"] > FLAG_BUILDUP:
        f.append(f"low-mid build-up: 100-250 Hz {vt['buildup_100_250']:+.1f} dB over the target ({vt['target']})")
    if peak:
        for c in out["census"]:
            if c["share"] > 0.001 and len(c["within_10db"]) == 1 and c["occupancy"] < 1.25:
                f.append(f"thin {c['region']}: only {c['within_10db'][0][0]} within 10 dB (occupancy {c['occupancy']})")
        if eqmap:
            have = {r["role"] for r in out["stems"]}
            have |= {l["role"] for st in out.get("stacks", []) for l in st["layers"]}  # a stack's layers fill roles
            for alt in eqmap.get("core", []):
                if not any(a in have for a in alt.split("|")):
                    f.append(f"role empty in a peak section: {alt}")
    return f


# ------------------------------------------------------------------ the command

def section_levels(meta):
    """Approximate level of each section (dB) from the render's per-track RMS envelopes (no audio needed)."""
    hop = meta["rms_hop"]
    envs = [np.asarray(e, dtype=float) ** 2 for e in meta["stems_rms"].values() if len(e)]
    if not envs:
        return {s["name"]: 0.0 for s in meta["sections"]}
    n = min(len(e) for e in envs)
    tot = np.sum([e[:n] for e in envs], axis=0)
    out = {}
    for s in meta["sections"]:
        a = min(int(s["start"] / hop), n - 1)
        b = min(max(a + 1, int(s["end"] / hop)), n)
        out[s["name"]] = float(_db(np.mean(tot[a:b])))
    return out


def run(a, renders, latest, meta):
    import studio as ST
    t_all = time.time()
    proj_path = latest.replace(".wav", ".project.json")
    if not os.path.exists(proj_path):
        raise SystemExit(f"--clarity needs the render's project file ({os.path.basename(proj_path)})")
    P = json.load(open(proj_path))
    genre = a.genre or P.get("genre")
    eqmap, gname = load_eqmap(genre)
    target = None
    if genre:
        gs = MA.load_genres()
        if genre in gs:
            target = gs[genre]["master"]["target"]
    lv = section_levels(meta)
    top = max(lv.values())
    sections = meta["sections"]
    if a.bars:
        b0, b1 = [int(v) for v in a.bars.split("-")]
        bar = 4 * 60.0 / meta["bpm"]
        t0, t1 = (b0 - 1) * bar, b1 * bar
        if meta.get("grid16"):
            g = meta["grid16"]
            t0, t1 = g[min((b0 - 1) * 16, len(g) - 1)], g[min(b1 * 16, len(g) - 1)]
        spans = [(f"bars {b0}-{b1}", t0, t1)]
    elif a.section == "all":
        spans = [(s["name"], s["start"], s["end"]) for s in sections]
    elif a.section:
        want = a.section.split(",")
        spans = [(s["name"], s["start"], s["end"]) for s in sections if s["name"] in want]
        if not spans:
            raise SystemExit(f"no section {a.section!r}. Have: {[s['name'] for s in sections]}")
    else:
        s = max(sections, key=lambda s: lv[s["name"]])
        spans = [(s["name"], s["start"], s["end"])]
    drum_types = set(ST.DRUM_TYPES)
    roles = {n: role_of(n, tr, drum_types) for n, tr in P["tracks"].items()}
    roles.update({"(reverb)": ("return", False), "(delay)": ("return", False), "(fx)": ("fx", False)})
    roles.update({f"({r})": ("return", False) for r in (P.get("mix") or {}).get("returns") or {}})  # named returns
    print(f"CLARITY: {os.path.basename(latest)}  genre {genre or '(none: no EQ map, no target; give --genre)'}"
          + (f"  EQ map {gname}" if eqmap else "") + (f"  target {target}" if target else "")
          + "  (* = role inferred from name/instrument; set \"role\" on the track)")
    results = []
    for label, t0, t1 in spans:
        t_s = time.time()
        stems = {}
        span = {}

        def hook(name, st):
            a0, a1 = span["a0"], span["a1"]
            stems[name] = band_power(((st[0, a0:a1] + st[1, a0:a1]) * 0.5).astype(np.float32))
        layers = {}

        def lhook(stack, layer, role, st):
            a0, a1 = span["a0"], span["a1"]
            layers.setdefault(stack, {})[layer] = (role, band_power(((st[0, a0:a1] + st[1, a0:a1]) * 0.5)
                                                                    .astype(np.float32)))
        pre = 2 * 4 * 60.0 / P["bpm"]
        off = max(0.0, t0 - pre)
        span["a0"], span["a1"] = int(round((t0 - off) * SR)), int(round((t1 - off) * SR))
        _, m = ST.render(P, window=(t0, t1), stem_hook=hook, pre_roll=pre, layer_hook=lhook)
        mix = m["_premaster"]
        mix = ((mix[0, span["a0"]:span["a1"]] + mix[1, span["a0"]:span["a1"]]) * 0.5).astype(np.float32)
        is_peak = lv.get(label, top) >= top - 3.0 if label in lv else True
        r = analyse(stems, roles, mix, target, eqmap, is_peak, layers)
        r.update(section=label, start_s=round(t0, 1), end_s=round(t1, 1), peak=is_peak,
                 seconds=round(time.time() - t_s, 1))
        results.append(r)
        report(r)
    json.dump(dict(render=os.path.basename(latest), genre=genre, eqmap=gname, target=target, sections=results),
              open(os.path.join(os.environ.get("BEAT_DIR", os.getcwd()), "clarity.json"), "w"), indent=1)
    print(f"wrote clarity.json  ({time.time() - t_all:.0f} s)")


def report(r):
    print(f"\n== {r['section']}  {r['start_s']}-{r['end_s']} s  ({len(r['sounding'])} sounding stems"
          + (", a peak section" if r["peak"] else "") + f"; {r['seconds']} s)")
    print("region          share  occ.  sources within 10 dB of the loudest (dB under it)")
    for c in r["census"]:
        src = ", ".join(f"{n}" + (f" {d:+.0f}" if d < 0 else "") for n, d in c["within_10db"]) or "-"
        print(f"{c['region']:9s} {c['hz'][0]:>5}-{c['hz'][1]:<5} {c['share']:4.0%}  {c['occupancy']:4.2f}  {src}")
    vt = r.get("vs_target")
    if vt:
        print(f"against {vt['target']} (dB, curve at the mix's level around 1 kHz): 50-80 Hz {vt['kick_sub_50_80']:+.1f}, "
              f"100-250 Hz {vt['buildup_100_250']:+.1f} (build-up), 315-400 {vt['lowmid_315_400']:+.1f}, "
              f"2-5 kHz {vt['presence_2k_5k']:+.1f}, 8-12.5 kHz {vt['air_8k_12k']:+.1f}")
    print("crest (10 ms, dB): " + ", ".join(f"{k} {v}" for k, v in r["crest_db"].items()))
    print("stem         role          level  masked  own   masked by        EQ map (cut region vs own; under hp)")
    for s in r["stems"]:
        e = s.get("eq") or {}
        eq = []
        if "cut_over_own_db" in e:
            eq.append(f"cut {e['cut_over_own_db']:+.1f} dB")
        if "below_hp" in e:
            eq.append(f"<{e['hp']} Hz {e['below_hp']:.0%}")
        if "above_lp" in e:
            eq.append(f">{e['lp']} Hz {e['above_lp']:.0%}")
        if "own_region_masked" in e:
            eq.append(f"own region {e['own_region_masked']:.0%} masked")
        if "note" in e:
            eq.append(e["note"])
        mk = f"{s['masker']} ({s['masker_share']:.0%})" if s["masker"] else "-"
        print(f"{s['name'][:12]:12s} {(s['role'] + ('*' if s['inferred'] else ''))[:12]:12s} {s['level_db']:6.1f}  "
              f"{s['masked']:5.0%}  {s['own']:4.0%}  {mk[:16]:16s} {'; '.join(eq)}")
    for stv in r.get("stacks", []):
        print(f"stack {stv['stack']}: layer (role) share of the stack, per region sub/bass/lowmid/mid/presence/air; "
              "level vs its loudest layer; EQ map")
        for l in stv["layers"]:
            reg = "/".join(f"{l['regions'][rn]:.0%}" for rn, _, _ in REGIONS)
            e = l.get("eq") or {}
            eq = []
            if "cut_over_own_db" in e:
                eq.append(f"cut {e['cut_over_own_db']:+.1f} dB")
            if "below_hp" in e:
                eq.append(f"<{e['hp']} Hz {e['below_hp']:.0%}")
            if "above_lp" in e:
                eq.append(f">{e['lp']} Hz {e['above_lp']:.0%}")
            print(f"  {l['layer'][:10]:10s} {l['role'][:10]:10s} {l['share']:4.0%}  {reg:28s} {l['level_db']:6.1f} dB  "
                  + "; ".join(eq))
    for f in r["flags"]:
        print("FLAG:", f)
