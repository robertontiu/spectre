import { Atmosphere } from "@/components/atmosphere/atmosphere";
import { Badge } from "@/components/brand/badge";
import { GithubBadge } from "@/components/brand/github-badge";
import { HeroMotion } from "@/components/brand/hero-motion";
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

/**
 * The whole site: a brand banner over a fixed ghostly backdrop, and the player. Scrolling
 * fades the title and carries the badge onto the player card's edge (HeroMotion).
 */
export function SpectrePage({ initial = 0, autoplay = false }: SpectrePageProps) {
  return (
    <PlayerProvider tracks={tracks} initial={initial} autoplay={autoplay}>
      <Atmosphere />
      {/* Above the player (z-2), so the badge can land on the card's edge; the header lets
          pointers through to the card it overlaps (only the GitHub pill takes them). */}
      <header className="pointer-events-none relative isolate z-2 grid min-h-[clamp(340px,60svh,660px)] items-end overflow-x-clip">
        <GithubBadge />
        <div className="relative z-1 mx-auto w-full max-w-[960px] px-[max(16px,env(safe-area-inset-left,0px))] pt-10 pb-[calc(var(--lift)+8px)]">
          <HeroMotion badge={<Badge />} title={<Logotype />} />
        </div>
      </header>
      <main className="relative isolate flow-root pb-14">
        <Player />
        <Footer />
      </main>
    </PlayerProvider>
  );
}
