"use client";

import { useMemo, useRef, type KeyboardEvent } from "react";
import { type Family, familiesInUse } from "@/lib/tracks";
import { usePlayer, usePlayerStore } from "./player-context";

type Option = { family: Family | null; label: string };

/**
 * Single-select genre pills over the playlist: "All", then each family that has a track,
 * in `FAMILIES` order. A radio group: one tab stop, arrow keys (and Home/End) move and
 * select. Choosing one filters the list and the play queue, never playback itself.
 */
export function GenreFilter() {
  const store = usePlayerStore();
  const family = usePlayer((s) => s.family);
  const options = useMemo<Option[]>(
    () => [{ family: null, label: "All" }, ...familiesInUse(store.tracks).map((f) => ({ family: f, label: f }))],
    [store.tracks],
  );
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const selected = Math.max(
    0,
    options.findIndex((o) => o.family === family),
  );

  if (options.length < 3) return null; // one family: nothing to filter

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const n = options.length;
    const moves: Record<string, number> = {
      ArrowRight: (selected + 1) % n,
      ArrowDown: (selected + 1) % n,
      ArrowLeft: (selected - 1 + n) % n,
      ArrowUp: (selected - 1 + n) % n,
      Home: 0,
      End: n - 1,
    };
    const to = moves[e.key];
    if (to === undefined) return;
    e.preventDefault();
    store.setFamily(options[to].family);
    refs.current[to]?.focus();
  };

  return (
    <div role="radiogroup" aria-label="Filter by genre" className="mb-3.5 flex flex-wrap gap-2" onKeyDown={onKeyDown}>
      {options.map((o, i) => (
        <button
          key={o.label}
          ref={(el) => {
            refs.current[i] = el;
          }}
          type="button"
          role="radio"
          aria-checked={i === selected}
          tabIndex={i === selected ? 0 : -1}
          className="pill"
          onClick={() => store.setFamily(o.family)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
