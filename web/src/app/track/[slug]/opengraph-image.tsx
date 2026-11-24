import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { fieldTone, paletteFrom, tone, type RGB } from "@/lib/color";
import { formatTime } from "@/lib/format";
import { trackSlug } from "@/lib/site";
import { tracks } from "@/lib/tracks";

export const alt = "Spectre: the track's title over a ghostly field in its colours";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export function generateStaticParams() {
  return tracks.map((t) => ({ slug: trackSlug(t) }));
}

const fonts = join(process.cwd(), "src/fonts/og");
const [syne, syneExt, manrope, manropeExt, badge] = await Promise.all([
  readFile(join(fonts, "syne-latin-800-normal.woff")),
  readFile(join(fonts, "syne-latin-ext-800-normal.woff")),
  readFile(join(fonts, "manrope-latin-600-normal.woff")),
  readFile(join(fonts, "manrope-latin-ext-600-normal.woff")),
  readFile(join(process.cwd(), "src/assets/badge.svg"), "base64"),
]);

const css = (c: RGB, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;

/** The track's share card: its title over a blurred field of its own colours. */
export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const track = tracks.find((t) => trackSlug(t) === slug) ?? tracks[0];
  const [p1, p2, p3] = paletteFrom(track.colors);
  const [f1, f2, f3] = [fieldTone(p1), fieldTone(p2), fieldTone(p3)];

  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        padding: "0 86px",
        gap: 56,
        color: "#eef3f5",
        backgroundColor: "#05070d",
        backgroundImage: [
          `radial-gradient(70% 85% at 12% 108%, ${css(f1, 0.95)}, transparent)`,
          `radial-gradient(60% 80% at 92% 100%, ${css(f2, 0.8)}, transparent)`,
          `radial-gradient(95% 70% at 50% 118%, ${css(f3)}, transparent)`,
          `radial-gradient(45% 55% at 75% 0%, rgba(216,244,255,.16), transparent)`,
          "linear-gradient(180deg, #03050b, #081020 55%, #05070d)",
        ].join(","),
      }}
    >
      <img src={`data:image/svg+xml;base64,${badge}`} width={250} height={250} alt="" />
      <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <div
          style={{ fontFamily: "Manrope, Manrope Ext", fontSize: 30, letterSpacing: 6, color: "rgba(223,243,245,.7)" }}
        >
          SPECTRE
        </div>
        <div
          style={{
            fontFamily: "Syne, Syne Ext",
            fontSize: track.title.length > 14 ? 84 : 104,
            lineHeight: 1.02,
            marginTop: 14,
          }}
        >
          {track.title}
        </div>
        <div style={{ fontFamily: "Manrope, Manrope Ext", fontSize: 32, marginTop: 26, color: css(tone(p2)) }}>
          {`${track.bpm} BPM · ${track.genre} · ${formatTime(Math.round(track.duration))}`}
        </div>
      </div>
    </div>,
    {
      ...size,
      fonts: [
        { name: "Syne", data: syne, weight: 800 },
        { name: "Syne Ext", data: syneExt, weight: 800 },
        { name: "Manrope", data: manrope, weight: 600 },
        { name: "Manrope Ext", data: manropeExt, weight: 600 },
      ],
    },
  );
}
