"use client";

import type { CSSProperties, ReactNode } from "react";
import { paletteFrom, paletteVars } from "@/lib/color";
import { cx } from "@/lib/cx";
import { usePlayer } from "../player/player-context";
import { FADE_MS } from "../player/player-store";

/**
 * Renders track-coloured background layers twice, once per palette slot, and crossfades
 * the slots' opacity when the track changes. Each slot is painted once in fixed colours,
 * so a track change or a tab switch never repaints the big blurred layers mid-glide (the
 * cause of flicker when the palette was animated through CSS variables on <html>).
 * Both copies stay mounted, so their drift animations stay in step.
 */
export function PaletteCrossfade({ className, children }: { className?: string; children: ReactNode }) {
  const fade = usePlayer((s) => s.fade);
  return (
    <div className={cx("xf", className)} aria-hidden="true">
      {fade.slots.map((colors, i) => {
        const front = i === fade.front;
        const style = {
          ...paletteVars(paletteFrom(colors)),
          "--xf-duration": `${FADE_MS}ms`,
          opacity: front ? 1 : 0,
          // A settled back slot is hidden, so the browser keeps no work for it.
          visibility: front || !fade.settled ? "visible" : "hidden",
        } as CSSProperties;
        return (
          <div key={i} className="xf-slot" style={style}>
            {children}
          </div>
        );
      })}
    </div>
  );
}
