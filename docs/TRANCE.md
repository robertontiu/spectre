# Trance for Spectre: a working brief

For sessions that make trance (uplifting, progressive, euphoric). A vocabulary, not a rulebook. Spectre has so far made only trap-family beats: trance is a different body. It runs on a straight four-on-the-floor pulse, the bass lives *between* the kicks, and the emotion comes from long-form tension and release instead of a loop.

## The tradition and the references
- Trance grew out of early-1990s European club music (Germany above all), adding melody, harmony, emotional highs and lows, long tracks and prominent breakdowns to house. Influences: UK progressive house, Goa, sci-fi soundtracks, Moroder/Jarre synth music, Italo-disco. It was dance music's dominant genre in the late 1990s, burned out in the early 2000s, fed the 2010s EDM boom and is having a UK resurgence now.
- **Uplifting trance** (also "epic" or "euphoric") got its name around 1996, after the "rush" listeners describe. It is happier than Goa and darker trance, rests on longer chord progressions, and draws on classical and film music.
- **Classic references:** Paul van Dyk, Ferry Corsten (System F), Tiësto, Armin van Buuren, Robert Miles, ATB, Paul Oakenfold, Sasha & Digweed.
- **Modern references:** Above & Beyond, Aly & Fila, Gareth Emery, Bryan Kearney, Sean Tyas, John O'Callaghan, Andy Blueman, Super8 & Tab; the UK resurgence: Ben Hemsley, Hannah Laing, Ewan McVicar.
- Trance is mostly instrumental; vocals are used sparingly.

## Tempo and groove (engine names in brackets)
- **Tempo:** 136-140 bpm is the core (uplifting 138-142, vocal 136-140, progressive 128-134, tech 140-145; hard trance 148+ is a different, harder body). Straight 16ths: `"swing": 0.5`, `humanize_ms` 0-1 on the drums.
- **Kick on every beat**, short and punchy (`clubkick`). Big reverbed kicks are for sparse moments only.
- **Clap or snare on 2 and 4** (`clap`, `snare`), with a 0.5-1.5 s reverb tail.
- **Open hat on the offbeat 8ths** (`openhat`, `"..x...x...x...x."`), 16th closed hats or shakers for drive (`hat`). In builds, add 16th hats.
- Keep percussion simple; strip the beat back where bass and lead are busy.

## Bass: offbeat and rolling
- **Offbeat bass:** one note on the "and" between kicks, `"..x...x...x...x."`. The classic progressive and uplifting pulse.
- **Rolling bass:** three 16ths between kicks, `".xxx.xxx.xxx.xxx"` (kick-bass-bass-bass). Drives harder; it suits drops and tech-leaning tracks. Reggae-style rolling lines are a variation.
- Low-pass the bass (about 500 Hz) so it doesn't clash with the kick's mids; boost 60-80 Hz, cut around 200 Hz. A sine sub with short attack and release reinforces it.
- **Sidechain** the bass, chords and pads to the kick: attack about 1 ms, release 80-120 ms. The pump is part of the sound, not just a mix fix.
- Engine: `trancebass` with chord stabs and the `root` voicing, e.g. `{"chords": "Am:16 F:16 C:16 G:16", "style": "stabs", "rhythm": ".xxx.xxx.xxx.xxx", "voicing": "root", "register": "A1", "stab_len": 1}`, plus `"sidechain": {"source": "kick", "depth": 0.85, "release_ms": 90}`.

