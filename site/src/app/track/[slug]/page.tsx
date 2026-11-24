import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SpectrePage } from "@/components/spectre-page";
import { formatTime } from "@/lib/format";
import { SITE_NAME, SITE_URL, audioPath, trackPath, trackSlug } from "@/lib/site";
import { tracks } from "@/lib/tracks";

/** Every track has a page, built at compile time; other slugs are 404s. */
export const dynamicParams = false;

export function generateStaticParams() {
  return tracks.map((t) => ({ slug: trackSlug(t) }));
}

const findTrack = async (params: PageProps<"/track/[slug]">["params"]) => {
  const { slug } = await params;
  const index = tracks.findIndex((t) => trackSlug(t) === slug);
  return index < 0 ? null : { index, track: tracks[index] };
};

export async function generateMetadata({ params }: PageProps<"/track/[slug]">): Promise<Metadata> {
  const found = await findTrack(params);
  if (!found) return {};
  const { track } = found;
  const title = `Spectre – ${track.title}`;
  const description = `${track.genre} by Spectre, ${track.bpm} BPM, ${formatTime(Math.round(track.duration))}. Feeling: ${track.feeling}. ${track.style}.`;
  return {
    title: { absolute: title },
    description,
    alternates: { canonical: trackPath(track) },
    openGraph: {
      type: "music.song",
      url: trackPath(track),
      siteName: SITE_NAME,
      title,
      description,
      locale: "en",
      duration: Math.round(track.duration),
      audio: [{ url: new URL(audioPath(track), SITE_URL).href, type: "audio/mpeg" }],
    },
    twitter: { card: "summary_large_image", title, description },
  };
}

/** A track link opens the player on that track, ready to play (no autoplay). */
export default async function TrackPage({ params }: PageProps<"/track/[slug]">) {
  const found = await findTrack(params);
  if (!found) notFound();
  return <SpectrePage initial={found.index} />;
}
