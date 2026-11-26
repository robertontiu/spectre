import data from "../../data/tracks.json";

/**
 * The listener-facing genre families: the order of the filter pills and of the playlist's
 * groups. Since 2026-11-26 the owner's order leads (Electronic, with trance before dubstep, then
 * Rock and Hip-Hop); the rest keep the popularity order below. Every track's `family` is one of these; add a new one only when no
 * existing family fits, placed by its share in the same source.
 *
 * Popularity is the U.S. share of on-demand audio streams in Luminate's 2025 Year-End Music
 * Report (January 2026, "U.S. Share of Total Volume, by Format & Genre" and "Top U.S. Main
 * Genres, 2025"): R&B/Hip-Hop 24.9%, Rock 18.6%, Latin 8.6%, Dance/Electronic 3.7%, World
 * Music 2.2%, Holiday/Seasonal about 1.0% (14.5B of about 1.4T streams). Mapping judgements:
 * Folklore is counted as World Music; Soundtrack has no genre of its own there (soundtracks are
 * split across their songs' genres) and our score-like instrumentals sit nearest Classical,
 * 0.8%, so it comes last.
 */
export const FAMILIES = ["Electronic", "Rock", "Hip-Hop", "Latin", "Folklore", "Holiday", "Soundtrack"] as const;

/** Within a family, these genres come first in this order (the owner's order: trance before dubstep); other genres follow. */
const GENRE_ORDER = ["Trance", "Dubstep"];
const genreRank = (g: string) => {
  const i = GENRE_ORDER.indexOf(g);
  return i < 0 ? GENRE_ORDER.length : i;
};

export type Family = (typeof FAMILIES)[number];

/** The family's URL value for `?genre=`, e.g. "hip-hop". */
export const familySlug = (f: Family) => f.toLowerCase().replace(/[^a-z0-9]+/g, "-");

/** The family a `?genre=` value names, or null (absent or unknown: all tracks). */
export const familyFromSlug = (slug: string | null | undefined): Family | null =>
  FAMILIES.find((f) => familySlug(f) === slug) ?? null;

/**
 * One third-party attribution shown in the track's info dialog: a voicebank or vocoder heard in
 * the track (its credit line from `engine/voices.json`), or a quoted public-domain melody.
 */
export type Credit = {
  /** The line as shown, e.g. "Vocals: Hoshino Hanami, DiffSinger voicebank by Lotte V". */
  text: string;
  /** Optional link: the licence where it asks for one, otherwise the author's page (opens in a new tab). */
  url?: string;
};

/** One finished Spectre session, as listed in `data/tracks.json` (newest first). */
export type Track = {
  /** Session number, e.g. "005"; selects `sessions/005-*` for the master. */
  id: string;
  /**
   * The track's fixed showcase id (UUID v4, made once at delivery, never changed): its
   * key prefix in the S3 bucket, `<uuid>/rendition.mp3` (the master) and `<uuid>/log.md`.
   */
  uuid: string;
  artist: string;
  title: string;
  /**
   * The master's file name, e.g. "005-fuck-every-war.mp3": the track's slug without
   * ".mp3" (`/track/005-fuck-every-war`), and its name under `public/tracks/` when the
   * audio is served locally (no bucket configured, `dev:local`, static exports).
   */
  file: string;
  /** Length in seconds. */
  duration: number;
  bpm: number;
  /** The model that ran the producer for this session, e.g. "Claude Opus 5.5"; shown in the track's info dialog. */
  model: string;
  /** Short genre label shown beside the tempo, e.g. "Latvian folk trap". */
  genre: string;
  /** The broad family the playlist filters by, e.g. "Hip-Hop" (one of `FAMILIES`). */
  family: Family;
  style: string;
  feeling: string;
  /** Two or three hex colours; the page mutes them into the night. */
  colors: string[];
  /**
   * Third-party attributions, required for every voicebank or other third-party asset audible
   * in the track; absent when the track has none.
   */
  credits?: Credit[];
};

/** The track's credits, checked: each a non-empty `text` and, if given, an http(s) `url`. */
function checkCredits(id: string, credits: unknown): Credit[] | undefined {
  if (credits === undefined) return undefined;
  const fail = (why: string) => {
    throw new Error(`data/tracks.json: track ${id} has invalid credits: ${why}`);
  };
  if (!Array.isArray(credits) || credits.length === 0) fail("expected a non-empty array (or no field)");
  return (credits as unknown[]).map((c, i) => {
    if (typeof c !== "object" || c === null) return fail(`entry ${i} is not an object`);
    const { text, url, ...rest } = c as Record<string, unknown>;
    if (Object.keys(rest).length) fail(`entry ${i} has unknown fields ${Object.keys(rest).join(", ")}`);
    if (typeof text !== "string" || !text.trim()) fail(`entry ${i} needs a non-empty text`);
    if (url !== undefined && (typeof url !== "string" || !/^https?:\/\/\S+$/.test(url))) {
      fail(`entry ${i} has a url that is not http(s)`);
    }
    return url === undefined ? { text: text as string } : { text: text as string, url: url as string };
  });
}

/**
 * JSON imports type strings as `string`, so `family` and `credits` are checked here: a track
 * whose family is not in `FAMILIES`, or whose credits are malformed, stops the build (every
 * page imports this list while prerendering).
 */
function checkTrack(t: Omit<Track, "family" | "credits"> & { family: string; credits?: unknown }): Track {
  const family = FAMILIES.find((f) => f === t.family);
  if (!family) {
    throw new Error(
      `data/tracks.json: track ${t.id} has family ${JSON.stringify(t.family)}, not one of ${FAMILIES.join(", ")}`,
    );
  }
  const { credits: raw, ...rest } = t;
  const credits = checkCredits(t.id, raw);
  return credits ? { ...rest, family, credits } : { ...rest, family };
}

/**
 * Every track in the playlist's order: grouped by family in `FAMILIES` order, then by genre in
 * `GENRE_ORDER` within a family, newest first within a genre (the higher session number first). The player's queue
 * and a filtered view follow this order, so a filtered view is newest first.
 */
export const tracks: readonly Track[] = data
  .map(checkTrack)
  .sort(
    (a, b) =>
      FAMILIES.indexOf(a.family) - FAMILIES.indexOf(b.family) ||
      genreRank(a.genre) - genreRank(b.genre) ||
      b.id.localeCompare(a.id),
  );

/** The families that have at least one track, in `FAMILIES` order. */
export const familiesInUse = (list: readonly Track[]): Family[] =>
  FAMILIES.filter((f) => list.some((t) => t.family === f));
