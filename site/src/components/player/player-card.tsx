"use client";

import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { paletteFrom, paletteVars } from "@/lib/color";
import { usePlayerStore } from "./player-context";

/**
 * The card element. It carries the accent palette (--c1..3) that its controls use. On a
 * track change the new colours are written once; the properties are registered as
 * <color> (player.css), so the browser transitions them itself, with no script per frame
 * and no re-render.
 */
export function PlayerCard({ children }: { children: ReactNode }) {
  const store = usePlayerStore();
  const ref = useRef<HTMLElement>(null);
  // The opening track's colours, rendered on the server.
  const [style] = useState(() => paletteVars(paletteFrom(store.tracks[store.initial]?.colors ?? [])) as CSSProperties);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let current = store.getState().current;
    return store.subscribe(() => {
      const next = store.getState().current;
      if (next === current) return;
      current = next;
      for (const [name, value] of Object.entries(paletteVars(paletteFrom(store.tracks[next]?.colors ?? [])))) {
        el.style.setProperty(name, value);
      }
    });
  }, [store]);

  return (
    <section ref={ref} className="player" aria-label="Spectre player" style={style}>
      {children}
    </section>
  );
}
