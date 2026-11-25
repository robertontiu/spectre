"use client";

import { useRef } from "react";
import { formatTime } from "@/lib/format";
import type { Track } from "@/lib/tracks";
import { CloseIcon, InfoIcon } from "./icons";

/**
 * An (i) button that opens a small dialog about the current track: the same
 * feeling and style text the link previews carry, plus its genre, tempo, length
 * and the model that produced it. Native <dialog>: Esc and a tap outside close it.
 */
export function InfoButton({ track }: { track: Track }) {
  const dialog = useRef<HTMLDialogElement>(null);

  return (
    <span className="share">
      <button
        type="button"
        className="share-btn info-btn"
        aria-label={`About ${track.title}`}
        aria-haspopup="dialog"
        onClick={() => dialog.current?.showModal()}
      >
        <InfoIcon />
      </button>
      <dialog
        ref={dialog}
        className="track-info"
        aria-labelledby="track-info-title"
        onClick={(e) => {
          if (e.target === e.currentTarget) e.currentTarget.close();
        }}
      >
        <div className="track-info-body">
          <button type="button" className="track-info-close" aria-label="Close" onClick={() => dialog.current?.close()}>
            <CloseIcon />
          </button>
          <h3 id="track-info-title">{track.title}</h3>
          <p className="track-info-feeling">{track.feeling}</p>
          <p className="track-info-style">{track.style}.</p>
          <dl>
            <div>
              <dt>Genre</dt>
              <dd>{track.genre}</dd>
            </div>
            <div>
              <dt>Tempo</dt>
              <dd>{track.bpm} BPM</dd>
            </div>
            <div>
              <dt>Length</dt>
              <dd>{formatTime(Math.round(track.duration))}</dd>
            </div>
            <div>
              <dt>Produced on</dt>
              <dd>{track.model}</dd>
            </div>
          </dl>
        </div>
      </dialog>
    </span>
  );
}
