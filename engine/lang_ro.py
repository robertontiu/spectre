"""Romanian letters to DiffSinger phonemes for `singer` `"source": "svs"` with `"lang": "ro"` (Hanami only).

No DiffSinger bank was trained on Romanian. This is the phoneme mapping of the Romanian experiment
(examples/vocals/svs/romanian.py; docs/voice/languages/ro.md), approved by the owner's ear as "good enough" on
2026-11-26: Romanian letters go to phonemes Hanami knows from its other languages (Spanish vowels, unaspirated stops,
clear l, tapped r; the German schwa `ax` for ă; the Korean ㅡ vowel `eu` for î/â; Japanese palatalized `ky`/`gy` for
ch/gh before e/i; glides for the diphthongs and offglides `I1`/`U1`; a final non-syllabic i as `I1`; initial e as
[je] in the pronouns and forms of "a fi"). Hyphenate the lyrics by syllable (pri-mă-va-ră): each hyphen part is one
syllable and one note. Lotte V's terms forbid political use: never in a track with a political subject.
"""

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


def syllables(word, n):
    """The word's phonemes as n syllables (one per hyphen part), or None when the hyphenation does not give n."""
    parts = [p for p in word.lower().strip(",.!?;:'\"()«»„”").split("-") if p]
    if not parts:
        return None
    out = g2p_ro("-".join(parts))
    if len(out) != n or any(not s for s in out):
        return None
    return out
