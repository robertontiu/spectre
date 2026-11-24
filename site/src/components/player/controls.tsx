"use client";

import { cx } from "@/lib/cx";
import { usePlayer, usePlayerStore } from "./player-context";
import type { RepeatMode } from "./player-store";
import { NextIcon, PlayPauseIcon, PreviousIcon, RepeatIcon, ShuffleIcon, SpeakerIcon } from "./icons";
import { RangeInput } from "./range-input";

const REPEAT_LABEL: Record<RepeatMode, string> = { all: "Repeat all", one: "Repeat one", off: "Repeat off" };

/** Shuffle and repeat on the left, transport in the middle, volume on the right
    (on phones: transport on its own row above the other two). */
export function Controls() {
  return (
    <div className="mt-1.5 grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2.5 [grid-template-areas:'mode_tr_vol'] phone:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] phone:gap-y-0.5 phone:[grid-template-areas:'tr_tr'_'mode_vol']">
      <Modes />
      <Transport />
      <Volume />
    </div>
  );
}

function Modes() {
  const store = usePlayerStore();
  const shuffle = usePlayer((s) => s.shuffle);
  const repeat = usePlayer((s) => s.repeat);
  return (
    <div className="flex gap-1 [grid-area:mode]">
      <button
        type="button"
        className="ib st"
        aria-pressed={shuffle}
        aria-label="Shuffle"
        title="Shuffle"
        onClick={store.toggleShuffle}
      >
        <ShuffleIcon />
      </button>
      <button
        type="button"
        className={cx("ib st", repeat === "one" && "r1")}
        aria-pressed={repeat !== "off"}
        aria-label={REPEAT_LABEL[repeat]}
        title={REPEAT_LABEL[repeat]}
        onClick={store.cycleRepeat}
      >
        <RepeatIcon />
        <span className="one">1</span>
      </button>
    </div>
  );
}

function Transport() {
  const store = usePlayerStore();
  const playing = usePlayer((s) => s.playing);
  const needsGesture = usePlayer((s) => s.needsGesture);
  return (
    <div className="flex items-center gap-2.5 [grid-area:tr] phone:justify-self-center">
      <button type="button" className="ib" aria-label="Previous track" onClick={store.previous}>
        <PreviousIcon />
      </button>
      <button
        type="button"
        className={cx("ib play", needsGesture && "nudge")}
        aria-label={playing ? "Pause" : needsGesture ? "Play (your browser waits for a tap)" : "Play"}
        onClick={store.togglePlay}
      >
        <PlayPauseIcon playing={playing} />
        {needsGesture && (
          <span className="nudge-tip" aria-hidden="true">
            Tap to play
          </span>
        )}
      </button>
      <button type="button" className="ib" aria-label="Next track" onClick={store.next}>
        <NextIcon />
      </button>
    </div>
  );
}

function Volume() {
  const store = usePlayerStore();
  const volume = usePlayer((s) => s.volume);
  const muted = usePlayer((s) => s.muted);
  return (
    <div className="flex w-[min(100%,190px)] items-center gap-1.5 justify-self-end [grid-area:vol]">
      <button
        type="button"
        className={cx("ib st", (muted || volume === 0) && "muted")}
        aria-label={muted ? "Unmute" : "Mute"}
        title="Mute"
        onClick={store.toggleMute}
      >
        <SpeakerIcon />
      </button>
      <RangeInput
        min={0}
        max={1}
        step={0.01}
        value={volume}
        progress={volume}
        aria-label="Volume"
        onChange={(e) => store.setVolume(Number(e.target.value))}
      />
    </div>
  );
}
