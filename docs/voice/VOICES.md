# Voice catalogue: `singer` `"source": "svs"`

The voices the producer can choose for sung words (docs/MANUAL.md "Voices"). Pick one with `"voice": "<id>"`. The same data is machine-readable in `engine/voices.json`: tags, range, licence and credit. Auditions are in `examples/vocals/svs/voices/<id>.mp3`. Each audition is the same two bars, dry: "here you are, round and round", F#4-B4 at 100 bpm (the male voices an octave lower). `examples/vocals/svs/voices.py` rebuilds the auditions and the measurements (`male.py` for the male voices).

**Voices are instruments** (standing rule 14): short lines, hooks, calls, refrain fragments and choir textures, never a sung song.

## Mixing a voice
Choosing a voice is half of it; the other half is the mix. The principles for every genre, the choir and ensemble research (separate takes, `svs_vibrato`, timing scatter, voice counts, reverb) and the Whisper and loudness checks are in [MIXING.md](MIXING.md). Each genre has a researched starting chain: [caroling](../CAROLING.md#mixing-the-voice-researched-2026-11-24), [trance](../TRANCE.md#mixing-the-voice-researched-2026-11-24), [Latin pop](../LATIN_POP.md#mixing-the-voice-researched-2026-11-24), [pop rock](../POP_ROCK.md#mixing-the-voice-researched-2026-11-24), [hip hop](../HIPHOP.md#mixing-the-voice-researched-2026-11-24), [joc and Romanian folk](../JOC_TIGANESC.md#mixing-the-voice-researched-2026-11-24). Two rules that came out of measurement: words go on the clear voices (`hanami`, `hanami-power`, `hanami-es`), never on `hanami-dark`; and every voice singing the same words starts them together (`push_ms` 0).

## Licences and credit (read before using a voice)

| bank | licence | credit line (put it in the session README's **Credits** and the site notes) |
|---|---|---|
| Hoshino Hanami ~AI❤dol~ v1.0, by Lotte V | Team L❤VE Voicebank License and Terms of Use. Any creative use is allowed, commercial included, without asking. Conditions: credit Lotte V; don't redistribute or sell the files; don't claim the voice as your own; no political, hateful or illegal use. Religious works are allowed without asking as long as they aren't for proselytizing (ToU_EN.md in Lotte V's lottev-voicebank-update-repo, read 2026-11-24): a carol quoted in a secular track is fine. | Vocals: Hoshino Hanami (DiffSinger voicebank by Lotte V, lottev.moe), Potluck Vocoder by tigermeat |
| LEONA -Ubasti- v0.0.1b (beta), by Lotte V | The voicebank is CC BY 4.0, plus the same Terms of Use as Hanami. | Vocals: LEONA (DiffSinger voicebank by Lotte V, lottev.moe, CC BY 4.0), Potluck Vocoder by tigermeat |
| Hanami made male: `hanami-male`, `hanami-male-es` | Hanami's licence and terms, nothing else. Lotte V's licence allows to "create a derivative voice through vocal synthesizer software settings, including for a different character", and her Terms of Use ask that derivatives be "created through settings contained within the synthesis software itself, rather than through pitch-shifting fully mixed songs through audio software" (`Terms of Use.pdf` and `__License/LICENSE_voicebank.txt` in the bank, read 2026-11-25): these voices are exactly that. No political, hateful or illegal use, as for `hanami`. | Hanami's line (above) |
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
| `hanami-male` | Hanami / Root, gender -0.2, sung an octave up and moved down in the synthesizer (`sing_up` 12) | **male**, dark, soft, covered, even; Hanami's vibrato and phrasing | tender, calm, sincere, intimate; ballad, folk, lo-fi, choir tenor and bass, low doubles of a female line | brightness and bite, grit, shouting, a trained male singer's ring | -20.5 | 0.14 | 540/1218 | 33 | correct |
| `hanami-male-es` | as `hanami-male`, **Spanish** (`"lang": "es"`) | male, dark, soft; Latin American Spanish | tender, sincere; Latin pop, bolero and bachata lines, a male answer to `hanami-es` | as above, and a native accent | -18.4 | 0.17 | | 33 | Spanish: 4 of 4 words |
| `leona` | LEONA / Core (beta) | bright, light, youthful, character/cute | playful, cheeky, sunny, excited; anime-style hooks, hyperpop, chiptune, trance | mature, serious or sad lines; natural adult pop | -3.2 | 0.05 | 801/1397 | 18 | correct |
| `leona-power` | LEONA / CatNip (beta) | brightest, hard, edgy | energetic, excited, bratty, triumphant; EDM/trance drops, hyperpop, rock calls | tenderness, warmth | +1.6 | 0.05 | 906/1318 | 18 | slurred ("hear you around") |
| `leona-soft` | LEONA / CatNap (beta) | soft, breathy, airy, dark | wistful, tender, fragile; lo-fi, dream pop, ambient, choir pads | dense mixes, energy | -17.0 | 0.18 | 526/1030 | 33 | slurred ("hear you around") |

**Range.**
- Hanami: the training data sits at G3-D5 (most of it C4-A#4, peak G4; `midi_distribution.jpg` in the bank). Write A3-D5. A fifth lower (B3-E4) and a fifth higher (C#5-F#5) both still transcribe correctly (`ctl-hanami-low`, `ctl-hanami-high`). The engine warns outside G3-F5.
- LEONA: trained together with Hanami's data. The range is assumed to be the same, not measured; the engine warns outside A3-F5.
- Both are female voices. Writing them an octave lower does not make a male voice (`ctl-hanami-male-fake` below). The male voices are `hanami-male` and `hanami-male-es`: write B2-E4; the engine warns outside A2-F4 ("Male voices" below).

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
| `ctl-hanami-male-fake` | gender -1, line an octave down (F#3-B3) | F1 350 Hz, vibrato 47 cents | **Not a male voice.** Below the trained range it wobbles and Whisper hears other words ("I don't know what to do"). Don't use it. What it got wrong, and the setting that works (`hanami-male`: gender -0.2, the octave moved inside the synthesizer): "Male voices" below. |
| `ctl-hanami-velocity-slow` / `-fast` | velocity 0.6 / 1.6 | nearly identical spectra | a small effect on these banks |
| `ctl-hanami-low` / `-high` | the line a fifth down / up | both still transcribe correctly | the usable range edges |
| `ctl-leona-soft-dark` | leona-soft, gender -0.5 | tilt -22.9 dB, breath 0.21 | the darkest, breathiest texture available |
| `../choir-vibrato-1` / `../choir-vibrato-0.3` | `svs_vibrato` 1 / 0.3 (engine-side: the pitch model's vibrato scaled inside held notes) | fast pitch movement inside held vowels 22.7 -> 16.0 (0.5) -> 11.7 (0) cents sd; Whisper unchanged | straighter tone for choir textures and doubles (GENERAL.md section 5); blend to be judged by ear |

**For choirs and doubles:** combine voices. Different modes and banks, a third or sixth apart, separate takes (each phrase has its own seeded pitch and noise; `seed` changes them). See `examples/vocals/svs/choir-line-dry.mp3`, which uses Hanami Root + Nectar and LEONA Core + CatNap. A real SATB takes `hanami-male` for tenor and bass ("Male voices" below; not tried as a choir yet). It shares Hanami's timing and vibrato controls, which a worded choir line needs.

## Romanian: `hanami-ro` (approved by the owner's ear as "good enough", 2026-11-26)

**Status: approved for use** ("good enough", the owner on `examples/vocals/svs/romanian-hanami-experiment.mp3`, 2026-11-26). No DiffSinger bank was trained on Romanian, so this is Hanami (Root) steered into Romanian by a phoneme mapping, now wired into the engine: `"voice": "hanami-ro"`, or `"lang": "ro"` on any Hanami voice (`engine/lang_ro.py`, the mapping of the experiment unchanged). How it was made: Romanian letters go to phonemes Hanami knows from its other languages (Spanish vowels, unaspirated stops `px tx kx`, clear `l1`, tapped `rx`; the German schwa `ax` for ă; the Korean ㅡ vowel `eu` for î/â; Japanese palatalized `ky`/`gy` for ch/gh before e/i; glides for the rising diphthongs, offglides `I1`/`U1` for the falling ones; a final non-syllabic i as `I1`; initial e as [je] in the pronouns and forms of "a fi"). Measured before the verdict (`examples/vocals/svs/romanian.py`, Whisper small forced to Romanian, five lines): 0.90 character accuracy, 48% word accuracy, Romanian detected on 1 of 5 lines; Whisper drops diacritics, so it could not judge ă and î, which is why the owner's ear decided. Expect a foreign accent; write lyrics as docs/voice/languages/ro.md says (hyphenated by syllable, stress on strong beats). Licence: Hanami's (credit Lotte V); **never in a track with a political subject** (Lotte V's terms: for example session 011 and any anthem or protest line).

## Male voices (`hanami-male`, `hanami-male-es`; approved by the owner by ear, 2026-11-25)

**Status: approved** ("it is more clear", 2026-11-25). Write male parts with these two.

**What they are.** Hoshino Hanami made male inside her own synthesizer. Her duration and pitch models sing an octave above the written notes, where the bank was trained; the pitch curve is moved down an octave inside the synthesizer, before the acoustic model and the vocoder, and the bank's own `gender` control is at -0.2. In voices.json that is `"sing_up": 12` on the voice (engine/svs.py). It is the DiffSinger pipeline with two settings changed: real time, 44.1 kHz, bit-for-bit repeatable, every Hanami control still works, Spanish included. Why `ctl-hanami-male-fake` failed and this doesn't: it wrote the line an octave down, so the pitch model worked below its range (wobble, 47 cents), and it set `gender` to -1, which alone loses the words. With the octave moved in the synthesizer, `gender` 0 to -0.4 keeps every word and -0.6 or -1 lose them; the octave alone (`gender` 0) still sounds like a low female voice, so the `gender` setting does the work.

**Licence and credit.** Hanami's, nothing else: the voice is Lotte V's own, given under her terms, and nobody else's voice is involved. Her licence allows to "create a derivative voice through vocal synthesizer software settings, including for a different character", and her Terms of Use ask that derivatives be "created through settings contained within the synthesis software itself, rather than through pitch-shifting fully mixed songs through audio software (e.g. \"pitchloids\" are not allowed)", adding that "formant filter effects applied to the rendered voice during mixing" are allowed (`Terms of Use.pdf` and `__License/LICENSE_voicebank.txt` in the bank, read 2026-11-25). Credit line: Hanami's (table at the top). **No political subject**, as for every Lotte V voice.

**Why not another route.** No licence-clean male DiffSinger bank exists ("What is missing" below); cloning a recorded male singer zero-shot with another model raised consent questions (the singers had not agreed to it); and converting Hanami's phrase to a male speaker's timbre with a voice conversion model was less clear by ear and lost words more often.

**Measured** (`examples/vocals/svs/male.py`; everything in `voices/hanami-male.json`; English: the catalogue line an octave down, F#3-B3; Spanish: "quiero quedarme aquí contigo", E3-B3; dry):

| voice | Whisper | pitch off, cents | tilt dB | breath | F1/F2 Hz | vib | above 12 kHz dB | flutter dB | jitter cents | new phrase |
|---|---|---|---|---|---|---|---|---|---|---|
| `hanami-male` | 6 of 6 | 3.5 | -20.5 | 0.14 | 540/1218 | 33 | -48 | 0.24 | 2.0 | about real time |
| `hanami-male-es` | 4 of 4, heard as Spanish (p 0.93) | 9.1 | -18.4 | 0.17 | | 33 | -46 | 1.13 | 3.0 | about real time |
| reference: `hanami` at F#4-B4 | 6 of 6 | 2.8 | -8.6 | 0.06 | 617/987 | 32 | -41 | 0.34 | 2.3 | about real time |
| reference: `hanami-es` an octave up | 4 of 4 (p 0.97) | 8.3 | -12.0 | 0.06 | | 61 | -43 | 1.42 | 2.8 | about real time |

(*flutter*: the 8-40 Hz part of the level inside held notes; *jitter*: the frame-to-frame pitch step inside held notes; both are artefact proxies, and they sit with Hanami's.)

- **Range:** B2-E3, F#3-B3 and B3-E4 all read 6 of 6, 2.8-4.0 cents off. It darkens downwards (tilt -24 dB at B2-E3, -14 at B3-E4). Write B2-E4; the engine warns outside A2-F4.
- **Timing is Hanami's** by construction: the same duration model with the same input (the onset detector reads 0 ms envelope lag against her own render).
- **Takes:** the audition line with seeds 1-8 (another seed is another performance) reads 6 of 6 words in 6 of 8 takes; the other two are heard as "Hear you around and round", the same sounds cut into other words (`hanami` herself: 8 of 8). Check an exposed line with Whisper and change `seed` if a word blurs. Pitch over the takes: 2.7-5.5 cents off.
- **In a mix** (the line in a small band through the standing chain of MIXING.md section 2, vocal 1 LU under the band, quick master; `voices/hanami-male-mix.mp3`, `hanami-male-es-mix.mp3`): 6 of 6 and 4 of 4, in the mix and alone, as Hanami in the same band.
- **Character:** dark (tilt -20.5 dB against -8.6 for Hanami) and a little breathy: give it the 8 kHz shelf of the standing chain. `gender` -0.3 is brighter (tilt -17.7) and larger and still reads 6 of 6. There is no trained male singer in it: expect a soft, covered low voice, not a tenor's ring; no grit or shouting.
- **Controls:** all of Hanami's (`seed`, `double`, `velocity`, `inhale`, `svs_vibrato`, `lang`, `gender`, phrase fades).
- **Install:** nothing beyond Hanami.

## What is missing: hard voices, and a male DiffSinger bank (searched 2026-11-24 and 2026-11-25)

No licence-clean English male DiffSinger voicebank was found (the male voices are Hanami's: "Male voices" above). Every male or hard DiffSinger voice found fails on terms or unknown status:

| bank | voice | why not |
|---|---|---|
| TIGER (tigermeat) | male, English | CC BY-NC-ND + Commons Clause: commercial use needs a paid licence (contact in the bank's LICENSE.md); CC BY tracks can be reused commercially by others |
| Nishiren Gard (Gardanana) | contralto with Power and Screamo modes, tension/breathiness controls (the hardest range found) | commercial use needs individual approval; its terms forbid use with "unethically AI generated ... music" and political or religious content |
| Aurelian Silva DS (AlexFloareaVT) | young male, British | no terms of use published (so no licence); its vocoder is fine-tuned on mixed data |
| Apollo DS (KAISKE) | male baritone, English among its languages | Google Drive release with no stated terms |
| Keiro Revenant, Liam Thorne, Albus Korde (LUNAI) | tenor, baritone/bass, tenor; English | CC BY-NC-SA with LUNAI's terms: commercial use needs their written permission |
| Miyo, No.7 (SEVEN) | various | non-commercial |

Options:
1. Ask a voicebank author for permission (TIGER sells commercial licences; Gardanana approves case by case, but the AI-music clause probably rules Spectre out).
2. Search again (new banks appear often; other singing models count too, if they run locally and their terms fit CC BY tracks).
3. Train a male bank from licensed singing (DiffSinger needs about 1-2 h of clean data and a GPU).

A trained male singer's voice (a tenor's ring, grit) would need one of these. There is still no hard, gritty or shouting voice of either sex.
