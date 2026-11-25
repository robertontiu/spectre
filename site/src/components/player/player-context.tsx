"use client";

import { createContext, useContext, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import type { Track } from "@/lib/tracks";
import { PlayerStore, type PlayerState } from "./player-store";

const PlayerContext = createContext<PlayerStore | null>(null);

type PlayerProviderProps = {
  tracks: readonly Track[];
  /** Index of the track to open with. */
  initial?: number;
  /** Try to start the initial track at once (track links). */
  autoplay?: boolean;
  children: ReactNode;
};

/** Owns the player store and the page's <audio> element. */
export function PlayerProvider({ tracks, initial = 0, autoplay = false, children }: PlayerProviderProps) {
  const [store] = useState(() => new PlayerStore(tracks, initial, autoplay));
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const detach = store.attach(audio);
    document.addEventListener("keydown", store.handleKey);
    return () => {
      detach();
      document.removeEventListener("keydown", store.handleKey);
    };
  }, [store]);

  return (
    <PlayerContext value={store}>
      {children}
      {/* crossOrigin: the audio comes from the S3 bucket (another origin) and feeds the
          Web Audio graph; without CORS the graph would only output silence. */}
      <audio ref={audioRef} preload="metadata" crossOrigin="anonymous" />
    </PlayerContext>
  );
}

export function usePlayerStore(): PlayerStore {
  const store = useContext(PlayerContext);
  if (!store) throw new Error("usePlayerStore must be used inside <PlayerProvider>");
  return store;
}

/** Subscribes to one slice of the player state. Return primitives or stable references. */
export function usePlayer<T>(selector: (state: PlayerState) => T): T {
  const store = usePlayerStore();
  const snapshot = () => selector(store.getState());
  return useSyncExternalStore(store.subscribe, snapshot, snapshot);
}