## Leads, chords, plucks, gates, pads
- **Supersaw:** Roland's JP-8000 (1996) supersaw, seven detuned saws, became the genre-defining trance sound. In anthem trance a supersaw lead carries the hook. Use about 7 voices and 15-25 cents of detune (under 10 sounds thin, over 30 out of tune), high-pass chords around 200 Hz, and keep them wide. Engine: `supersaw` (stereo; uses the JP-8000's uneven detune pattern).
- **Plucks and arps:** a pluck has 0 attack and 100-150 ms decay with no sustain. Arps run 16ths through each chord for 2-4 bars. Engine: `supersaw` with `sustain_level` 0, short `decay`, `env` and `fdecay`, played as a chord `arp`.
- **Trance gate:** sustained pads or chords chopped into a rhythmic 16th pattern. Longer release means a smoother, more organic gate; delay and reverb suit gated parts. Engine: `gate` fx with a step pattern.
- **Pads:** attack 0.5-2 s, release 2-4 s; boost gently somewhere in 200 Hz-1 kHz. Strings, choirs and voices are the classic "wash" layer. Engine: `supersaw` with long attack, `pad`, `strings`, `choir`.
- **Piano** riffs, with delay and reverb, are classic breakdown material (`piano`).

## Harmony
- **Minor keys,** most often A minor, then D, F, G, B and E minor.
- **Progressions:** i-VI-III-VII (Am-F-C-G) is the uplifting workhorse. Others: i-VI-i-V with a major V (Am-F-Am-E) for the emotional cadence, i-iv-VII-III (Am-Dm-G-C), and VI-III-VII-i (F-C-G-Am) for the breakdown uplift.
- **Lift:** major chords carry the joy, and the balance of major and minor sets how happy or sad a progression feels. Suspended chords resolving (Esus4 to E, sus2 colour on the VI) give the yearning-then-arriving feeling. Changing key by 3 or 5 semitones after a long build gives a new direction.
- **Complexity sweet spot:** in a study where fans rated generated uplifting-trance progressions, enjoyment rose with harmonic complexity up to a point, then fell. Very simple progressions were disliked; "awkward" changes kill the dancefloor. Trance clichés are part of its fabric: predictability lets listeners get lost.

## Arrangement and the radio edit
- Club ("extended") mixes run 7-9 minutes, with 16-32-bar intros and outros for DJs. A typical extended layout: intro 16-32, theme 16-32, build 8-16, first drop 16-32, breakdown 32-64, build 8-16, main drop 32-64, outro 16-32. DJs cut tracks to 4-5 minutes; radio edits run about 3-4 minutes.
- **Spectre's radio-edit shape** (2:30-3:30; at 138 bpm a bar is 1.74 s, so 96 bars is about 2:47): intro 8 (kick, bass and a filtered hint of the theme), first theme or drop 16, **breakdown 16-24** (no kick: pads, piano or the vocal-like lead, the theme stated slowly), **build 8** (snare roll 4ths, 8ths, 16ths, then 32nds; riser; high-pass sweep on the music; pitch rise; one beat of silence), **release/main drop 16-32** (full lead and chords, everything back), outro 8.
- Tease the breakdown: strip to strings, effects and the "vocal", then bring parts back every couple of bars. Introduce new layers with an incidental (offbeat snare, reverse crash, filter sweep). Work in 16-bar blocks.

## Mixing and loudness
- **Kick and bass carve-up:** the offbeat placement is the first carve; the sidechain is the second. Keep everything below about 250 Hz narrow and the mids and highs wide.
- Supersaws high-passed (about 200 Hz) and wide; long, cavernous reverbs on leads and pads; snare and clap tails 0.5-1.5 s. Delays at 138 bpm: quarter 435 ms, dotted 8th 326 ms (`"beats": 0.75`), 8th 217 ms. Don't overuse delay on cycling arps.
- **Loudness:** club masters run -9 to -7 LUFS, streaming masters -12 to -10. In Spectre: `studio.py master --target trance --lufs -10`. Louder masters hit the true-peak guard and stop gaining loudness.

## The "vocal" role (instrumental)
Trance is mostly instrumental already. **The lead synth is the singer:** the supersaw lead carries the hook and the theme. In the breakdown a wordless vocal-like line can carry the theme slowly before the lead takes it at full power: `vox` (soprano "ah" or "oo", long reverb, glides) or a piano. Keep the theme singable: a short, memorable phrase repeated with small changes, rising at the end of each 8 bars.

