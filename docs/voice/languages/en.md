# Voice: English

The English profile (standing rule 10). General findings and their sources are in [../GENERAL.md](../GENERAL.md); the voices in [../VOICES.md](../VOICES.md). Researched 2026-11-24 (queue item 5b).

## The voices that sing it
- **`svs`:** every catalogue voice sings English (Hanami: about 2 h of English data; LEONA likewise). Words are read from the bank's English dictionaries (`dsdict-en*.yaml`, ARPAbet), then CMUdict (`pip install cmudict`); a word in neither is sung as "ah" with a warning (respell it). **Stress digits are dropped**: DiffSinger's English phoneme set has no stress, so the notes alone make it (below).

## Rhythm and stress
- **Stress-timed:** English has a small vocalic share and variable consonant intervals (Ramus, Nespor & Mehler 1999), complex syllables and reduced unstressed vowels (Dauer 1983); duration is a primary cue to stress, to vowel length and to the voicing of a final consonant (a vowel before a voiced coda is longer: "bead" vs "beat"; Klatt 1976, JASA 59, doi:10.1121/1.380986). Spoken, the stressed syllables carry the time and function words pass quickly.
- **In a song, stress goes on the meter:** compound nouns take the stronger beat on their first part (BLACKbird), adjective-noun phrases on the second (black BIRD), following the compound and nuclear stress rules; singers lengthen syllables that carry linguistic or musical accent (Palmer & Kelly 1992, J. Memory and Language 31, doi:10.1016/0749-596X(92)90027-U). Put each content word's stressed syllable on a strong beat or a long note; "a-ROUND" wants its second syllable on the beat, "EV-ery" its first.
- **Function words** (the, a, and, you, of, to) are short and reduced in speech: give them 8ths and weak positions. On their own long note they sound read, not sung.
- **Unstressed vowels reduce to schwa** in speech ("a-BOUT", "TO-day" with /ə/); singers keep that reduction on short notes but often sing a fuller vowel on a long one. CMUdict writes most reduced vowels as `ah` (with stress 0), and the svs voice sings what the dictionary gives: if a long unstressed note sounds lazy, respell the syllable with a full vowel.
- **Phrase-final lengthening** falls on the rhyme of the last syllable before a boundary, graded by the boundary's strength (Wightman et al. 1992, JASA 91, doi:10.1121/1.402450), and can reach a phrase-final word's stressed syllable (Turk & Shattuck-Hufnagel 2007). In a line over a band, write it in the notes: the last stressed syllable on the longest note, then a rest.

## Vowels and consonants in singing
- **Diphthongs** (ay "high", aw "round", ey "stay", ow "go", oy): hold the first element and move to the second at the end of the note (GENERAL.md "Sustaining"). DiffSinger treats ARPAbet diphthongs as single phonemes whose timing it learned from the singer.
- **R-coloured vowels** ("her", "bird": `er`; "here", "are": vowel plus `r`): on a long note the r colour is better at the end than throughout; open the vowel first ("ah-r" for "are").
- **High notes:** above about C5, F0 passes the first formant of /i/ and /u/ and the vowels converge toward /a/-like ones (Joliveau, Smith & Wolfe 2004; Hollien et al. 2000): put "high", "are", "go", "ride" (open vowels) on the top notes, and "see", "you", "blue" lower.
- **Flapping:** American English speech flaps /t/ and /d/ between vowels ("better", "city"); CMUdict writes them as plain T and D, so the svs voice sings a crisper /t/ than a speaker would. That's closer to sung diction anyway; respell ("bedder") only for a casual effect.
- **Vowel-initial words** after a pause start with a soft glottal onset in careful speech; in a phrase they link to the previous word's final consonant (below), which carries the rhythm.
- **Final consonants:** in choir textures coda plosives (/b d g p/) and liquids are the most confused sounds (Condit-Schultz & Huron 2017, Journal of Voice 31, doi:10.1016/j.jvoice.2016.02.011). For a several-voice word, prefer endings in a vowel or a nasal ("home", "on", "go"); keep "round" or "hold" on a single voice.

## Linking (connected speech)
- A final consonant becomes the onset of a following vowel-initial word ("round-and": the /d/ release starts "and"; "hold on": the /l/ and /d/ lead into "on"). The svs model links words in a phrase by itself (a rest of more than about 12% of the note's slot starts a new phrase and breaks the link).

## Writing English lines for Spectre (practical)
- Short lines, one image, concrete words; the voice is an instrument (standing rule 14).
- One syllable per note; hyphenate multi-syllable words (`a-round`, `ev-ery-thing`), `_` for a melisma.
- Stressed syllables on strong beats or long notes; function words on 8ths; never 16ths for words.
- Open vowels on long and high notes; important words below about C5; endings in vowels or nasals for choir words.
- Check the line with Whisper (small.en) dry and in the mix (examples/vocals/svs/blend.py shows how): about 70% of words is what listeners get from commercial songs on one hearing (Condit-Schultz & Huron 2015), so aim for the hook's key words, not every word.

## Still open
- A meter/stress warning in the engine (GENERAL.md section 5, item 5).
- British vs American vowels on the svs voices (the banks' English is American-leaning; untested).
- Human pop-singing timing against a band (GENERAL.md, "Timing").
