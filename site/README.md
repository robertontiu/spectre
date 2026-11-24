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
  atmosphere/             the fixed background stack: SVG apparition (server-rendered) and
                          AtmosphereField, the canvas planes of mist, fog and track colours
  brand/                  badge, logotype + GlitchFrame, GitHub pill
  player/                 store, provider, card, visualizer, now playing + share,
                          seek bar, controls, equalizer, playlist
src/lib/                  Web Audio engine, colours, equalizer presets, palette animator,
                          site URLs, tracks
```

- **Server first.** The page shell, the apparition, the badge and the logotype are server components; client components are the player, the background field and the logotype's glitch timer.
- **Player state** lives in a small external store (`player-store.ts`) read with `useSyncExternalStore`, so audio events, media keys and the canvases always see the latest state without re-rendering the page. Preferences persist in `localStorage` (`spectre.v1`, the showcase's format).
- **Audio:** `<audio>` → MediaElementSource → preamp → 10 biquads → analyser → volume. The graph is built on the first play, so the EQ and visualizer always apply. Nothing autoplays, not even a track link (it opens on that track, ready to play).
- **Background field.** The mist, fog banks, wisps and the track-coloured field are composited by `AtmosphereField` (`atmosphere/field-scene.ts`) into two canvases, one under the apparition and one over it. Each original CSS layer is pre-rendered once into its own sprite exactly as its gradient (0.5 px per CSS px; track-coloured sprites again only when the colours change), and every frame the sprites are drawn in the original order with the original keyframed drift and opacity, like the browser composited the CSS layers. The canvases are 0.75 px per CSS px (within about 0.7 Mpx each, no CSS blur); if a device cannot hold about 20 fps (canvas drawn without a GPU) they step down, never below 0.4. One loop (`field-renderer.ts`) draws at 30 fps with time-based drift, in a worker on OffscreenCanvases where the browser supports it (otherwise on the page), pauses in hidden tabs, and glides to a new track's colours in OKLab over 2 s. A track change or tab switch creates, hides or repaints no DOM layer. The stack's height is pinned in px (100lvh first), so a phone's address bar never resizes it while scrolling. Until the first frame, CSS layers in the opening track's colours stand in (frozen), so the server-rendered page looks right; under reduced motion the field is static and colour changes take 0.5 s.
- **Track colours in the card.** The card's accents `--c1..3` are `@property`-registered colours, written once per track and transitioned by the browser (1.6 s); the visualizer and EQ canvases glide the same palette in JS (`PaletteAnimator`, no DOM writes). The visualizer paints its own glow, reads no layout in its frame loop (ResizeObserver, IntersectionObserver), caps its backing store at 2x and runs at up to 60 fps (30 on touch screens).
- **Sliders on touch.** The seek and volume sliders are native ranges for keyboard and assistive tech, but a finger only drags them once the gesture is clearly horizontal (a tap still seeks); vertical swipes scroll. An EQ band takes a finger only on its knob after a short rest (the knob glows when armed), otherwise the page scrolls. Mouse and keyboard work as before.
- **Styling:** Tailwind for layout and type; the atmosphere, logotype, range inputs, sliders and pressed states are plain CSS next to their components (in `@layer components`). DOM motion is transform and opacity only (each moving part of the badge and logotype fog is its own SVG, so it runs on the compositor), never filters or blur, and it all stops under `prefers-reduced-motion`.
- **Fonts:** Syne and Manrope, self-hosted variable fonts from Fontsource (SIL OFL, see `src/fonts/`), with latin-ext loaded only when needed (Latvian, Romanian titles).