## Ecstasy and euphoria: how trance gets there
- **The break routine** (breakdown, build-up, drop) is the engine of euphoria. In a 2019 study of EDM peak experiences, listeners described intense, energising, uplifting and embodied responses, attributed mostly to the drop. Drop sections produced significantly higher skin conductance than the rest of the break routine.
- **Expectation:** pleasure comes from expectations being fulfilled, delayed or violated, which can produce chills and an intense desire to move. The drop should come exactly when the body expects it, but with *more* than expected: the lead an octave up, a sus chord resolving, a new top note, a key change, the kick returning after a beat of silence.
- **The collective moment:** goosebumps and the urge to raise arms come from "planet-sized major chord riffs" and emotive melodies. The breakdown's chord change, where the progression turns from minor weight to a major lift, is the "hands in the air" moment that a crowd shares. Ecstasy here is self-dissolving and communal: being lifted out of yourself together.
- **For an ecstasy brief:** build the release through the arc, not just the drop. The breakdown should feel like holding your breath with everyone; the drop is the exhale. Keep the body (kick, pump, rolling bass) and the sky (supersaw, pads, reverb) both present at the peak.

### Nearest wrong feelings
- **Cheesy:** a stock progression, stock arp, stock riser, everything predictable including the sounds, or "happy" with no shadow. Fix: one unexpected chord colour (sus, add9, a borrowed chord), restraint in the breakdown, a melody with a real shape.
- **Hollow festival EDM:** a big-room drop that is just a kick, a stab and a shout, with no melody or harmony carrying the release; builds that promise and deliver nothing. Ecstasy in trance is melodic and harmonic.
- **Aggressive hard dance:** above 145 bpm, distorted kicks, hammering minor stabs, a rave alarm. That is an attack; ecstasy is open.
- **Chill or ambient:** a breakdown that never returns, no kick release, floating without a body. The rush needs the body back.
- **Melancholy "sad trance":** minor progressions that reach up and never land read as longing (the same trap as session 001). The lift has to arrive.

## Engine mapping
| Role | Engine |
|---|---|
| Kick | `clubkick` (tune 48-55, tail 0.06-0.12) |
| Clap, snare, hats, crash | `clap`, `snare`, `openhat` (offbeat), `hat` (16ths), `crash` / `kitcrash` at the drop |
| Offbeat or rolling bass | `trancebass` + stabs + `"voicing": "root"` + sidechain to the kick |
| Lead, chords, plucks, pads | `supersaw` (stereo); chords with the `gate` fx; plucks with `sustain_level` 0 and `env` |
| Breakdown | `pad`, `strings`, `choir`, `piano`, `vox` |
| Build | snare roll pattern, `"exit": {"riser": 8, "rise": 16}`, `auto` `hpf` sweep, `"cut": {"tracks": "all", "beats": 1}` |
| Master | `--target trance --lufs -10` |

## Sources
- Uplifting trance (Wikipedia): https://en.wikipedia.org/wiki/Uplifting_trance
- Roland JP-8000 and the supersaw (Wikipedia): https://en.wikipedia.org/wiki/Roland_JP-8000 ; A. Szabo (2010), "How to Emulate the Super Saw" (detune offsets used in `supersaw`)
- MusicRadar, 26 trance tips: https://www.musicradar.com/tuition/tech/26-trance-tips-34006
- How to make trance music (BPM, keys, progressions, supersaw settings, arrangement, loudness): https://beatkey.pages.dev/how-to-make-trance-music
- Digital DJ Tips, Everything you wanted to know about trance: https://www.digitaldjtips.com/everything-wanted-to-know-trance/
- MusicRadar, How to use rhythmic sidechain gates: https://www.musicradar.com/tuition/tech/how-to-use-rhythmic-sidechain-gates-588195
- DJ Mag, Why trance works (Herremans, Solarstone, Helstrip, Solberg): https://djmag.com/longreads/why-trance-works
- R. T. Solberg and N. Dibben (2019), "Peak experiences with electronic dance music", Music Perception 36(4): https://eprints.whiterose.ac.uk/id/eprint/145911/
