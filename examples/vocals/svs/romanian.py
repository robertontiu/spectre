"""Romanian experiment for singer source "svs" (docs/voice/languages/ro.md, "Can a voice sing Romanian?").

python3 examples/vocals/svs/romanian.py     # renders, transcribes, writes romanian.json and romanian-hanami-experiment.mp3

No licence-clean voice was trained on Romanian. This checks whether Hanami (DiffSinger, trained on 8 other languages)
can be steered into Romanian by mapping Romanian letters to phonemes it knows from those languages: Spanish vowels,
unaspirated stops, clear l and tapped r; the German schwa `ax` for ă; the Korean ㅡ vowel `eu` for î/â; Japanese
palatalized `ky`/`gy` for ch/gh before e/i; glides for the diphthongs (ea, oa, ia, ie, iu, ua) and offglides `I1`/`U1`
(ai, ei, oi, ui, au, eu); a final non-syllabic i after a consonant (pomi, tăi) as `I1`; initial e as [je] in the
pronouns and forms of "a fi". Five lines are sung dry (Hanami Root, 92 bpm, E4-B4) through the bank directly (not
the engine: Romanian is not wired), then Whisper small (multilingual, int8 CPU) transcribes them forced to Romanian:
word accuracy and character accuracy (spaces and diacritics ignored: Whisper writes "prima vara" for "primăvară"),
plus which language Whisper detects. The control sings the same lines through the Spanish G2P (engine/lang_es.py).
This is an experiment, not an engine feature; Whisper cannot judge ă/î (it drops diacritics), so the verdict needs a
native ear.
"""
import json, os, subprocess, sys, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "engine"))
import svs

V = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u1", "ă": "ax", "â": "eu", "î": "eu"}
GL = {"e": "y", "i": "y", "o": "w", "u": "w"}
OFF = {"i": "I1", "u": "U1"}
JE = {"e", "el", "ea", "ei", "ele", "eu", "este", "ești", "era", "eram", "erai", "erau"}
C = {"b": ["b"], "d": ["d"], "f": ["f"], "v": ["v"], "s": ["s"], "z": ["z"], "l": ["l1"], "m": ["m"], "n": ["n"], "p": ["px"],
     "t": ["tx"], "ș": ["sh"], "ş": ["sh"], "ț": ["ts"], "ţ": ["ts"], "j": ["zh"], "r": ["rx"], "x": ["kx", "s"],
     "k": ["kx"], "q": ["kx"], "w": ["v"], "y": ["y"]}
def g2p_ro(word):
    parts = [p for p in word.lower().split("-") if p]
    letters = [(ch, k) for k, p in enumerate(parts) for ch in p]
    out = [[] for _ in parts]
    i = 0
    nxt = lambda j: letters[j][0] if j < len(letters) else ""
    whole = "".join(parts)
    while i < len(letters):
        ch, k = letters[i]
        if ch in V:
            j = i
            while j < len(letters) and letters[j][0] in V and letters[j][1] == k:
                j += 1
            cl = [c for c, _ in letters[i:j]]
            # nucleus: the strongest vowel (a/ă/â/î/o/e before u/i offglides)
            strength = {"a": 5, "ă": 4, "â": 4, "î": 4, "o": 3, "e": 3, "u": 1, "i": 1}
            if len(cl) == 1:
                ph = [V[cl[0]]]
            else:
                n = max(range(len(cl)), key=lambda q: (strength[cl[q]], -q))
                if cl == ["i", "i"]:
                    n = 0
                ph = [GL[c] for c in cl[:n]] + [V[cl[n]]] + [OFF.get(c, V[c]) for c in cl[n + 1:]]
            if i == 0 and whole in JE and cl[0] == "e":
                ph = ["y"] + ph
            out[k] += ph
            i = j
            continue
        n1 = nxt(i + 1)
        if ch in "cg":
            hard = {"c": "kx", "g": "g"}[ch]
            if n1 == "h" and nxt(i + 2) in ("e", "i"):
                out[k].append({"c": "ky", "g": "gy"}[ch]); i += 2; continue
            if n1 in ("e", "i"):
                out[k].append({"c": "ch", "g": "jh"}[ch])
                # silent e/i before another vowel (cea, cio, giu), or a final non-syllabic i (dulci)
                if nxt(i + 2) in V and nxt(i + 2) not in ("i",) and letters[i + 1][1] == (letters[i + 2][1] if i + 2 < len(letters) else -1):
                    i += 2; continue
                i += 1; continue
            out[k].append(hard); i += 1; continue
        if ch == "h":
            out[k].append("x" if (n1 == "" or n1 not in V) else "hh"); i += 1; continue
        if ch == "n" and n1 in ("c", "g") and nxt(i + 2) not in ("e", "i"):
            out[k].append("ng"); i += 1; continue
        if ch in C:
            out[k] += C[ch]; i += 1; continue
        i += 1
    # a final i after a consonant in a syllable that already has a nucleus is [ʲ] (pomi, lupi, dulci, tăi)
    for s in out:
        nuc = [q for q, p in enumerate(s) if p in V.values()]
        if len(nuc) >= 2 and s[-1] == "i":
            s[-1] = "I1"
    return out

