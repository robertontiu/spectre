# Voice catalogue: `singer` `"source": "svs"`

The voices the producer can choose for sung words (docs/MANUAL.md "Voices"). Pick one with `"voice": "<id>"`. The same data is machine-readable in `engine/voices.json`: tags, range, licence and credit. Auditions are in `examples/vocals/svs/voices/<id>.mp3`. Each audition is the same two bars, dry: "here you are, round and round", F#4-B4 at 100 bpm (the male voices an octave lower). `examples/vocals/svs/voices.py` rebuilds the auditions and the measurements.

**Voices are instruments** (standing rule 14): short lines, hooks, calls, refrain fragments and choir textures, never a sung song.

## Mixing a voice
Choosing a voice is half of it; the other half is the mix. The principles for every genre, the choir and ensemble research (separate takes, `svs_vibrato`, timing scatter, voice counts, reverb) and the Whisper and loudness checks are in [MIXING.md](MIXING.md). Each genre has a researched starting chain: [caroling](../CAROLING.md#mixing-the-voice-researched-2026-11-24), [trance](../TRANCE.md#mixing-the-voice-researched-2026-11-24), [Latin pop](../LATIN_POP.md#mixing-the-voice-researched-2026-11-24), [pop rock](../POP_ROCK.md#mixing-the-voice-researched-2026-11-24), [hip hop](../HIPHOP.md#mixing-the-voice-researched-2026-11-24), [joc and Romanian folk](../JOC_TIGANESC.md#mixing-the-voice-researched-2026-11-24). Two rules that came out of measurement: words go on the clear voices (`hanami`, `hanami-power`, `hanami-es`), never on `hanami-dark`; and every voice singing the same words starts them together (`push_ms` 0).

## Licences and credit (read before using a voice)

| bank | licence | credit line (put it in the session README's **Credits** and the site notes) |
|---|---|---|
| Hoshino Hanami ~AI❤dol~ v1.0, by Lotte V | Team L❤VE Voicebank License and Terms of Use. Any creative use is allowed, commercial included, without asking. Conditions: credit Lotte V; don't redistribute or sell the files; don't claim the voice as your own; no political, hateful or illegal use. Religious works are allowed without asking as long as they aren't for proselytizing (ToU_EN.md in Lotte V's lottev-voicebank-update-repo, read 2026-11-24): a carol quoted in a secular track is fine. | Vocals: Hoshino Hanami (DiffSinger voicebank by Lotte V, lottev.moe), Potluck Vocoder by tigermeat |
| LEONA -Ubasti- v0.0.1b (beta), by Lotte V | The voicebank is CC BY 4.0, plus the same Terms of Use as Hanami. | Vocals: LEONA (DiffSinger voicebank by Lotte V, lottev.moe, CC BY 4.0), Potluck Vocoder by tigermeat |
| SoulX-Singer (Soul AI Lab) with VocalSet prompt singers: `male-light`, `male-deep` (**waiting for the owner's verdict**) | Model code and weights Apache 2.0; prompt recordings CC BY 4.0. No ban on commercial use, AI-made music or political subjects. Open point: the prompt singers' consent ("Male voices" below). Uses its own vocoder, not Potluck. | Vocals: SoulX-Singer (Soul AI Lab, Apache 2.0, https://github.com/Soul-AILab/SoulX-Singer), voice from a singer of VocalSet (Wilkins, Seetharaman, Wahl, Pardo 2018, https://zenodo.org/records/1193957, CC BY 4.0) |
| Potluck Vocoder (lite) v100, by tigermeat | The engine uses this vocoder for every voice, because both banks' own vocoders are CC BY-NC-SA. Commercial use is allowed only with DiffSinger models. Credit it with a link to its licence (https://github.com/mrtigermeat/potluck-vocoder). Its output may not be used to train generative models. | (included in the lines above) |

**Never use a Lotte V voice in a track with a political subject** (for example session 011, "Corruption" / "Deșteaptă-te, române!"). Their terms forbid political use. For such a track, use the wordless `vox`/`vox2` or no voice.

## The voices

How to read the measurements: they are taken on the dry audition (WORLD analysis, `examples/vocals/svs/voices.py`).
- **tilt**: energy at 2-5 kHz relative to 0.2-1 kHz. Higher means brighter.
- **breath**: aperiodicity at 1-4 kHz. 0 is pure harmonics; higher is breathier.
- **F1/F2**: formants of the long "are" vowel, from LPC.
- **vib**: vibrato depth in cents (sd on long notes).
- **Whisper**: whether Whisper small.en transcribed the dry audition correctly.

| id | bank / mode | sound (tags) | suits (emotions; genres) | bad at | tilt dB | breath | F1/F2 Hz | vib | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| `hanami` (default) | Hanami / Root | female, warm, clear, natural | tender, hopeful, nostalgic, sincere; pop rock, ballad, lo-fi, folk, carol choir, hip-hop hooks | grit, belting, menace, male parts | -8.6 | 0.06 | 617/987 | 32 | correct |
| `hanami-power` | Hanami / Fragrance | bright, firm, open, forward | joyful, anthemic, confident; pop rock choruses, trance/EDM hooks, calls over dense mixes | intimacy, whisper | -5.7 | 0.06 | 958/1501 | 27 | correct |
| `hanami-soft` | Hanami / Nectar | soft, dark, airy | intimate, melancholy, dreamy, longing; lo-fi, ambient, ballad, dream pop, choir pads | cutting through guitars or saws; energy | -19.3 | 0.10 | 511/1024 | 39 | correct |
| `hanami-dark` | Hanami / Root, gender -0.5 | dark, rounded, covered (formants lowered) | solemn, mournful, mysterious, reverent; folk lament, dark ambient, choir alto, cinematic | bright pop; diction in dense mixes | -28.4 | 0.10 | 498/1009 | 32 | wrong ("here's a round-and-down") |
| `hanami-es` | Hanami / Root, **Spanish** (`"lang": "es"`) | female, warm, clear, natural; Latin American Spanish | tender, sincere, warm, nostalgic; Latin pop, bolero and bachata lines, ballad | a native accent (7 min of Spanish data), male parts, grit | | | | | Spanish: 96% of words ("Spanish" below) |
| `hanami-es-soft` | Hanami / Nectar, **Spanish** (`"lang": "es"`) | soft, dark, airy; Latin American Spanish | intimate, tender, longing; bolero, romantic ballad, Latin acoustic pop | dense mixes, energy, a native accent | | | | | Spanish: 96% of words |
| `leona` | LEONA / Core (beta) | bright, light, youthful, character/cute | playful, cheeky, sunny, excited; anime-style hooks, hyperpop, chiptune, trance | mature, serious or sad lines; natural adult pop | -3.2 | 0.05 | 801/1397 | 18 | correct |
| `leona-power` | LEONA / CatNip (beta) | brightest, hard, edgy | energetic, excited, bratty, triumphant; EDM/trance drops, hyperpop, rock calls | tenderness, warmth | +1.6 | 0.05 | 906/1318 | 18 | slurred ("hear you around") |
| `leona-soft` | LEONA / CatNap (beta) | soft, breathy, airy, dark | wistful, tender, fragile; lo-fi, dream pop, ambient, choir pads | dense mixes, energy | -17.0 | 0.18 | 526/1030 | 33 | slurred ("hear you around") |

**Range.**
- Hanami: the training data sits at G3-D5 (most of it C4-A#4, peak G4; `midi_distribution.jpg` in the bank). Write A3-D5. A fifth lower (B3-E4) and a fifth higher (C#5-F#5) both still transcribe correctly (`ctl-hanami-low`, `ctl-hanami-high`). The engine warns outside G3-F5.
- LEONA: trained together with Hanami's data. The range is assumed to be the same, not measured; the engine warns outside A3-F5.
- Both are female voices. Writing them an octave lower does not make a male voice. The male voices are `male-light` and `male-deep` (B2-E4; another model, waiting for the owner's verdict: "Male voices" below).

## Spanish (`hanami-es`, `hanami-es-soft`; searched and checked 2026-11-24)

**What sings Spanish.** Hoshino Hanami is officially trilingual and more: its readme lists the languages "for which actual data has been recorded": English (about 2 h), Japanese (40 min), German (17 min), Korean (11 min), **Spanish (about 7 min)**, Mandarin (6 min), Latin (5 min, no dictionary), French (3 min); "No external data has been used for training. Due to this, some of the data might have a bit of an accent." The bank ships a Spanish dictionary (`dsdur/dsdict-es.yaml`, identical to the one in Lotte V's [update repo](https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/tree/main/dsdict), commit b866687, 2024-09-30) and the Spanish phonemes are in the repo's [Phoneme_chart.md](https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/blob/main/Phoneme_chart.md) (a e i o u1; bh dh gh; px tx kx; rx rr; l1 ny ch x j th zh h; glides y w I1 U1). The dictionary lists only exceptions (numbers, names, about 280 words with consonantal "y"); the engine reads every other word with its own Spanish G2P, `engine/lang_es.py` (rules and sources: [languages/es.md](languages/es.md)), which matches the dictionary on 269 of its 278 Spanish words. **LEONA can't sing Spanish:** it ships English and Japanese dictionaries only and its phoneme set (71 symbols) lacks the Spanish ones.

**Licence.** The same as `hanami` (table above): the Team L❤VE Voicebank License and Lotte V's Terms of Use allow any creative use, commercial included, with credit, no political, hateful or illegal use; the terms are published in Spanish too ([ToU_ES.md](https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/blob/main/ToU_ES.md), a machine translation; the English text rules). The dictionaries are MIT (`__License/LICENSE_dictionaries.txt`). Credit line: the `hanami` one. Fit for CC BY tracks under the same conditions as the English voice.

**Pronunciation, measured** (`examples/vocals/svs/spanish.py`; five lines, 92 bpm, E4-B4, dry; Whisper small, multilingual, forced to Spanish for word accuracy, and once with language detection; results in `examples/vocals/svs/spanish.json`, auditions `voices/hanami-es.mp3`, `voices/hanami-es-soft.mp3`):

| voice | word accuracy | heard as Spanish | the only miss |
|---|---|---|---|
| `hanami-es` | **96%** (27/28 words) | 5 of 5 lines (p 0.40-0.97) | "guardo" heard as "cuarto" |
| `hanami-es-soft` | **96%** (27/28) | 4 of 5 (one line as Italian, p 0.41) | "guardo" heard as "cuarto" |
| control: `hanami` with the English path (cmudict) | 4% | 0 of 5 | most words sung as "ah" ("Cut up all abroad to number") |

Lines: "cada palabra lleva tu nombre", "quiero quedarme aquí contigo", "guardo tu voz en el papel", "mi corazón no sabe esperar", "te escribo con la luz de la mañana". Verdict: proper Spanish by machine measure; the accent still needs the owner's ear (and ideally a native speaker's). A word-initial voiced stop before a glide ("gu-") can be heard voiceless; prefer other words on exposed notes or check them.

**Searched for other Spanish DiffSinger voices (2026-11-24): none usable.** Web searches (English and Spanish) for Spanish DiffSinger voicebanks, multilingual banks and OpenUtau Spanish phonemizers found no other bank with published terms that allow commercial use: Apollo DS and Aurelian Silva DS (multilingual, no stated terms; see "What is missing" below), community banks on personal sites without terms (the Lenz Blair page on furloidnia.com could not be opened here), and the non-commercial banks already listed below. OpenUtau's Spanish phonemizers are code (the engine has its own G2P), not voices.

## Controls (what they can and can't fake)

These banks expose:
- **vocal modes** (the voice ids above),
- **`gender`** (-1..1, formant shift),
- **`velocity`** (consonant speed),
- **mode mixes** (in voices.json, `"mix": {"Root": 0.5, "Nectar": 0.5}` instead of `"mode"`: the speaker embeddings are interpolated).

They have **no** breathiness, tension, voicing or energy controls: their models were trained without them.

| demo (`examples/vocals/svs/voices/`) | setting | measured | verdict |
|---|---|---|---|
| `ctl-hanami-gender-dark` | gender -0.5 | F1/F2 617/987 -> 498/1009 Hz, tilt -8.6 -> -28.4 dB | darker and rounder, but less intelligible. This is the `hanami-dark` voice. |
| `ctl-hanami-gender-bright` | gender +0.5 | F2 987 -> 1342 Hz | brighter vowels, more youthful |
| `ctl-hanami-male-fake` | gender -1, line an octave down (F#3-B3) | F1 350 Hz, vibrato 47 cents | **Not a male voice.** Below the trained range it wobbles and Whisper hears other words ("I don't know what to do"). Don't use it. |
| `ctl-hanami-velocity-slow` / `-fast` | velocity 0.6 / 1.6 | nearly identical spectra | a small effect on these banks |
| `ctl-hanami-low` / `-high` | the line a fifth down / up | both still transcribe correctly | the usable range edges |
| `ctl-leona-soft-dark` | leona-soft, gender -0.5 | tilt -22.9 dB, breath 0.21 | the darkest, breathiest texture available |
| `../choir-vibrato-1` / `../choir-vibrato-0.3` | `svs_vibrato` 1 / 0.3 (engine-side: the pitch model's vibrato scaled inside held notes) | fast pitch movement inside held vowels 22.7 -> 16.0 (0.5) -> 11.7 (0) cents sd; Whisper unchanged | straighter tone for choir textures and doubles (GENERAL.md section 5); blend to be judged by ear |

**For choirs and doubles:** combine voices. Different modes and banks, a third or sixth apart, separate takes (each phrase has its own seeded pitch and noise; `seed` changes them). See `examples/vocals/svs/choir-line-dry.mp3`, which uses Hanami Root + Nectar and LEONA Core + CatNap. A real SATB needs the male voices (`male-light`, `male-deep`: "Male voices" below; not tried as a choir yet).

## Romanian (searched and tested 2026-11-24): no voice

No DiffSinger bank sings Romanian, and the catalogue's banks have no Romanian data. A phoneme-mapping experiment (Hanami steered into Romanian with phonemes from its other languages: `examples/vocals/svs/romanian.py`, audition `romanian-hanami-experiment.mp3`) reached 0.90 character accuracy and 48% word accuracy with Whisper forced to Romanian (control through the Spanish G2P: 0.85 and 51%), and Whisper heard Romanian on 1 of 5 lines: partly intelligible, not proper Romanian, and Whisper can't judge ă/î. It is not wired into the engine. Details and sources: [languages/ro.md](languages/ro.md).

## Male voices (`male-light`, `male-deep`; searched, installed and measured 2026-11-25)

**Status: wired and measured, waiting for the owner.** Two decisions are his: whether they sound right (auditions below), and whether the prompt singers are acceptable (see "The open point"). Until then the engine prints a note when one of them is used, and they stay out of released tracks.

**What they are.** Not DiffSinger banks. [SoulX-Singer](https://github.com/Soul-AILab/SoulX-Singer) (Soul AI Lab, 2026) is a zero-shot singing synthesizer: it gets the words, the notes and a short recording of a singer (the "prompt"), and sings the line in that singer's timbre. The engine drives it like a bank (`engine/svs_soulx.py`: words through CMUdict, one or more notes per word, seeded, phrase-cached). The two voices are two prompts, six seconds each of "Row, row, row your boat" sung straight by two male singers of [VocalSet](https://zenodo.org/records/1193957) (`engine/soulx_prompts.json` holds the cuts and their hand-aligned scores; the audio is cut from the archive at setup and never committed). English only: the model also sings Mandarin and Cantonese, and no Spanish.

**Licence.**

| part | licence and terms | fits CC BY 4.0 tracks? |
|---|---|---|
| SoulX-Singer, code and weights | Apache 2.0 for both ("Researchers and developers are free to use the codes and model weights", README and the Hugging Face model card). Its usage disclaimer asks users to respect "intellectual property, privacy, and personal consent" and not to "impersonate individuals without authorization or to create deceptive audio". No clause on AI-generated music, commercial use or political subjects. Its vocoder is inside the weights (no Potluck, so no DiffSinger-only clause). | yes |
| VocalSet 1.0 (Wilkins, Seetharaman, Wahl, Pardo, ISMIR 2018) | CC BY 4.0 on Zenodo: any use, commercial included, with attribution. 20 professional singers recorded for the dataset, anonymous (the archive has `male1`-`male11` and `female1`-`female9`; its description counts 9 male and 11 female). | yes for the recordings; see the open point |

Credit line: *Vocals: SoulX-Singer (Soul AI Lab, Apache 2.0, https://github.com/Soul-AILab/SoulX-Singer), voice from a singer of VocalSet (Wilkins, Seetharaman, Wahl, Pardo 2018, https://zenodo.org/records/1193957, CC BY 4.0)*.

**The open point (for the owner).** The licences are clean; consent is thinner than for Hanami. (1) CC BY covers the VocalSet recordings, not the singers' rights in their own voices, and they recorded for singing research, not to have their timbre continued by a model. They are anonymous and the tracks don't present anyone, so this is not impersonation in the disclaimer's sense, but nobody asked them. (2) SoulX-Singer's training data is "more than 42,000 hours of vocal data" with no source given (paper abstract): the weights are Apache 2.0, the data behind them is undisclosed. Lotte V's banks are consented recordings with a named author; these are not. The clean way out of (1) is a prompt whose singer agreed: six seconds of the owner or any consenting singer, sung dry with known words, added to `soulx_prompts.json` (a `notes` table like the two there); the voice then sounds like that person. Nothing fixes (2) except another model.

**Measured** (`examples/vocals/svs/male.py`; the catalogue line an octave down, F#3-B3, dry, tuned; `voices/male.json` has everything):

| id | sound (tags) | suits | bad at | tilt dB | breath | F1/F2 Hz | vib | pitch off, cents | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| `male-light` | male, light, open, clear; a trained singer (tenor or high baritone) | sincere, hopeful, tender; pop rock, folk, ballad, hooks and calls, choir tenor | grit and shouting; air (nothing above 12 kHz); tight rhythmic lines | -13.9 | 0.11 | 714/1215 | 22 | 2.0 | correct |
| `male-deep` | male, dark, round, full (baritone or bass-baritone) | solemn, warm, grave; folk, ballad, choir bass, cinematic, low hooks | bright leads; the same limits | -13.5 | 0.08 | 577/952 | 18 | 7.3 | correct |
| reference: `hanami` at F#4-B4 | | | | -8.6 | 0.06 | 617/987 | 32 | 2.8 | correct |

- **Range:** B2-E3 (`ctl-male-*-low`), F#3-B3 and B3-E4 (`ctl-male-*-high`) all transcribe correctly on both voices (pitch 3-8 cents off). Write B2-E4; the engine warns outside A2-F4. Not tested beyond.
- **Pitch needs the second pass.** Sung once, the model is 22 cents off on average and up to 63 sharp on the first note (both voices). With `tune` 1 (the default) a phrase is sung twice: the first pass gives a natural curve, each note is moved so that its median sits on the written pitch, the second pass follows it. Result 2-7 cents, the same class as Hanami (2.8).
- **In a mix** (the line over electric piano, bass and drums through the standing chain of MIXING.md section 2, quick master; `voices/male-light-mix.mp3`, `male-deep-mix.mp3`): at 1 LU under the band Whisper reads 6 of 6 words for both voices and for `hanami` in the same mix. In a first run with the vocal about 9 LU under the band and pushed hard into the compressor (a gain-staging mistake in the script, since fixed; noted in `male.json`), `male-light` and `hanami` still read 6 of 6 and `male-deep` 4 of 6 ("love and love"): one observation that the dark voice loses words first, as `hanami-dark` does.
- **Timing is looser than Hanami's, and not measured well.** The fastest level rise near each note start lies within 7 ms of the grid for Hanami's notes 2-6, and scatters by 75-100 ms (sd) for the male voices. The detector is crude (words that start with a vowel or a glide have no sharp rise), but the model does place syllables itself: there is no phoneme timing to set. Use these voices for held lines, calls, refrain fragments and choir parts; judge a rhythmic hook by ear before trusting it.
- **Band-limited:** the model works at 24 kHz, so there is nothing above 12 kHz (-65 dB against -41 dB for Hanami). A male voice has little up there; don't try to add air with a shelf.
- **Cost:** about 100 s for a new 6 s phrase on 2 CPU threads (75 s with `svs_tune` 0), cached afterwards; a `double` is a second phrase. 8 / 16 / 32 steps: 65 / 99 / 183 s, all three correct and 2-5 cents off, so 16 stays. About 5 GB of RAM while the model is loaded (a 2.8 GB checkpoint): one render at a time on this machine.
- **Controls:** `seed`, `double`, `svs_steps`, `svs_tune`. No `gender`, `velocity`, `inhale`, `svs_vibrato`, `lang`.
- **SATB** becomes possible: Hanami and LEONA for soprano and alto, `male-light` for tenor, `male-deep` for bass. Not tried yet; the choir rules in MIXING.md section 3 apply, and the two models' vibrato and timing differ, which a choir tolerates better than a duet.

**Install** (never in git; about 2.9 GB under `~/.cache/spectre/svs/soulx/`): `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`, `pip install omegaconf`, then `python3 engine/svs_soulx.py setup` (clones SoulX-Singer at a pinned commit, downloads `model.pt`, cuts the two prompts out of VocalSet by range requests). SoulX's own requirements pin `transformers` 4.41, which did not install here (its `tokenizers` version does not build on Python 3.13); the engine supplies the two classes it needs instead, checked by loading the weights strictly and by Whisper reading the repository's own example.

### Every candidate found (2026-11-25)

The DiffSinger wiki (diffsinger.miraheze.org) and the UTAU wikis could not be opened from here (bot check), so the community's own lists were not read: banks were found through web, GitHub and Hugging Face searches and through projects that use them. A bank announced only on Discord would be missed.

| candidate | what | licence and terms | verdict |
|---|---|---|---|
| **SoulX-Singer** + VocalSet prompts | zero-shot singing model, English / Mandarin / Cantonese | Apache 2.0 (code, weights); prompts CC BY 4.0 | **installed** (above) |
| SoulX-Singer-SVC (same repository) | converts a sung line to the prompt's timbre, any language | Apache 2.0 | not tested (another 2.8 GB plus a Whisper encoder). The route to a male Spanish line: `hanami-es` converted. The result would still carry Lotte V's terms (no political use) |
| TIGER v102 (tigermeat), DiffSinger | male, English | CC BY-NC-ND 4.0 + Commons Clause. "Commercial usage is not allowed without purchase of a license from the rights holder"; a cheaper licence exists for charity. Contact in the bank's LICENSE.md: tora@tora-ouji.com | **ask** (below) |
| Keiro Revenant, Liam Thorne, Albus Korde (LUNAI Project), DiffSinger | tenor, baritone/bass, tenor; English | CC BY-NC-SA 4.0 with LUNAI's terms: commercial use needs their written permission, and the audio may not train other voice models (as reported by two projects that use them, [sjespersen/singer](https://github.com/sjespersen/singer) and [taygetea/etudes](https://github.com/taygetea/etudes); LUNAI's own text was not read) | ask |
| Aurelian Silva DS (AlexFloareaVT), DiffSinger | young male; English, Japanese, Chinese, Korean, French, Spanish, Thai | still no licence or terms in the [repository](https://github.com/AlexFloareaVT/Aurelian_DS); vocoder tgm_hifigan v107 by tigermeat; third-party datasets credited | ask (GitHub issue) |
| Apollo DS 1.0 (KAISKE), DiffSinger | baritone; Portuguese, Japanese, English recorded, Spanish and four more by cross-language | no terms on its [page](https://sites.google.com/view/cabaretike/downloads/apollo-diffsinger); Google Drive release | ask (only social links given) |
| Nishiren Gard (Gardanana), DiffSinger | contralto with hard modes | commercial use by approval; forbids "unethically AI generated ... music", political and religious content | no |
| Miyo, No.7, other community banks | various | non-commercial | no |
| NNSVS / ENUNU banks | | the code is MIT; no English male bank with published commercial terms was found | none found |
| VocalRender (pymaster17) | score to singing, 48 kHz, prompt voice | code Apache 2.0, no licence stated for the weights; trained on OpenSinger, M4Singer, GTSinger (non-commercial datasets); needs a CUDA GPU, 9.5 GB checkpoints | no |
| YingMusic-Singer-Plus (ASLP-lab) | Chinese and English; the melody comes from a sung reference clip, not from notes | CC BY 4.0 | doesn't sing from notes; not tested |
| TCSinger, TCSinger 2 | zero-shot, multilingual | code MIT; no checkpoints published (train your own, on GTSinger: non-commercial) | no |
| VISinger2 | | no licence file, no English weights | no |
| DiffRhythm, YuE (Apache 2.0), ACE-Step 1.5 (MIT) | whole songs from a text prompt | permissive | not a singing voice from notes; against the project's principle (no audio from a prompt) |
| Seed-VC (GPL-3.0, code and weights) | zero-shot singing voice conversion, 44.1 kHz | GPL covers the tool, not its output | a second conversion route; not tested |
| RVC (MIT; base model trained on VCTK), so-vits-svc (AGPL), DDSP-SVC (MIT) | voice conversion trained per target voice | permissive code | need training on the target (minutes of data, a GPU in practice) |
| OpenVoice V2, FreeVC, kNN-VC (all MIT) | zero-shot conversion built for speech | permissive | not tested on singing |

### If these two are not good enough: the options and their cost

1. **Another prompt** (free, about an hour): a different VocalSet singer (11 male folders; `male1`, `male2` and `male4` have low-noise "straight" takes), or a consenting singer's own six seconds. Changes the timbre and removes the consent question, not the model's limits (24 kHz, loose timing, 100 s a phrase).
2. **Ask an author for a licence.** TIGER is the only male English bank whose author offers one: write to tigermeat (address above), say what Spectre is (AI-produced instrumental tracks released under CC BY 4.0, the voice as short hooks and choir parts, credit given), and ask (a) the price of a commercial licence, (b) whether it can cover tracks that others may reuse commercially under CC BY, which is the hard part: his licence is no-derivatives and non-commercial by default, and (c) his view on AI-made music, since his licences speak of "ethical collection of data". LUNAI (three male voices) gives written permission case by case; Aurelian's and Apollo's authors would first have to state any terms at all. A DiffSinger bank would bring what SoulX lacks: 44.1 kHz, exact timing, real time on CPU, the same code path as Hanami (TIGER already renders here, for comparison only: `examples/vocals/svs/tiger-line-dry.mp3`).
3. **Train a bank.** DiffSinger needs 1-2 h of clean, labelled singing by one singer and a GPU (roughly a day or two on one 12-24 GB card for the acoustic and variance models; an estimate, not measured); this machine has 2 CPU threads and no GPU, so not here. No open dataset has that for a male English singer: VocalSet is CC BY but mostly vowels, scales and three short songs; GTSinger, M4Singer, OpenSinger, NUS-48E are non-commercial. So training means recording someone (Lotte V's [public English corpus](https://github.com/lottev1991/Project-AIdol-Public-English-Dataset), CC BY-SA, shows what a recording script looks like), labelling, and renting a GPU: days of work, and the singer's written consent.
4. **Conversion** of a clean female line (SoulX-Singer-SVC or Seed-VC onto a VocalSet or consenting male timbre): keeps Hanami's timing and languages (Spanish), adds the converter's artefacts and keeps Lotte V's terms. Untested; half a day.

## What is missing: hard voices, and a male DiffSinger bank (searched 2026-11-24)

No licence-clean English male DiffSinger voicebank was found (the 2026-11-25 search above found none either; the male voices come from another model). Every male or hard DiffSinger voice found fails on terms or unknown status:

| bank | voice | why not |
|---|---|---|
| TIGER (tigermeat) | male, English | CC BY-NC-ND + Commons Clause: commercial use needs a paid licence; CC BY tracks can be reused commercially by others |
| Nishiren Gard (Gardanana) | contralto with Power and Screamo modes, tension/breathiness controls (the hardest range found) | commercial use needs individual approval; its terms forbid use with "unethically AI generated ... music" and political or religious content |
| Aurelian Silva DS (AlexFloareaVT) | young male, British | no terms of use published (so no licence); its vocoder is fine-tuned on mixed data |
| Apollo DS (KAISKE) | male baritone, English among its languages | Google Drive release with no stated terms |
| Albus Korde (LUNAI), Miyo, No.7 (SEVEN) | various | non-commercial |

Options:
1. Ask a voicebank author for permission (TIGER sells commercial licences; Gardanana approves case by case, but the AI-music clause probably rules Spectre out).
2. Search again (new banks appear often; other singing models count too, if they run locally and their terms fit CC BY tracks).
3. Train a male bank from licensed singing (DiffSinger needs about 1-2 h of clean data and a GPU).

**Male voices:** `male-light` and `male-deep` ("Male voices" above), waiting for the owner's verdict. Until he approves them, write male parts for an instrument or leave them out. There is still no hard, gritty or shouting voice of either sex.
