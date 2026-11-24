# Voice: English

The English profile (standing rule 10). General findings and their sources are in [../GENERAL.md](../GENERAL.md); the voices in [../VOICES.md](../VOICES.md). Researched 2026-11-24 (queue item 5b), on top of the first pass written while fixing the `tts` joins.

## The voices that sing it
- **`svs` (main):** every catalogue voice sings English (Hanami: about 2 h of English data; LEONA likewise). Words are read from the bank's English dictionaries (`dsdict-en*.yaml`, ARPAbet), then CMUdict (`pip install cmudict`); a word in neither is sung as "ah" with a warning (respell it). **Stress digits are dropped**: DiffSinger's English phoneme set has no stress, so the notes alone make it (below).
- **`tts`:** Kokoro v1.0 (Apache 2.0), `af_heart` (female, default), `am_michael` (male), more in docs/MANUAL.md; Kokoro phonemizes with eSpeak NG (US English; voices starting with `b` speak British English). The male voices and tracks with a political subject use this path.

## Rhythm and stress
- **Stress-timed:** English has a small vocalic share and variable consonant intervals (Ramus, Nespor & Mehler 1999), complex syllables and reduced unstressed vowels (Dauer 1983); duration is a primary cue to stress, to vowel length and to the voicing of a final consonant (a vowel before a voiced coda is longer: "bead" vs "beat"; Klatt 1976, JASA 59, doi:10.1121/1.380986). Spoken, the stressed syllables carry the time and function words pass quickly.
- **In a song, stress goes on the meter:** compound nouns take the stronger beat on their first part (BLACKbird), adjective-noun phrases on the second (black BIRD), following the compound and nuclear stress rules; singers lengthen syllables that carry linguistic or musical accent (Palmer & Kelly 1992, J. Memory and Language 31, doi:10.1016/0749-596X(92)90027-U). Put each content word's stressed syllable on a strong beat or a long note; "a-ROUND" wants its second syllable on the beat, "EV-ery" its first.
- **Function words** (the, a, and, you, of, to) are short and reduced in speech ("and" with a 35 ms vowel, measured in Kokoro's phrase): give them 8ths and weak positions. On their own long note they sound read, not sung; the `tts` core stretch holds their vowel without slowing their transitions.
- **Unstressed vowels reduce to schwa** in speech ("a-BOUT", "TO-day" with /ə/); singers keep that reduction on short notes but often sing a fuller vowel on a long one. CMUdict writes most reduced vowels as `ah` (with stress 0), and the svs voice sings what the dictionary gives: if a long unstressed note sounds lazy, respell the syllable with a full vowel.
- **Phrase-final lengthening** falls on the rhyme of the last syllable before a boundary, graded by the boundary's strength (Wightman et al. 1992, JASA 91, doi:10.1121/1.402450), and can reach a phrase-final word's stressed syllable (Turk & Shattuck-Hufnagel 2007). In a line over a band, write it in the notes: the last stressed syllable on the longest note, then a rest.

## Vowels and consonants in singing
- **Diphthongs** (ay "high", aw "round", ey "stay", ow "go", oy): hold the first element and move to the second at the end of the note (GENERAL.md "Sustaining"). DiffSinger treats ARPAbet diphthongs as single phonemes whose timing it learned from the singer; the `tts` path holds the core of the vowel (`stretch: "core"`, `linger`).
- **R-coloured vowels** ("her", "bird": `er`; "here", "are": vowel plus `r`): on a long note the r colour is better at the end than throughout; open the vowel first ("ah-r" for "are"). Words ending in r keep 120 ms of their spoken tail on the `tts` path.
- **High notes:** above about C5, F0 passes the first formant of /i/ and /u/ and the vowels converge toward /a/-like ones (Joliveau, Smith & Wolfe 2004; Hollien et al. 2000): put "high", "are", "go", "ride" (open vowels) on the top notes, and "see", "you", "blue" lower.
- **Flapping:** American English speech flaps /t/ and /d/ between vowels ("better", "city"); CMUdict writes them as plain T and D, so the svs voice sings a crisper /t/ than a speaker would. That's closer to sung diction anyway; respell ("bedder") only for a casual effect.
- **Vowel-initial words** after a pause start with a soft glottal onset in careful speech; in a phrase they link to the previous word's final consonant (below), which carries the rhythm: in the timing analysis their "onset" is that linking consonant.
- **Final consonants:** in choir textures coda plosives (/b d g p/) and liquids are the most confused sounds (Condit-Schultz & Huron 2017, Journal of Voice 31, doi:10.1016/j.jvoice.2016.02.011). For a several-voice word, prefer endings in a vowel or a nasal ("home", "on", "go"); keep "round" or "hold" on a single voice. Final voiced stops end in a long aspirated burst when Kokoro speaks a word alone; the `tts` engine keeps them voiced with a short soft release ("round", not "rount").

## Linking (connected speech)
- A final consonant becomes the onset of a following vowel-initial word ("round-and": the /d/ release starts "and"; "hold on": /l/ 20 ms, /d/ closure 10 ms, release 15 ms, then the vowel; measured in Kokoro's phrase). `tts` phrase mode keeps these links and `keep_joins` their spoken lengths; the svs model links words in a phrase by itself (a rest of more than about 12% of the note's slot starts a new phrase and breaks the link).

## What Kokoro's stress does sung (measured on the "Here You Are" chorus)
- Kokoro puts phrase stress where English speech does: content words get the pitch accent and the bright, high-energy spectrum (the first "round" of "round and round": +3.1 semitones; the second, phrase-final one: 4 dB more 2-8 kHz energy). Sung, that pattern fights the melody; `prosody` (0.7) evens out the tilt and onset force (GENERAL.md section 5).
- Speaking rate `tts_speed` 0.9 gives about 3-4.5 syllables a second ("here you are" 660 ms, "and you stay on the ride" 1085 ms); slower speech mostly lengthens consonants.

## Writing English lines for Spectre (practical)
- Short lines, one image, concrete words; the voice is an instrument (standing rule 14).
- One syllable per note; hyphenate multi-syllable words (`a-round`, `ev-ery-thing`), `_` for a melisma.
- Stressed syllables on strong beats or long notes; function words on 8ths; never 16ths for words.
- Open vowels on long and high notes; important words below about C5; endings in vowels or nasals for choir words.
- Check the line with Whisper (small.en) dry and in the mix (examples/vocals/svs/blend.py shows how): about 70% of words is what listeners get from commercial songs on one hearing (Condit-Schultz & Huron 2015), so aim for the hook's key words, not every word.

## Still open
- A meter/stress warning in the engine (GENERAL.md section 6, item 6).
- British vs American vowels on the svs voices (the banks' English is American-leaning; untested).
- Human pop-singing timing against a band (GENERAL.md, "Timing").
