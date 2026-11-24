"use client";

import { useEffect, useRef, useState } from "react";
import { formatTime } from "@/lib/format";
import { usePlayer, usePlayerStore } from "./player-context";
import { RangeInput } from "./range-input";

const STEPS = 1000;

/** Elapsed time, a scrubbable position slider and the track length. */
export function SeekBar() {
  const store = usePlayerStore();
  const time = usePlayer((s) => s.time);
  const duration = usePlayer((s) => s.duration);
  /** Position (0-1) while the visitor drags; playback position otherwise. */
  const [scrub, setScrub] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Seek once, when the drag is released (the native change event), not on every input.
  useEffect(() => {
    const input = inputRef.current;
    if (!input) return;
    const commit = () => {
      store.seekToFraction(Number(input.value) / STEPS);
      setScrub(null);
    };
    input.addEventListener("change", commit);
    return () => input.removeEventListener("change", commit);
  }, [store]);

  const fraction = scrub ?? (duration ? Math.min(1, time / duration) : 0);
  const elapsed = scrub === null ? time : scrub * duration;

  return (
    <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 text-[14px] text-mute tabular-nums">
      <span>{formatTime(elapsed)}</span>
      <RangeInput
        ref={inputRef}
        min={0}
        max={STEPS}
        step={1}
        value={Math.round(fraction * STEPS)}
        progress={fraction}
        aria-label="Seek"
        onChange={(e) => setScrub(Number(e.target.value) / STEPS)}
      />
      <span>{formatTime(Math.round(duration))}</span>
    </div>
  );
}
