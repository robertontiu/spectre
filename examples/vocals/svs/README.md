# SVS trial: a singing voice synthesizer instead of bent TTS speech (2026-11-24)

**Outcome:** Robert approved the Hanami chorus by ear ("a clear improvement"). It is now in the engine as `singer` `"source": "svs"` (`engine/svs.py`; voices in `engine/voices.json` and [docs/voice/VOICES.md](../../../docs/voice/VOICES.md); auditions in `voices/`). Robert's remaining note was that it sounded "like the song is playing on a speaker and someone sings along": see **Blend** below. The trial scripts (`dsinger.py`, `build.py`) stay as they were, except for one fix: LEONA's mel is log10, the Potluck vocoder expects a natural log, and they now convert. The first `leona-potluck-line-dry.mp3` was noise because of this; it has been re-rendered.

**Question:** does a model trained on singing (DiffSinger) sing Spectre's short vocal lines better than `singer` `source: "tts"` (Kokoro speech bent onto the melody with WORLD)? Scope: voices as an instrument (hooks, calls, refrain fragments, choir textures), not full songs. Nothing here changes the engine; `engine/singer.py` is untouched.

## Listen

| file | what |
|---|---|
| `hanami-line-dry.mp3` | "here you are, round and round", dry: Hoshino Hanami (female, "natural pop soprano"), own vocoder |
| `hanami-potluck-line-dry.mp3` | the same with the commercial-friendly Potluck vocoder (the chain that is licence-clean, see below) |
| `leona-line-dry.mp3`, `leona-potluck-line-dry.mp3` | LEONA (female, cuter character soprano), own vocoder / Potluck |
| `tiger-line-dry.mp3` | TIGER (male), **non-commercial licence**: for comparison only. Sung at the written notes (F#4-B4), high for a male voice |
| `hanami-potluck-chorus.mp3` | the c1 chorus (pre-chorus + chorus of session 009) with Hanami + Potluck as the lead: same backing, vocal chain, level, double, sends and `master --genre rock` as `../tts/c1-natural.mp3` |
| `choir-line-dry.mp3` | a few-voice texture: four separate takes (Hanami Root + Nectar, LEONA Core + CatNap), melody plus a third below, panned, dry |

Compare with `../tts/b1-natural-dry.mp3` / `../tts/b3-stage4-timing.mp3` (same line, current engine) and `../tts/c1-natural.mp3` (same chorus).

## What was installed

- **DiffSinger, OpenVPI ONNX format** (what OpenUtau runs), driven headless by `dsinger.py` (about 350 lines, numpy + onnxruntime 1.29, CPU). It is a port of OpenUtau's code path (`OpenUtau.Core/DiffSinger`: `DiffSingerBasePhonemizer.ProcessPart`, `DiffSingerPitch.Process`, `DiffSingerRenderer`): words to ARPAbet (the bank's `dsdict-en*.yaml`, then CMUdict via `pip install cmudict`), phonemes grouped per note from the vowel on (a note's onset consonants belong to the previous group, so they are sung before the note and the vowel lands on it), the bank's **duration model** predicts every phoneme's length, each group is stretched to its note span, the **pitch model** draws the f0 (auto-pitch), the **acoustic model** makes the mel, the **vocoder** the wave. OpenUtau defaults: 20 acoustic steps, 10 pitch steps, depth = the bank's max depth, gender 0, velocity 1.
- Two deviations from a bare OpenUtau render, both small: a 300 ms closing `SP` token after each phrase (DiffSinger's training phrases end in `SP`; without it Hanami held the final "d" of "round" for 590 ms and Whisper heard "brown"), and 5 ms fades at phrase edges (TIGER clicked at its first frame). Renders are deterministic: onnxruntime is seeded before the sessions are made.
- `pip install faster-whisper` (small.en) only as a rough intelligibility check; not needed to render.
- Model files live in `~/.cache/spectre/svs/<bank>/bank/` (500-560 MB per bank, plus `potluck/`), never in git.

## Voicebanks and licences

| bank | voice | source | licence (summary) | for Spectre (CC BY 4.0 tracks)? |
|---|---|---|---|---|
| **Hoshino Hanami ~AI❤dol~ v1.0** by Lotte V | female, "natural pop soprano", ~2 h English data (3 h 53 min total, 8 languages), 3 modes (Root, Fragrance = power, Nectar = soft) | <https://lottev.moe/> (MediaFire link in the v1.0 release post); terms also in <https://github.com/lottev1991/LotteV-Voicebank-Update-Repo> | Team L❤VE Voicebank License + Terms of Use: use "for any creative purpose, even commercially", no permission needed; credit Lotte V; don't redistribute/sell the files or claim the voice; no political, hateful or illegal use; derivative voices only through synth settings. **Its vocoder AI❤dolGAN is fine-tuned from OpenVPI NSF-HiFiGAN: CC BY-NC-SA 4.0** | yes **with the Potluck vocoder** (credit "Hoshino Hanami by Lotte V"). Note the "no political applications" clause |
| **LEONA -Ubasti- AI for DiffSinger** v0.0.1b (beta) by Lotte V | female, "cute, character-style" soprano, ~2 h English, trained multispeaker with Hanami's data; modes Core, CatNip, CatNap | <https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/releases/tag/v0.0.1b-leona> | voicebank **CC BY 4.0** (`__license/LICENSE_voicebank.txt`) + the same Terms of Use as Hanami; **vocoder "meowcoder" CC BY-NC-SA 4.0** | yes with the Potluck vocoder; but it is a beta and the less natural, more anime-styled of the two |
| **TIGER** v102 by tigermeat | male, English | <https://github.com/spicytigermeat/tiger_diffsinger/releases/tag/v102> | **CC BY-NC-ND 4.0 + Commons Clause**: non-commercial only, commercial use needs a purchased licence; no redistribution or derivatives | **no** (only to hear a male DiffSinger voice). CC BY tracks may be reused commercially by others, which this licence forbids |
| **Potluck Vocoder** (lite, PC-NSF-HiFiGAN) v100 by tigermeat | vocoder, community data | <https://github.com/mrtigermeat/potluck-vocoder/releases/tag/v100> (`dsvocoder.zip`) | adapted from CC BY 4.0: free to use, share, adapt; **commercial use allowed only with DiffSinger models**; attribution with a link to the licence; outputs/weights may not be used to train other generative models | yes (we use it with DiffSinger). Credit "Potluck Vocoder by tigermeat" |

Not used: No.7 (SEVEN) and Miyo (non-commercial), Albus Korde/LUNAI (non-commercial), the OpenVPI NSF-HiFiGAN vocoders (CC BY-NC-SA). English DiffSinger banks with clean commercial terms are rare, and almost all are character voices (idol, cute, anime-adjacent); Hanami is the most natural-sounding adult one found within the time box. GitHub release pages of unlisted repos are blocked in the sandbox (assets download fine when the name is known); the community wiki (diffsinger.miraheze.org) is blocked too.

## Reproduce

```bash
# banks (see the table for sources) unpacked so that ~/.cache/spectre/svs/<bank>/bank/dsconfig.yaml exists,
# Potluck's dsvocoder.zip unpacked into ~/.cache/spectre/svs/potluck/
pip install cmudict
python3 examples/vocals/svs/build.py line                  # <bank>-line-dry.mp3 for hanami leona tiger + timing tables
python3 examples/vocals/svs/build.py line hanami-potluck leona-potluck
python3 examples/vocals/svs/build.py timing hanami-potluck # dry chorus timing table
python3 examples/vocals/svs/build.py chorus hanami-potluck # mixed + mastered like c1 (runs studio.py in-process with singer.sing swapped)
python3 examples/vocals/svs/build.py choir
```

## CPU cost (2 threads, this sandbox)

The 6.2 s line renders in 5-6 s once the models are loaded (about 1 s more on first load): acoustic model 3.2-3.9 s, vocoder 1.5-1.9 s, pitch 0.6 s, durations under 0.1 s. The 15 s dry chorus: 17-20 s. The whole c1 chorus (two SVS takes for the double, the backing, mix and master): 61 s. Peak RAM for a line is about 1.2 GB. So roughly real time: usable for hooks and short lines in a producer loop, if renders are cached per phrase.

## Timing (same metrics as `tools/joincheck.py --timing`)

Perceived onset (P-centre, the "maxD" fastest 300-3000 Hz energy rise) against the score; for the SVS the syllable boundaries are its own phoneme boundaries. Current engine = `joincheck.py --timing` on the same line, and `/tmp/tts-joins-ready.txt` ("timing fix, final") for the chorus.

| | P-centre mean | sd | max \|dev\| | IOI error sd | beyond JND | beyond 3x JND | consonant start vs beat | vowel vs beat | lead |
|---|---|---|---|---|---|---|---|---|---|
| **line**, current engine | +23 ms | 35 | 75 | 56 | 5/6 | 2 | | | |
| line, Hanami | -24 | 52 | 135 | 64 | 2/6 | 1 | -76 | 0 | 76 |
| line, Hanami + Potluck | -27 | 50 | 135 | 61 | 2/6 | 1 | -76 | 0 | 76 |
| line, LEONA | -18 | 60 | 150 | 63 | 2/6 | 1 | -76 | 0 | 76 |
| line, TIGER | +2 | 49 | 80 | 49 | 5/6 | 3 | -102 | 0 | 102 |
| **chorus**, current engine | +23 | 40 | 124 | 61 | 16/24 | 5 | -12 | +72 | 78 |
| chorus, Hanami + Potluck | -25 | 39 | 115 | 57 | 13/24 | 9 | -63 | 0 | 63 |
| chorus, LEONA | -19 | 33 | 110 | 48 | 11/24 | 8 | -65 | 0 | 65 |
| chorus, TIGER | -20 | 31 | 90 | 50 | 10/24 | 7 | -78 | 0 | 78 |
| human singers (GTSinger, docs/voice/GENERAL.md) | | | | | | | +1 | +106 | 91 |

Reading it:
- **On these numbers it is a draw.** Spread and inter-onset regularity are about the same as the engine's after its timing fix (sd 31-39 vs 40 ms on the chorus, IOI sd 48-57 vs 61), with fewer onsets beyond the JND but more beyond 3x the JND. Between takes of the same bank the line's P-centre numbers move by 10-20 ms (the pitch model samples a new curve each time), so differences that size mean nothing.
- **DiffSinger, as OpenUtau drives it, puts the vowel exactly on the note and the consonants before it** (63-102 ms lead). That is the classical rule (VOCALOID, Saino 2006), not what the GTSinger singers do (consonant on the beat, vowel about 100 ms later), and it is a labelling convention of DiffSinger datasets (a note starts at its vowel), not something the model learned. What the model does learn is the consonant lengths in context (hh 105-140 ms, y 60-85, r 40-70, st 193) and how the phonemes flow into each other. The worst flags are the phrase-initial words ("here", "hold": P-centre 100-145 ms early, on the /h/), the same words the engine used to rush.
- Intelligibility (Whisper small.en, a rough proxy): all three dry SVS choruses transcribe word-perfect. On the short line the engine's renders also transcribe perfectly (they are speech underneath); the SVS lines mostly do, with the last "round" sometimes heard as "band"/"bend" (LEONA).
- What the metrics do not capture is what the SVS is for: the joins, coarticulation, vibrato, pitch transitions and breath come from one model of a singing voice, so there is nothing to stitch. In the spectrograms the SVS lines show continuous formant transitions at every join and singer-like vibrato and scoops; the engine's line shows the speech-derived consonant bursts (e.g. the "d" of "round and").

## Verdict (by measurement and spectrograms; it needs Robert's ears)

- **It works**: free, local, CPU, about real time, deterministic, intelligible, and it removes the whole class of join, cadence and stitching problems the `tts` path keeps hitting, because the sung voice is made in one piece by a model of a singer. For Spectre's use (short lines, hooks, refrain fragments) that is the right shape of tool, and the four-take choir test shows it can make a few-voice texture from separate takes and modes cheaply.
- **Timing is not better by the numbers**, only different: the model's "vowel on the note" convention gives consonants 60-100 ms ahead of the beat. If that sounds early by ear, the fix is one parameter (shift each note group so the onset consonant starts on the beat), not a pile of rules.
- **The real limit is voices and licences.** Commercial-clean English banks are few and mostly character voices; Hanami ("natural pop soprano") is the best candidate found, and only with the Potluck vocoder (her own vocoder is non-commercial). No commercial-clean male English bank was found in the time box (TIGER is non-commercial). The Potluck "lite" vocoder is a general model; its author recommends fine-tuning it per voice.
- **Recommendation:** if the Hanami + Potluck chorus sounds more like singing than `c1-natural` to Robert, this is the better path for sung hooks: integrate it as a `singer` source (`source: "svs"`) that renders each phrase with the bank and caches it, keeping the existing vocal chain (fx, double, sends). If the voice character is wrong for Spectre, the next step is not more rules but a different or self-trained bank (DiffSinger training needs about 1-2 h of clean, licensed singing and a GPU).

## Blend: "singing along to a speaker" (engine `source: "svs"`, voice hanami)

`blend.py` rebuilds everything. Each variant is the c1 chorus with the same backing and the same `master --genre rock`. To measure, every variant is rendered four times: full mix, vocal muted, send returns off, and both. That gives the vocal as heard in the mix, the band, and each one's dry and wet parts, all over chorus1. Whisper (small.en) word accuracy is taken on the **full mastered mix**: it is a rough, single-run proxy for whether the words still read (guitars make it hard; one run per mix).

| file | what changes | vocal vs band LU | wet vs dry, vocal / band dB | L/R coherence 0.5-4 kHz, vocal / band | side-mid dB, vocal / band | 8 kHz vs band | phrase release ms | Whisper words |
|---|---|---|---|---|---|---|---|---|
| `blend-ref-tts.mp3` | c1 as it was (tts singer) | -0.5 | -11.4 / -22.2 | 0.77 / 0.52 | -8.9 / -6.6 | +4.4 | 340 | 46% |
| `blend-ref-svs.mp3` | approved svs chorus, c1's tts chain | -0.6 | -11.4 / -22.2 | 0.77 / 0.52 | -8.8 / -6.6 | **-3.8** | 160 | 42% |
| `blend-a.mp3` | **tone**: hpf 100 (was 150), 800 Hz -2.5 instead of 500 Hz +3, high shelf +3 dB at 8 kHz | -1.3 | -11.5 / -22.2 | 0.77 / 0.52 | -8.8 / -6.6 | -0.7 | 160 | 54% |
| `blend-b.mp3` | a + **room**: the kit's early reflections on the voice (`room` 0.35/0.3), send 0.28, 35 ms pre-delay, -1 dB | -2.9 | -8.9 / -22.2 | **0.56** / 0.52 | -6.5 / -6.6 | -1.1 | 235 | fails (transcribes other words) |
| `blend-c.mp3` | b + edges (double 0.2, breath, 30/120 ms phrase fades) + guitars -2.5 dB at 2.5 kHz + glue comp | -3.2 | -8.7 / -22.6 | 0.60 / 0.55 | -7.5 / -6.8 | +1.2 | 260 | 42% |
| **`blend-d.mp3`** | a + **space without smear**: no early reflections, reverb send 0.32 behind a **60 ms pre-delay**, double 0.2 panned wider (0.7), breath, soft phrase edges, guitars -2.5 dB at 2.5 kHz | -0.9 | -8.4 / -22.6 | 0.66 / 0.55 | -6.3 / -6.8 | -0.1 | 270 | **62%** |
| `blend-e.mp3` | d + a light room (`room` 0.3, mix 0.12) | -1.2 | -8.1 / -22.6 | 0.64 / 0.55 | -6.1 / -6.8 | -0.2 | 290 | 58% |

What the numbers say:
- Against the band, the approved chorus was **dull on top** (8 kHz 3.8 dB under the band, where the tts voice was 4.4 dB over it). It was also **more mono** (coherence 0.77 vs the band's 0.52; side-mid 2 dB narrower) and **barely in the room**.
- It is also 7-8 dB heavier at 500 Hz-1 kHz than this guitar-and-drum band. That comes from the voice itself: no EQ variant moved it by more than about 1 dB.
- Its phrase ends were short: the 90-10 % release was 160 ms, against the tts voice's 340 ms.
- Putting the kit's early reflections on the voice (b) matched the band's width and coherence almost exactly, but it smeared the consonants and Whisper lost the words. A light room (e) costs a little clarity too.
- The best balance is **d**: air back, the reverb's wet level up 3 dB behind a 60 ms pre-delay (the tail sits in the band's reverb, the words stay clean), a wider and quieter double, soft phrase edges with a breath, and a little 2.5 kHz room carved in the guitars. Its width now matches the band (-6.3 vs -6.8 dB side-mid), it is less mono (0.66), and its words read best of all versions (62%, vs 42% before).
- d is the mix example in docs/MANUAL.md "Voices". `reverb_predelay_ms` is a new track key (studio.py; 0 = as before).
- All of this is measured, not heard: b, c, d and e need Robert's ears.

## Engine integration (`singer` `"source": "svs"`)

- `engine/svs.py` is the same OpenUtau code path as `dsinger.py`, with a few additions:
  - syllables and melismas from the engine's lyric notation;
  - phrases split at rests (a gap over 12% of the note's slot, or 25 ms);
  - an optional breath (the model's own `AP`);
  - phrase-edge fades;
  - a double as a second take.
- **Deterministic**: each bank's pitch and acoustic models are patched once (cached in `~/.cache/spectre/svs/<bank>/patched/`). Their starting noise becomes an input, fed from a generator seeded by the phrase and the track's `seed`, so a phrase renders the same no matter what was rendered before. Verified by rendering the same line twice from an empty cache: identical.
- LEONA's DDPM models also draw noise inside the sampling loop. Those nodes get a fixed seed, and the sessions are rebuilt per phrase, which is slower on a first render but deterministic.
- Rendered phrases are cached in `~/.cache/spectre/svs/phrases/`, keyed by the render version, bank, mode, vocoder, settings, words, notes and seed.
- `tts` and the eSpeak sources are untouched: `singer.sing` only gains an early branch for `source: "svs"`. Verified: the tts and `breathy` renders of the line are bit-identical to the previous `singer.py`.
