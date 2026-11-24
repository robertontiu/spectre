# Spectre: the site

The public home of [Spectre](../README.md), an AI beat producer that starts from a feeling and listens by looking. It is a port of the static showcase in [`site/`](../site/) to Next.js: the same ghostly backdrop, the wraith badge and the smoky logotype, and a player with a visualizer, a 10-band equalizer and the playlist. Every track also has its own page and share card.

Next.js 16 (App Router, Turbopack), React 19, TypeScript (strict), Tailwind CSS 4. No UI or animation libraries.

## Run it

Node 20.9 or newer.

```bash
cd site
npm install
npm run dev          # http://localhost:3000
```

`dev` and `build` first run `scripts/sync-tracks.mjs`, which copies each track's master from `../sessions/<id>-*/*-mastered.mp3` to `public/tracks/` (the MP3s are not committed under `site/`).

| Script                                                  | What it does                                                                                                                     |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `npm run dev`                                           | Sync the tracks, start the dev server.                                                                                           |
| `npm run build` / `npm start`                           | Production build (what Vercel runs) and a local production server.                                                               |
| `npm run export`                                        | Fully static site in `out/` (`output: "export"`; nothing here needs a server).                                                   |
| `npm run export:preview`                                | Static home page that works from any sub-path (relative URLs, assets in `out/assets/`); used for the claude.ai artifact preview. |
| `npm run lint` / `npm run typecheck` / `npm run format` | ESLint (create-next-app config), `tsc`, Prettier with Tailwind class sorting.                                                    |

## Add a track

1. Put the master in its session folder as `sessions/NNN-name/<title-slug>-mastered.mp3` (the session delivery procedure already does this).
2. Add a line at the top of [`data/tracks.json`](data/tracks.json) (newest first):

   ```json
   {"id":"007","artist":"Spectre","title":"…","src":"tracks/007-title-slug.mp3","duration":180.0,"bpm":120,"genre":"…","style":"…","feeling":"…","colors":["#…","#…","#…"]},
   ```

   `id` selects the session folder, `src`'s file name is where the MP3 is copied to and also the track's URL (`/track/007-title-slug`), `duration` comes from `ffprobe`, `genre` is the short label shown beside the tempo, and `colors` are 2-3 colours that fit the track (the page mutes them).

3. Run `python3 ../tools/sync_tracks.py` to update the other players (it writes `site/tracks/tracks.json` from this file and copies the masters everywhere), then commit `data/tracks.json`.

## Deploy on Vercel

Create a Vercel project from the GitHub repo with:

- **Root Directory:** `site`
- **Include files outside the root directory in the Build Step:** enabled (it is by default). The prebuild step reads the masters from `../sessions/`, so the build fails with "missing master" if this is off.
- Framework preset Next.js, default build command (`npm run build`) and output. No environment variables and no `vercel.json` are needed.
- Domain: add `spectre.robertontiu.com` and point a `CNAME` for `spectre` at `cname.vercel-dns.com`. Absolute URLs in the metadata, sitemap, share links and OG cards use `https://spectre.robertontiu.com` (`src/lib/site.ts`).

The six masters are about 42 MB; Vercel serves them from `public/tracks/` as static files.

## How it is built

```
data/tracks.json          the canonical track list (newest first)
scripts/                  sync-tracks.mjs (prebuild), preview-export.mjs
src/app/                  layout (metadata, fonts), home page, track/[slug] (page + OG card),
                          robots, sitemap, icons
src/components/
  spectre-page.tsx        the whole page, shared by / and /track/[slug]
  atmosphere/             the fixed background stack (server-rendered) and PaletteCrossfade
  brand/                  badge, logotype + GlitchFrame, GitHub pill
  player/                 store, provider, card, visualizer, now playing + share,
                          seek bar, controls, equalizer, playlist
src/lib/                  Web Audio engine, colours, equalizer presets, palette animator,
                          site URLs, tracks
```

- **Server first.** The page shell, the background stack, the badge and the logotype are server components; client components are the player, the colour crossfade and the logotype's glitch timer.
- **Player state** lives in a small external store (`player-store.ts`) read with `useSyncExternalStore`, so audio events, media keys and the canvases always see the latest state without re-rendering the page. Preferences persist in `localStorage` (`spectre.v1`, the showcase's format).
- **Audio:** `<audio>` → MediaElementSource → preamp → 10 biquads → analyser → volume. The graph starts on the first tap or key press; a track link's autoplay plays the element directly, and if the browser blocks it the play button asks for a tap.
- **Track colours.** The background layers that carry a track's colours are rendered in two palette slots that crossfade by opacity (2 s); they are painted once per track and never repaint mid-glide. Only the player card's accent colours glide through CSS variables.
- **Styling:** Tailwind for layout and type; the atmosphere, logotype, range inputs, sliders and pressed states are plain CSS next to their components (in `@layer components`). Motion is transform and opacity only, never filters or blur, and it all stops under `prefers-reduced-motion`.
- **Fonts:** Syne and Manrope, self-hosted variable fonts from Fontsource (SIL OFL, see `src/fonts/`), with latin-ext loaded only when needed (Latvian, Romanian titles).
