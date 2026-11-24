import { Atmosphere } from "@/components/atmosphere/atmosphere";
import { Badge } from "@/components/brand/badge";
import { GithubBadge } from "@/components/brand/github-badge";
import { Logotype } from "@/components/brand/logotype";
import { Footer } from "@/components/footer";
import { Player } from "@/components/player/player";
import { PlayerProvider } from "@/components/player/player-context";
import { tracks } from "@/lib/tracks";

type SpectrePageProps = {
  /** Index of the track to open with. */
  initial?: number;
  /** Start it at once (track links). */
  autoplay?: boolean;
};

/** The whole site: a brand banner over a fixed ghostly backdrop, and the player. */
export function SpectrePage({ initial = 0, autoplay = false }: SpectrePageProps) {
  return (
    <PlayerProvider tracks={tracks} initial={initial} autoplay={autoplay}>
      <Atmosphere />
      <header className="relative isolate grid min-h-[clamp(340px,60svh,660px)] items-end overflow-x-clip">
        <GithubBadge />
        <div className="relative z-1 mx-auto w-full max-w-[960px] px-[max(16px,env(safe-area-inset-left,0px))] pt-10 pb-[calc(var(--lift)+8px)]">
          <Badge />
          <Logotype />
        </div>
      </header>
      <main className="relative isolate flow-root pb-14">
        <Player />
        <Footer />
      </main>
    </PlayerProvider>
  );
}
