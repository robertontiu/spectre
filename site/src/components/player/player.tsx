import { Controls } from "./controls";
import { NowPlaying } from "./now-playing";
import { PlayerCard } from "./player-card";
import { Playlist } from "./playlist";
import { SeekBar } from "./seek-bar";
import { TopBar } from "./top-bar";
import { Visualizer } from "./visualizer";
import "./player.css";

/**
 * The player card, raised over the banner and dissolving into the colour field. The top
 * bar sits inside it (position: fixed) so it shares the card's track colours (--c1..3).
 */
export function Player() {
  return (
    <PlayerCard>
      <i className="edge" aria-hidden="true" />
      <Visualizer />
      <NowPlaying />
      <SeekBar />
      <Controls />
      <Playlist />
      <TopBar />
    </PlayerCard>
  );
}
