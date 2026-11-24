import data from "../../data/tracks.json";

/** One finished Spectre session, as listed in `data/tracks.json` (newest first). */
export type Track = {
  /** Session number, e.g. "005"; selects `sessions/005-*` for the master. */
  id: string;
  artist: string;
  title: string;
  /** Path of the MP3 relative to the site root, e.g. "tracks/005-fuck-every-war.mp3". */
  src: string;
  /** Length in seconds. */
  duration: number;
  bpm: number;
  /** Short genre label shown beside the tempo, e.g. "Latvian folk trap". */
  genre: string;
  style: string;
  feeling: string;
  /** Two or three hex colours; the page mutes them into the night. */
  colors: string[];
};

export const tracks: readonly Track[] = data satisfies Track[];
