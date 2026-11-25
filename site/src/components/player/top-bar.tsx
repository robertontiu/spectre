"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/brand/badge";
import { cx } from "@/lib/cx";
import { usePlayer, usePlayerStore } from "./player-context";
import type { RepeatMode } from "./player-store";
import { NextIcon, PlayPauseIcon, PreviousIcon, RepeatIcon, ShuffleIcon } from "./icons";

const REPEAT_LABEL: Record<RepeatMode, string> = { all: "Repeat all", one: "Repeat one", off: "Repeat off" };

/**
 * A glass bar pinned to the top of the viewport while the player card's top edge is
 * scrolled away: the badge, the playing track and the transport, wired to the same store
 * as the card (so the filtered queue applies). An IntersectionObserver on the card's
 * top-edge sentinel (`[data-card-top]`, in PlayerCard) shows and hides it; while hidden it
 * is inert and aria-hidden, so neither Tab nor a screen reader lands in it.
 */
export function TopBar() {
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const sentinel = document.querySelector("[data-card-top]");
    if (!sentinel) return;
    const observer = new IntersectionObserver(([entry]) => {
      // Out of view above the viewport, not below it (a short window, a restored scroll).
      setShown(!entry.isIntersecting && entry.boundingClientRect.top < 0);
    });
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      role="region"
      aria-label="Now playing"
      aria-hidden={!shown}
      inert={!shown}
      className={cx("topbar", shown && "on")}
    >
      <div className="mx-auto flex h-14 max-w-[860px] items-center gap-3 px-4 phone:gap-2">
        <span className="topbar-logo">
          <Badge />
        </span>
        <NowPlayingLine />
        <BarTransport />
      </div>
      <Progress />
    </div>
  );
}

function NowPlayingLine() {
  const { tracks } = usePlayerStore();
  const track = tracks[usePlayer((s) => s.current)];
  if (!track) return <div className="flex-1" />;
  return (
    <div className="min-w-0 flex-1 leading-tight">
      <p className="m-0 truncate font-display text-[15px] font-bold">{track.title}</p>
      <p className="m-0 truncate text-[13px] text-mute">
        {track.artist}, <span className="font-semibold text-ice">{track.bpm} BPM</span>
        {` · ${track.genre}`}
      </p>
    </div>
  );
}

function BarTransport() {
  const store = usePlayerStore();
  const playing = usePlayer((s) => s.playing);
  const shuffle = usePlayer((s) => s.shuffle);
  const repeat = usePlayer((s) => s.repeat);
  return (
    <div className="flex flex-none items-center gap-0.5">
      {/* Shuffle and repeat only where they fit (not on phones). */}
      <button
        type="button"
        className="ib st tb phone:hidden"
        aria-pressed={shuffle}
        aria-label="Shuffle"
        title="Shuffle"
        onClick={store.toggleShuffle}
      >
        <ShuffleIcon />
      </button>
      <button
        type="button"
        className={cx("ib st tb phone:hidden", repeat === "one" && "r1")}
        aria-pressed={repeat !== "off"}
        aria-label={REPEAT_LABEL[repeat]}
        title={REPEAT_LABEL[repeat]}
        onClick={store.cycleRepeat}
      >
        <RepeatIcon />
        <span className="one">1</span>
      </button>
      <button type="button" className="ib tb phone:hidden" aria-label="Previous track" onClick={store.previous}>
        <PreviousIcon />
      </button>
      <button
        type="button"
        className="ib tb tb-play"
        aria-label={playing ? "Pause" : "Play"}
        onClick={store.togglePlay}
      >
        <PlayPauseIcon playing={playing} />
      </button>
      <button type="button" className="ib tb" aria-label="Next track" onClick={store.next}>
        <NextIcon />
      </button>
    </div>
  );
}

/** A hairline of the track's progress along the bar's bottom edge. */
function Progress() {
  const time = usePlayer((s) => s.time);
  const duration = usePlayer((s) => s.duration);
  const fraction = duration > 0 ? Math.min(1, time / duration) : 0;
  return <i className="topbar-progress" aria-hidden="true" style={{ transform: `scaleX(${fraction})` }} />;
}
