import type { MetadataRoute } from "next";
import { SITE_URL, trackPath } from "@/lib/site";
import { tracks } from "@/lib/tracks";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: SITE_URL, changeFrequency: "weekly", priority: 1 },
    ...tracks.map((t) => ({ url: `${SITE_URL}${trackPath(t)}`, changeFrequency: "monthly" as const, priority: 0.8 })),
  ];
}
