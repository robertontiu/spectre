# Spectre: the site

The public home of [Spectre](../README.md), an AI beat producer that starts from a feeling and listens by looking. It is a port of the static showcase in [`site/`](../site/) to Next.js: the same ghostly backdrop, the wraith badge and the smoky logotype, and a player with a visualizer and the playlist (no equalizer: the tracks play exactly as mastered). Every track also has its own page and share card.

Next.js 16 (App Router, Turbopack), React 19, TypeScript (strict), Tailwind CSS 4. No UI or animation libraries.

## Run it

Node 20.9 or newer.

```bash
cd site
npm install
npm run dev          # http://localhost:3000
```

| Script                                                  | What it does                                                                                                                                                                              |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm run dev`                                           | Dev server. Audio comes from the S3 bucket if `.env.local` configures it, otherwise from `public/tracks/` (see "Audio").                                                                  |
| `npm run dev:local`                                     | Offline development: copies the masters from `../sessions/` into `public/tracks/` and plays them from there, bucket or not (`SPECTRE_LOCAL_AUDIO=1`).                                     |
| `npm run build` / `npm start`                           | Production build (what Vercel runs) and a local production server. The prebuild copies local masters only while no bucket is configured (the transition; see "Audio").                    |
| `npm run export`                                        | Fully static site in `out/` (`output: "export"`): no audio route, so the masters are copied into it and played from `tracks/`.                                                            |
| `npm run export:preview`                                | Static home page that works from any sub-path (relative URLs, assets in `out/assets/`); used for the claude.ai artifact preview. Like `export`, it carries its own copies of the masters. |
| `npm run sync-tracks`                                   | Copy the masters into `public/tracks/` (needs the session folders locally: `python3 ../tools/upload_track.py --fetch <id>` restores one from the bucket).                                 |
| `npm run lint` / `npm run typecheck` / `npm run format` | ESLint (create-next-app config), `tsc`, Prettier with Tailwind class sorting.                                                                                                             |

## Audio

The masters are not part of the site or its deployments. With a bucket configured, they live in an S3-compatible bucket set up through environment variables (below), with each track's other session files, under the track's `uuid` from `data/tracks.json`: `<uuid>/rendition.mp3` is the master (layout in [docs/agents/track-storage.md](../docs/agents/track-storage.md)).

- The player loads `/api/track/<slug>` ([`src/app/api/track/[slug]/route.server.ts`](src/app/api/track/[slug]/route.server.ts)). The route finds the slug in `data/tracks.json` (404 otherwise) and answers with a 302 to a presigned GET of `<uuid>/rendition.mp3`, signed with a **read-only** key ([`src/lib/s3.ts`](src/lib/s3.ts)). No audio passes through the function, which only signs (Node runtime, a few ms per call, well inside Vercel Hobby's limits). The redirect carries `Cache-Control: private, max-age=300`.
- **Signed URLs** are valid for at least `SPECTRE_SIGNED_URL_TTL` seconds (default 3600) after they are handed out. The `<audio>` element keeps using the URL it got for every later range request (seeking, re-buffering after a pause), so the URL has to outlive a listening session of a track: the longest track runs 7:28, and an hour covers it several times over, pauses included, while a shared URL dies within the hour. URLs are signed per 10-minute window (the same URL for everyone inside a window, valid for window + TTL), so the browser's HTTP cache can reuse the bytes across plays. If a URL still expires (a very long pause), the player re-resolves the source before resuming or seeking once it is 25 minutes old, and reloads after an error or an 8-second stall, carrying on from the same spot (`player-store.ts`).
- **Signing:** a hand-written SigV4 query presigner (about 40 lines of `node:crypto`) instead of `@aws-sdk/client-s3` + `@aws-sdk/s3-request-presigner`: the route signs one kind of request only, and the SDK would add several MB of dependencies and a heavier function bundle and cold start. Its output is byte-identical to botocore's presigner (tested with hosted S3-compatible and local endpoints, special characters in keys, a trailing slash in the endpoint).
- **Cross-origin audio:** the visualizer wires the `<audio>` element into an AudioContext through a MediaElementSource; for audio from another origin that graph outputs silence unless the element has `crossOrigin="anonymous"` (set in `player-context.tsx`) **and** the bucket answers with CORS headers. The bucket's CORS rules are set with `python3 ../tools/upload_track.py --cors`: GET and HEAD from `https://spectre.robertontiu.com`, `https://spectre-*.vercel.app` (preview deployments) and `http://localhost:3000`, exposing `Accept-Ranges`, `Content-Range` and `Content-Length`.
- **Hotlinking** is deterred where it is cheap and cannot break playback: the route refuses (403) a request whose `Origin` is another site, or that another site's page makes for media or a fetch (`Sec-Fetch-Site: cross-site` with any `Sec-Fetch-Dest` but `document`). Same-origin requests, address-bar navigations, link clicks and clients without these headers (crawlers reading `og:audio`, curl) pass: a missing `Referer` or `Origin` is normal for `<audio>`. This keeps other pages from embedding the player's audio; it cannot stop anyone from downloading a track, and a signed URL works for anyone who has it until it expires.
- `og:audio` on each track page is `https://spectre.robertontiu.com/api/track/<slug>`.
- **Without a bucket** (any of the five `SPECTRE_S3_*` variables below missing), the route redirects to `/tracks/<file>` in `public/tracks/`, and `npm run build`'s prebuild copies the masters there from `../sessions/`. That is how the site runs for anyone without a bucket (a fork, a fresh clone, local work): the session folders are the local source of the audio. A track whose session folder is not in the checkout is skipped with a warning and has no audio in that build; the build itself never fails for it (`npm run build` without any `SPECTRE_S3_*` variable: checked 2026-11-25). **Switching to a bucket is setting the variables and redeploying**; the prebuild then copies nothing and deployments carry no audio.
- Static exports (`export`, `export:preview`) have no server, so they leave the route out (`pageExtensions` in `next.config.ts` drops `*.server.ts`) and play their bundled copies under `tracks/`.