LINES = [
    ("a-cum e pri-mă-va-ră", "E4:2 F#4:2 G4:2 A4:2 B4:4 A4:2 G4:6"),
    ("în o-chii tăi e lu-mi-nă", "B4:2 A4:2 G4:2 A4:4 G4:2 F#4:2 G4:2 E4:8"),
    ("ți-ne-mă de mâ-nă", "A4:4 G4:2 F#4:2 G4:4 A4:2 E4:8"),
    ("noap-tea vi-ne în-cet", "F#4:4 G4:2 A4:2 B4:2 G4:2 A4:10"),
    ("dor de ca-să dor de voi", "E4:4 G4:2 A4:4 G4:2 F#4:4 G4:2 E4:10"),
]
MIDI = {"E4": 64, "F#4": 66, "G4": 67, "A4": 69, "B4": 71}

def render(bank, lyrics, mel, mode, path, bpm=92):
    q = 60000 / bpm / 4
    t, notes = 300.0, []
    toks = mel.split()
    sylls = []
    for w in lyrics.split():
        sylls += path(w)
    for k, tok in enumerate(toks):
        nm, ln = tok.split(":")
        notes.append((t, float(ln) * q, MIDI[nm], k)); t += float(ln) * q
    for s in sylls:
        for p in s:
            assert p in bank.tok_dur and p in bank.tok_ac, (p, lyrics)
    assert len(sylls) == len(notes), (lyrics, sylls)
    wav, t0, _ = bank.render(sylls, notes, mode, 1234)
    y = np.zeros(int((t + 900) / 1000 * 44100) + len(wav), np.float32)
    a = max(0, int(t0 / 1000 * 44100)); y[a:a + len(wav)] += wav
    return y / (np.abs(y).max() + 1e-9) * 0.7, sylls

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))
    return "".join(c if c.isalnum() or c.isspace() else " " for c in s.replace("-", "")).split()

def acc(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1)); d[:, 0] = range(len(r) + 1); d[0, :] = range(len(h) + 1)
    for a in range(1, len(r) + 1):
        for b in range(1, len(h) + 1):
            d[a, b] = min(d[a - 1, b] + 1, d[a, b - 1] + 1, d[a - 1, b - 1] + (r[a - 1] != h[b - 1]))
    return max(0.0, 1 - d[-1, -1] / len(r))

def cacc(ref, hyp):
    return acc(" ".join("".join(norm(ref))), " ".join("".join(norm(hyp))))

if __name__ == "__main__":
    voices, banks = svs.voices()["voices"], svs.voices()["banks"]
    bank = svs.Bank.get("hanami", banks)
    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2,
                      download_root=os.path.expanduser("~/.cache/spectre/svs/hf/hub"))
    es = lambda w: bank.syllables(w, len([x for x in w.split("-") if x]), "es")
    res, clips = {}, {}
    for name, path in (("ro-map", g2p_ro), ("es-g2p", es)):
        tot, ctot, rows = [], [], []
        for lyr, mel in LINES:
            y, sy = render(bank, lyr, mel, "Root", path)
            import librosa; f = librosa.resample(y, orig_sr=44100, target_sr=16000); clips.setdefault(name, []).append(y)
            segs, _ = wm.transcribe(f, language="ro", beam_size=5, condition_on_previous_text=False)
            hyp = " ".join(s.text for s in segs).strip()
            _, info = wm.transcribe(f, beam_size=1, condition_on_previous_text=False)
            a = acc(lyr, hyp); c = cacc(lyr, hyp); tot.append(a); ctot.append(c)
            rows.append(dict(lyrics=lyr, hyp=hyp, acc=round(float(a), 2), char=round(float(c), 2), lang=info.language,
                             p=round(float(info.language_probability), 2), ph=[" ".join(s) for s in sy]))
            print(name, rows[-1], flush=True)
        res[name] = dict(mean=round(float(np.mean(tot)), 3), char=round(float(np.mean(ctot)), 3), rows=rows)
    json.dump(res, open(os.path.join(HERE, "romanian.json"), "w"), ensure_ascii=False, indent=1)
    gap = np.zeros(int(0.5 * 44100), np.float32)
    trim = lambda c: c[:int(np.nonzero(np.abs(c) > 1e-4)[0][-1]) + 4410]
    y = np.concatenate([np.concatenate([trim(c), gap]) for c in clips["ro-map"]])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", "44100", "-ac", "1", "-i", "-",
                    "-b:a", "96k", os.path.join(HERE, "romanian-hanami-experiment.mp3")], input=y.astype("<f4").tobytes(),
                   check=True)
    print({k: (v["mean"], v["char"]) for k, v in res.items()})
