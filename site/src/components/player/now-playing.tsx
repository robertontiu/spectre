"use client";

import { usePlayer, usePlayerStore } from "./player-context";
import { InfoButton } from "./info-button";
import { ShareButton } from "./share-button";

/** Title, artist, tempo and genre of the selected track, plus any playback problem (the model is in the info dialog). */
export function NowPlaying() {
  const { tracks } = usePlayerStore();
  const current = usePlayer((s) => s.current);
  const message = usePlayer((s) => s.message);
  const track = tracks[current];

  return (
    <div className="mt-[18px] mb-1 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1.5">
      <div className="flex min-w-0 items-center gap-1.5">
        <h2 className="m-0 font-display text-[clamp(24px,3.4vw,32px)] leading-[1.05] font-extrabold tracking-[-.01em]">
          {track?.title ?? "Spectre"}
        </h2>
        {track && <InfoButton key={track.id} track={track} />}
        {track && <ShareButton track={track} />}
      </div>
      {track && (
        <p className="m-0 text-[15px] text-mute">
          <span>{track.artist}</span>, <span className="font-semibold whitespace-nowrap text-ice">{track.bpm} BPM</span>
          <span className="whitespace-nowrap">{` · ${track.genre}`}</span>
        </p>
      )}
      {message && <p className="m-0 basis-full text-[14px] text-[#ffb4a8]">{message}</p>}
    </div>
  );
}