### Environment variables

Set them in Vercel (Project → Settings → Environment Variables, Production and Preview) or in `site/.env.local` for local work (gitignored). Never commit values.

| Variable                       | Value                                                                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------- |
| `SPECTRE_S3_ENDPOINT`          | the bucket's S3 endpoint, e.g. `https://s3.<region>.example.com` (path-style URLs are used) |
| `SPECTRE_S3_REGION`            | e.g. `<region>`                                                                             |
| `SPECTRE_S3_BUCKET`            | the bucket's name, e.g. `<your-bucket>`                                                     |
| `SPECTRE_S3_ACCESS_KEY_ID`     | the site's **read-only** key (the workspace's upload key is a different, read-write one)    |
| `SPECTRE_S3_SECRET_ACCESS_KEY` | its secret                                                                                  |
| `SPECTRE_SIGNED_URL_TTL`       | optional: seconds a signed URL lives at least, default `3600` (minimum 60)                  |
| `SPECTRE_LOCAL_AUDIO`          | optional, development only: `1` plays `public/tracks/` even with a bucket (`dev:local`)     |

## Add a track

1. The master is in its session folder as `sessions/NNN-name/<title-slug>-mastered.mp3` (the session delivery procedure does this).
2. Add a line at the top of [`data/tracks.json`](data/tracks.json) (newest first), without a `uuid`:

   ```json
   {"id":"016","artist":"Spectre","title":"…","file":"016-title-slug.mp3","duration":180.0,"bpm":120,"model":"…","genre":"…","family":"…","style":"…","feeling":"…","colors":["#…","#…","#…"]},
   ```

   `id` selects the session folder; `file` is the track's slug plus `.mp3` (the slug is its URL, `/track/016-title-slug`, and `file` its name in `public/tracks/` when played locally); `duration` comes from `ffprobe`, `model` is the producer agent's model (shown only in the track's (i) dialog), `genre` is the short label shown beside the tempo, `family` is the broad genre the playlist's filter pills use (one of `FAMILIES` in [`src/lib/tracks.ts`](src/lib/tracks.ts): Hip-Hop, Electronic, Rock, Latin, Folklore, Soundtrack, Holiday; a new top-level family, added there, only when no existing one fits; the build fails on a family not in that list; Folklore is traditional and folk music of any nation (joc țigănesc, carols of a folk tradition, folk dances); a fusion takes the family of its beat or form (folk trap is Hip-Hop)), and `colors` are 2-3 colours that fit the track (the page mutes them).

3. **Publish,** only after the owner has listened to and approved the master (docs/ORCHESTRATION.md standing rule 21): `python3 ../tools/upload_track.py 016 --owner-approved` (with the workspace's write key in the environment) gives the track its `uuid` in `data/tracks.json` and uploads its session files to the bucket. Without a bucket it uploads nothing, runs the same local checks and lists the files to send to the user instead (exit 0); the session folder stays local and the site plays its master from it. Then check `npm run build` and commit `data/tracks.json`; the site picks the track up on its next deploy.

## Deploy on Vercel

Create a Vercel project from the GitHub repo with:

- **Root Directory:** `site`
- **Include files outside the root directory in the Build Step:** enabled (it is by default). Only needed without a bucket: the prebuild then reads the masters from `../sessions/`.
- Framework preset Next.js, default build command (`npm run build`) and output.
- **Deployments only for site changes:** [`vercel.json`](vercel.json) turns Vercel's automatic Git deployments off (`git.deploymentEnabled: false`), because Hobby counts every deployment, cancelled ones included. The workflow [`.github/workflows/deploy-site.yml`](../.github/workflows/deploy-site.yml) calls a Vercel Deploy Hook (repository secret `VERCEL_DEPLOY_HOOK`; Vercel → Project → Settings → Git → Deploy Hooks, branch `main`) when a push to `main` changes `site/**`. To redeploy without a change: GitHub → Actions → Deploy site → Run workflow, or Redeploy in Vercel.
- **Environment variables:** the five `SPECTRE_S3_*` variables above with the read-only key, for Production and Preview (and `SPECTRE_SIGNED_URL_TTL` if the default doesn't suit). Without them the site serves the local copies (see "Audio").
- Domain: add `spectre.robertontiu.com` and point a `CNAME` for `spectre` at `cname.vercel-dns.com`. Absolute URLs in the metadata, sitemap, share links and OG cards use `https://spectre.robertontiu.com` (`src/lib/site.ts`).

With the bucket configured, deployments carry no audio (the 15 masters were about 119 MB per deployment when Vercel served them from `public/tracks/`).

## How it is built

```
data/tracks.json          the canonical track list (newest first), with each track's uuid
scripts/                  sync-tracks.mjs (local copies of the masters), preview-export.mjs
src/app/                  layout (metadata, fonts), home page, track/[slug] (page + OG card),
                          api/track/[slug] (audio redirect), robots, sitemap, icons
src/components/
  spectre-page.tsx        the whole page, shared by / and /track/[slug]
  atmosphere/             the fixed background stack: SVG apparition (server-rendered) and
                          AtmosphereField, the canvas planes of mist, fog and track colours
  brand/                  badge, logotype + GlitchFrame, GitHub pill
  player/                 store, provider, card, visualizer, now playing + share,
                          seek bar, controls, playlist + genre filter, top bar
src/lib/                  Web Audio engine, colours, palette animator,
                          site URLs, tracks, s3 (bucket config and SigV4 presigner)
```

- **Server first.** The page shell, the apparition, the badge and the logotype are server components; client components are the player, the background field and the logotype's glitch timer.
- **Genre filter.** Pills over the playlist ("All", then each family that has a track, in `FAMILIES` order) form a radio group (one tab stop, arrow keys). The choice lives in the player store and the address as `?genre=<slug>` (`history.replaceState`, no navigation or scroll; absent or unknown means All; the prerendered pages render All and apply it on hydration). Next/previous, auto-advance, shuffle and repeat run over the filtered list in its order (`PlayerStore.step`); a playing track outside a newly chosen filter keeps playing, and next/previous continue from its place in the full list. Changing the filter never touches playback.
- **Top bar.** `player/top-bar.tsx`: while the player card's top edge is scrolled away, a glass bar (dark like the visualizer, `backdrop-filter` blur and saturate, solid fallback) slides in at the top of the viewport: the badge, the playing track (title, "Spectre, BPM · genre", truncated) and the transport (previous, play/pause, next; shuffle and repeat too above phone width; phones keep play/pause and next), with a hairline of the track's progress along its bottom edge. It reads the same player store as the card, so the two stay in sync and the filtered queue applies. An IntersectionObserver on a sentinel at the card's top (`[data-card-top]` in `player-card.tsx`) shows and hides it; no scroll handler. Hidden, it is `inert` and `aria-hidden`; it respects the top safe-area inset; under reduced motion it only fades. It lives inside the card (`position: fixed`) to share the track colours. The GitHub pill scrolls away with the banner before the bar can appear, so they never overlap.
- **Player state** lives in a small external store (`player-store.ts`) read with `useSyncExternalStore`, so audio events, media keys and the canvases always see the latest state without re-rendering the page. Preferences (shuffle, repeat, volume, mute) persist in `localStorage` (`spectre.v1`); EQ fields in older saves are ignored.
- **Audio:** `<audio crossOrigin="anonymous">` (the source is the bucket; see "Audio" above) → MediaElementSource → analyser → volume. No EQ or other processing: the tracks are mastered, so they play exactly as mastered (the volume gain is 1 at full volume and the element stays at volume 1, so the level matches the raw file). The graph is built on the first play, so the visualizer and volume always apply. Nothing autoplays, not even a track link (it opens on that track, ready to play).
- **Background field.** The mist, fog banks, wisps and the track-coloured field are composited by `AtmosphereField` (`atmosphere/field-scene.ts`) into two canvases, one under the apparition and one over it. Each original CSS layer is pre-rendered once into its own sprite exactly as its gradient (0.5 px per CSS px; track-coloured sprites again only when the colours change), and every frame the sprites are drawn in the original order with the original keyframed drift and opacity, like the browser composited the CSS layers. The canvases are 0.75 px per CSS px (within about 0.7 Mpx each, no CSS blur); if a device cannot hold about 20 fps (canvas drawn without a GPU) they step down, never below 0.4. One loop (`field-renderer.ts`) draws at 30 fps with time-based drift, in a worker on OffscreenCanvases where the browser supports it (otherwise on the page), pauses in hidden tabs, and glides to a new track's colours in OKLab over 2 s. A track change or tab switch creates, hides or repaints no DOM layer. The stack's height is pinned in px (100lvh first), so a phone's address bar never resizes it while scrolling. Until the first frame, CSS layers in the opening track's colours stand in (frozen), so the server-rendered page looks right; under reduced motion the field is static and colour changes take 0.5 s.
- **Track colours in the card.** The card's accents `--c1..3` are `@property`-registered colours, written once per track and transitioned by the browser (1.6 s); the visualizer canvas glides the same palette in JS (`PaletteAnimator`, no DOM writes). The visualizer paints its own glow, reads no layout in its frame loop (ResizeObserver, IntersectionObserver), caps its backing store at 2x and runs at up to 60 fps (30 on touch screens).
- **Sliders on touch.** The seek and volume sliders are native ranges for keyboard and assistive tech, but a finger only drags them once the gesture is clearly horizontal (a tap still seeks); vertical swipes scroll. Mouse and keyboard work as before.
- **Styling:** Tailwind for layout and type; the atmosphere, logotype, range inputs, sliders and pressed states are plain CSS next to their components (in `@layer components`). DOM motion is transform and opacity only (each moving part of the badge and logotype fog is its own SVG, so it runs on the compositor), never filters or blur, and it all stops under `prefers-reduced-motion`.
- **Fonts:** Syne and Manrope, self-hosted variable fonts from Fontsource (SIL OFL, see `src/fonts/`), with latin-ext loaded only when needed (Latvian, Romanian titles).
