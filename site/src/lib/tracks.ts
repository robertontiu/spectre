import data from "../../data/tracks.json";

/**
 * The listener-facing genre families, in the order the playlist's filter shows them. Every
 * track's `family` is one of these; add a new one only when no existing family fits.
 */
export const FAMILIES = ["Hip-Hop", "Electronic", "Rock", "Latin", "World", "Soundtrack", "Holiday"] as const;

export type Family = (typeof FAMILIES)[number];

/** The family's URL value for `?genre=`, e.g. "hip-hop". */
export const familySlug = (f: Family) => f.toLowerCase().replace(/[^a-z0-9]+/g, "-");

/** The family a `?genre=` value names, or null (absent or unknown: all tracks). */
export const familyFromSlug = (slug: string | null | undefined): Family | null =>
  FAMILIES.find((f) => familySlug(f) === slug) ?? null;

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
};

/**
 * JSON imports type strings as `string`, so `family` is checked here: a track whose family
 * is not in `FAMILIES` stops the build (every page imports this list while prerendering).
 */
function checkFamily(t: Omit<Track, "family"> & { family: string }): Track {
  const family = FAMILIES.find((f) => f === t.family);
  if (!family) {
    throw new Error(
      `data/tracks.json: track ${t.id} has family ${JSON.stringify(t.family)}, not one of ${FAMILIES.join(", ")}`,
    );
  }
  return { ...t, family };
}

export const tracks: readonly Track[] = data.map(checkFamily);

/** The families that have at least one track, in `FAMILIES` order. */
export const familiesInUse = (list: readonly Track[]): Family[] =>
  FAMILIES.filter((f) => list.some((t) => t.family === f));
