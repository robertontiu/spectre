import type { Track } from "./tracks";

export const SITE_URL = "https://spectre.robertontiu.com";
export const SITE_NAME = "Spectre";
export const SITE_DESCRIPTION = "Spectre, an AI beat producer that starts from a feeling and listens by looking.";

/**
 * Preview builds (`npm run export:preview`) are served from an unknown sub-path, so they
 * load audio by relative URL and leave the address bar alone.
 */
export const IS_PREVIEW = process.env.NEXT_PUBLIC_SPECTRE_PREVIEW === "1";

/** The track's URL slug, taken from its file name, e.g. "005-fuck-every-war". */
export const trackSlug = (t: Track) => t.src.replace(/^.*\//, "").replace(/\.mp3$/, "");

export const trackPath = (t: Track) => `/track/${trackSlug(t)}`;

/** Where the page loads the track's audio from. */
export const audioPath = (t: Track) => (IS_PREVIEW ? t.src : `/${t.src}`);

/** The public link to a track, for sharing. */
export const trackUrl = (t: Track) => new URL(trackPath(t), SITE_URL).href;
