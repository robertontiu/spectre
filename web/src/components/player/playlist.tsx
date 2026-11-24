"use client";

import { formatTime } from "@/lib/format";
import { usePlayer, usePlayerStore } from "./player-context";

/** Every finished track, newest first; the selected one carries the track's colours. */
export function Playlist() {
  const store = usePlayerStore();
  const { tracks } = store;
  const current = usePlayer((s) => s.current);
  const total = tracks.reduce((sum, t) => sum + Math.round(t.duration || 0), 0);

  return (
    <div className="mt-[22px] border-t border-white/8 pt-[18px]">
      <div className="mb-3 flex flex-wrap items-center gap-2.5">
        <h3 className="m-0 mr-auto font-display text-[18px] leading-[1.2] font-semibold">Tracks</h3>
        <span className="text-[14px] whitespace-nowrap text-mute">
          {`${tracks.length} ${tracks.length === 1 ? "track" : "tracks"}, ${formatTime(total)}`}
        </span>
      </div>
      <ol className="m-0 grid list-none gap-1.5 p-0">
        {tracks.length === 0 && <li className="rounded-[14px] bg-white/5 px-4 py-3.5 text-mute">No tracks yet.</li>}
        {tracks.map((t, i) => (
          <li key={t.id}>
            <button type="button" className="row" aria-current={i === current} onClick={() => store.select(i, true)}>
              <span className="t">{`${t.artist} - ${t.title}`}</span>
              <span className="d">{formatTime(Math.round(t.duration))}</span>
              <span className="b">{`${t.bpm} BPM · ${t.genre}`}</span>
            </button>
          </li>
        ))}
      </ol>
    </div>
  );
}
