import { Controls } from "./controls";
import { NowPlaying } from "./now-playing";
import { PlayerCard } from "./player-card";
import { Playlist } from "./playlist";
import { SeekBar } from "./seek-bar";
import { Visualizer } from "./visualizer";
import "./player.css";

/** The player card, raised over the banner and dissolving into the colour field. */
export function Player() {
  return (
    <PlayerCard>
      <i className="edge" aria-hidden="true" />
      <Visualizer />
      <NowPlaying />
      <SeekBar />
      <Controls />
      <Playlist />
    </PlayerCard>
  );
}
