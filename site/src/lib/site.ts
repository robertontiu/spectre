import type { Track } from "./tracks";

export const SITE_URL = "https://spectre.robertontiu.com";
export const SITE_NAME = "Spectre";
export const SITE_DESCRIPTION = "Spectre, an AI beat producer that starts from a feeling and listens by looking.";

/**
 * Preview builds (`npm run export:preview`) are served from an unknown sub-path, so they
 * load audio by relative URL and leave the address bar alone.
 */
export const IS_PREVIEW = process.env.NEXT_PUBLIC_SPECTRE_PREVIEW === "1";

/**
 * Static exports (`npm run export`, `export:preview`) have no server for the audio route,
 * so they ship the masters under `tracks/` and play them from there (set in next.config.ts).
 */
export const STATIC_AUDIO = process.env.NEXT_PUBLIC_SPECTRE_STATIC_AUDIO === "1";

/** The track's URL slug, taken from its file name, e.g. "005-fuck-every-war". */
export const trackSlug = (t: Track) => t.file.replace(/\.mp3$/, "");

export const trackPath = (t: Track) => `/track/${trackSlug(t)}`;

/** Where a local copy of the master is served from (`public/tracks/`). */
export const localAudioPath = (t: Track) => `/tracks/${t.file}`;

/**
 * Where the page loads the track's audio from: the audio route, which redirects to a
 * short-lived signed URL in the S3 bucket (or to the local copy when no bucket is
 * configured); static exports use their bundled copy.
 */
export const audioPath = (t: Track) =>
  IS_PREVIEW ? `tracks/${t.file}` : STATIC_AUDIO ? localAudioPath(t) : `/api/track/${trackSlug(t)}`;

/** The track's audio at the production site, for og:audio (the route lives only there). */
export const trackAudioUrl = (t: Track) => new URL(`/api/track/${trackSlug(t)}`, SITE_URL).href;

/** The public link to a track, for sharing. */
export const trackUrl = (t: Track) => new URL(trackPath(t), SITE_URL).href;
