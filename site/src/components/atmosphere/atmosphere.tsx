import { harmonicGroups, moteFields, type Mote } from "./ghost-geometry";
import { PaletteCrossfade } from "./palette-crossfade";
import "./atmosphere.css";

const harmonics = harmonicGroups();
const motes = moteFields();

/* Every layer shares the 1200x700 scene, anchored to the top centre. */
const scene = { viewBox: "0 0 1200 700", preserveAspectRatio: "xMidYMin slice", "aria-hidden": true } as const;

const GHOST_PATH =
  "M600 92C550 92 522 132 518 184C514 236 502 264 472 302C432 352 410 422 394 502C382 562 364 612 340 672C384 640 414 680 456 648C496 678 526 638 566 668C602 638 634 678 674 648C714 678 744 638 784 664C824 632 852 672 880 672C856 612 818 562 806 502C790 422 768 352 728 302C698 264 686 236 682 184C678 132 650 92 600 92Z";

function Motes({ motes }: { motes: Mote[] }) {
  return (
    <g>
      {motes.map((m, i) => (
        <circle key={i} cx={m.cx} cy={m.cy} r={m.r} fill="#dff3f5" opacity={m.opacity} />
      ))}
    </g>
  );
}

/** Classes of plain divs, back to front, that make a layer of the stack. */
const Layers = ({ names }: { names: string[] }) => names.map((n) => <div key={n} className={n} aria-hidden="true" />);

/**
 * The fixed, full-viewport background: one stack for the whole page, so there are no
 * section seams. The top half is the moonlit apparition in mist; the bottom half is a
 * blurred field of the playing track's colours (--f1..3), which also tint the mist.
 */
export function Atmosphere() {
  return (
    <div className="atmos" aria-hidden="true">
      <div className="atop">
        <svg className="ghost" {...scene}>
          <defs>
            <radialGradient id="moon" cx=".5" cy=".5" r=".5">
              <stop offset="0" stopColor="#d8f4ff" stopOpacity=".30" />
              <stop offset=".4" stopColor="#7d9fd0" stopOpacity=".12" />
              <stop offset="1" stopColor="#03050b" stopOpacity="0" />
            </radialGradient>
          </defs>
          <ellipse cx="860" cy="90" rx="420" ry="260" fill="url(#moon)" />
          <ellipse cx="600" cy="260" rx="300" ry="300" fill="url(#moon)" opacity=".45" />
        </svg>
        <PaletteCrossfade>
          <Layers names={["tint t1", "tint t2", "tint t3"]} />
        </PaletteCrossfade>
        <Layers names={["fg fg6"]} />
        <PaletteCrossfade>
          <Layers names={["fg fg1 fg1-c"]} />
        </PaletteCrossfade>
        <Layers names={["fg fg1 fg1-n", "fg fg2 fg2-n"]} />
        <PaletteCrossfade>
          <Layers names={["fg fg2 fg2-c"]} />
        </PaletteCrossfade>

        <svg className="layer appar" {...scene}>
          <defs>
            <radialGradient id="body" cx=".5" cy=".22" r=".7">
              <stop offset="0" stopColor="#e6f8ff" stopOpacity=".42" />
              <stop offset=".45" stopColor="#a7c9e8" stopOpacity=".16" />
              <stop offset="1" stopColor="#8fb3c8" stopOpacity="0" />
            </radialGradient>
            <path id="gpath" d={GHOST_PATH} />
            {/* Blur is baked into static layers; only their transform and opacity animate. */}
            <filter id="haze" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="28" />
            </filter>
            <filter id="hush" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="26" />
            </filter>
          </defs>
          <g filter="url(#haze)">
            <use href="#gpath" fill="url(#body)" />
          </g>
          <ellipse cx="600" cy="196" rx="46" ry="60" fill="#03050b" opacity=".6" filter="url(#hush)" />
        </svg>

        <svg className="layer harm" {...scene}>
          <defs>
            <linearGradient id="bodyfade" x1="0" y1="0" x2="0" y2="1">
              <stop offset=".35" stopColor="#fff" />
              <stop offset="1" stopColor="#fff" stopOpacity="0" />
            </linearGradient>
            <mask id="gm">
              <use href="#gpath" fill="url(#bodyfade)" />
            </mask>
          </defs>
          <g mask="url(#gm)" opacity=".32">
            {harmonics.map((lines, i) => (
              <g key={i} className={`hs hs${i}`}>
                {lines.map((l) => (
                  <path
                    key={l.d}
                    d={l.d}
                    fill="none"
                    stroke="#e3f6f7"
                    strokeOpacity={l.opacity}
                    strokeWidth={l.width}
                  />
                ))}
              </g>
            ))}
          </g>
        </svg>

        <svg className="layer dust d1" {...scene}>
          <Motes motes={motes[0]} />
        </svg>
        <svg className="layer dust d2" {...scene}>
          <Motes motes={motes[1]} />
        </svg>
        <Layers names={["mist m1", "mist m2", "mist m3"]} />
        <PaletteCrossfade>
          <Layers names={["fg fg3 fg3-c"]} />
        </PaletteCrossfade>
        <Layers names={["fg fg3 fg3-n"]} />
        <PaletteCrossfade>
          <Layers names={["fg fg4 fg4-c"]} />
        </PaletteCrossfade>
        <Layers names={["fg fg4 fg4-n", "wisp", "wisp w2", "wisp w3"]} />
        <PaletteCrossfade>
          <Layers names={["rise"]} />
        </PaletteCrossfade>
      </div>

      <div className="abot">
        <div className="blobs">
          <PaletteCrossfade>
            <Layers names={["blob b1", "blob b2", "blob b3"]} />
          </PaletteCrossfade>
        </div>
        <PaletteCrossfade>
          <Layers names={["sink", "bf bf1 bf1-c"]} />
        </PaletteCrossfade>
        <Layers names={["bf bf1 bf1-n", "bf bf2 bf2-n"]} />
        <PaletteCrossfade>
          <Layers names={["bf bf2 bf2-c"]} />
        </PaletteCrossfade>
        <Layers names={["bf bf3 bf3-n"]} />
        <PaletteCrossfade>
          <Layers names={["bf bf3 bf3-c"]} />
        </PaletteCrossfade>
      </div>
    </div>
  );
}
