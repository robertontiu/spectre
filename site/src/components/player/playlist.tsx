"use client";

import { useMemo } from "react";
import { formatTime } from "@/lib/format";
import { GenreFilter } from "./genre-filter";
import { usePlayer, usePlayerStore } from "./player-context";
import { filterIndices } from "./player-store";

/**
 * The finished tracks, newest first, narrowed by the genre filter; the selected one
 * carries the track's colours. The count and total length are the filtered list's.
 */
export function Playlist() {
  const store = usePlayerStore();
  const { tracks } = store;
  const current = usePlayer((s) => s.current);
  const family = usePlayer((s) => s.family);
  const shown = useMemo(() => filterIndices(tracks, family), [tracks, family]);
  const total = shown.reduce((sum, i) => sum + Math.round(tracks[i].duration || 0), 0);

  return (
    <div className="mt-[22px] border-t border-white/8 pt-[18px]">
      <div className="mb-3 flex flex-wrap items-center gap-2.5">
        <h3 className="m-0 mr-auto font-display text-[18px] leading-[1.2] font-semibold">Tracks</h3>
        <span className="text-[14px] whitespace-nowrap text-mute" aria-live="polite">
          {`${shown.length} ${shown.length === 1 ? "track" : "tracks"}, ${formatTime(total)}`}
        </span>
      </div>
      <GenreFilter />
      <ol className="m-0 grid list-none gap-1.5 p-0">
        {tracks.length === 0 && <li className="rounded-[14px] bg-white/5 px-4 py-3.5 text-mute">No tracks yet.</li>}
        {shown.map((i) => {
          const t = tracks[i];
          return (
            <li key={t.id}>
              <button type="button" className="row" aria-current={i === current} onClick={() => store.select(i, true)}>
                <span className="t">{`${t.artist} - ${t.title}`}</span>
                <span className="d">{formatTime(Math.round(t.duration))}</span>
                <span className="b">{`${t.bpm} BPM · ${t.genre}`}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
