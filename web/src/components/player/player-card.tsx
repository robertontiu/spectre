"use client";

import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { paletteFrom, paletteVars } from "@/lib/color";
import { usePlayerStore } from "./player-context";

/**
 * The card element. It carries the accent palette (--c1..3) that the controls and
 * canvases use; the store glides it from track to track.
 */
export function PlayerCard({ children }: { children: ReactNode }) {
  const store = usePlayerStore();
  const ref = useRef<HTMLElement>(null);
  // The opening track's colours, rendered on the server; later changes are written by the store.
  const [style] = useState(() => paletteVars(paletteFrom(store.tracks[store.initial]?.colors ?? [])) as CSSProperties);

  useEffect(() => {
    store.palette.attach(ref.current);
    return () => store.palette.attach(null);
  }, [store]);

  return (
    <section ref={ref} className="player" aria-label="Spectre player" style={style}>
      {children}
    </section>
  );
}
