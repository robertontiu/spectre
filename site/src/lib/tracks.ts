import data from "../../data/tracks.json";

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
  /** The model that ran the producer for this session, e.g. "Claude Opus 5.5"; shown beside the tempo. */
  model: string;
  /** Short genre label shown beside the tempo, e.g. "Latvian folk trap". */
  genre: string;
  style: string;
  feeling: string;
  /** Two or three hex colours; the page mutes them into the night. */
  colors: string[];
};

export const tracks: readonly Track[] = data satisfies Track[];
