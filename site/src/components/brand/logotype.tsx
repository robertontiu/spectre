import { GlitchFrame } from "./glitch-frame";
import "./brand.css";

/* Each layer covers the same box: the backlight (lgl) sits in flow and sets the size,
   the others are absolutely stacked over it. */
const box = { viewBox: "-60 -30 1400 390", "aria-hidden": true } as const;
const region = { filterUnits: "userSpaceOnUse", x: "-60", y: "-30", width: "1400", height: "390" } as const;

/** Displaced, softened copy of the letters: smoke instead of a clean edge. */
function Smoke({
  id,
  frequency,
  octaves,
  seed,
  scale,
  blur,
}: {
  id: string;
  frequency: string;
  octaves: number;
  seed: number;
  scale: number;
  blur: number;
}) {
  return (
    <filter id={id} {...region}>
      <feTurbulence type="fractalNoise" baseFrequency={frequency} numOctaves={octaves} seed={seed} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={scale} xChannelSelector="R" yChannelSelector="G" />
      <feGaussianBlur stdDeviation={blur} />
    </filter>
  );
}

/**
 * SPECTRE as dark smoky strokes against a cold backlight, faded to ~80%, with a wisp
 * rising off the letters and fog drifting at their feet. The blurred and ghost copies
 * (lgb, lgg) stay invisible until GlitchFrame plays a glitch.
 */
export function Logotype() {
  return (
    <GlitchFrame label="Spectre">
      <svg className="logo lgl" {...box}>
        <defs>
          <g id="word" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path
              transform="translate(40 70)"
              d="M128 42C112 18 88 13 66 13C34 13 14 32 14 56C14 84 40 94 70 100C102 106 128 118 128 146C128 172 106 187 74 187C48 187 24 177 12 154"
            />
            <path transform="translate(216 70)" d="M18 187V13H78C110 13 130 34 130 62C130 90 110 110 78 110H18" />
            <path transform="translate(392 70)" d="M128 13H18V187H128M18 100H108" />
            <path
              transform="translate(568 70)"
              d="M134 50C120 26 98 13 72 13C38 13 13 50 13 100C13 150 38 187 72 187C98 187 120 174 134 150"
            />
            <path transform="translate(744 70)" d="M8 13H136M72 13V187" />
            <path
              transform="translate(920 70)"
              d="M18 187V13H78C110 13 130 34 130 60C130 86 110 106 78 106H18M76 106L132 187"
            />
            <path transform="translate(1096 70)" d="M128 13H18V187H128M18 100H108" />
          </g>
          <linearGradient id="unev" x1="0" y1="1" x2="1" y2="0">
            <stop offset="0" stopColor="#555" />
            <stop offset=".55" stopColor="#a0a0a0" />
            <stop offset="1" stopColor="#fff" />
          </linearGradient>
          <mask id="unevm" maskUnits="userSpaceOnUse" x="-60" y="-30" width="1400" height="390">
            <rect x="-60" y="-30" width="1400" height="390" fill="url(#unev)" />
          </mask>
          <radialGradient id="lfl">
            <stop offset="0" stopColor="#e2f6fc" stopOpacity=".42" />
            <stop offset="1" stopColor="#e2f6fc" stopOpacity="0" />
          </radialGradient>
          <filter id="lhalo" {...region}>
            <feGaussianBlur stdDeviation="14" />
          </filter>
          <Smoke id="lrim" frequency="0.014 0.035" octaves={2} seed={5} scale={22} blur={5} />
        </defs>
        <ellipse cx="990" cy="92" rx="300" ry="112" fill="url(#lfl)" />
        <g mask="url(#unevm)">
          <use href="#word" stroke="#9fcfe2" strokeWidth="58" opacity=".5" filter="url(#lhalo)" />
          <use href="#word" stroke="#e0f6fc" strokeWidth="40" opacity=".78" filter="url(#lrim)" />
        </g>
      </svg>

      <svg className="logo lgd" {...box}>
        <defs>
          <linearGradient id="ldk" x1="0" y1="80" x2="0" y2="260" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#0b121d" stopOpacity=".92" />
            <stop offset=".5" stopColor="#070c15" stopOpacity=".9" />
            <stop offset=".8" stopColor="#16222f" stopOpacity=".7" />
            <stop offset="1" stopColor="#2a3a4a" stopOpacity=".3" />
          </linearGradient>
          <Smoke id="lsm1" frequency="0.011 0.028" octaves={3} seed={5} scale={34} blur={6} />
          <Smoke id="lsm2" frequency="0.02 0.05" octaves={3} seed={8} scale={16} blur={2.4} />
          <Smoke id="lcore" frequency="0.03 0.06" octaves={2} seed={3} scale={6} blur={1.3} />
        </defs>
        <use href="#word" stroke="#070c15" strokeWidth="40" opacity=".42" filter="url(#lsm1)" />
        <use href="#word" stroke="url(#ldk)" strokeWidth="29" opacity=".8" filter="url(#lsm2)" />
        <use href="#word" stroke="url(#ldk)" strokeWidth="18" opacity=".85" filter="url(#lcore)" />
      </svg>

      <svg className="logo lgw" {...box}>
        <defs>
          <Smoke id="lwsp" frequency="0.006 0.05" octaves={2} seed={2} scale={80} blur={3.5} />
          <linearGradient id="lwg" x1="0" y1="60" x2="0" y2="200" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#cfe9f2" stopOpacity=".9" />
            <stop offset="1" stopColor="#cfe9f2" stopOpacity="0" />
          </linearGradient>
        </defs>
        <use
          href="#word"
          stroke="url(#lwg)"
          strokeWidth="9"
          opacity=".32"
          filter="url(#lwsp)"
          transform="translate(0 -18)"
        />
      </svg>

      <svg className="logo lgb" {...box}>
        <defs>
          <filter id="lbw" {...region}>
            <feGaussianBlur stdDeviation="20" />
          </filter>
          <Smoke id="lbd" frequency="0.011 0.028" octaves={3} seed={5} scale={40} blur={8} />
        </defs>
        <use href="#word" stroke="#9fcfe2" strokeWidth="64" opacity=".45" filter="url(#lbw)" />
        <use href="#word" stroke="#0a111b" strokeWidth="32" opacity=".9" filter="url(#lbd)" />
      </svg>

      <svg className="logo lgg" {...box}>
        <defs>
          <Smoke id="lgh" frequency="0.015 0.04" octaves={3} seed={9} scale={28} blur={3.5} />
        </defs>
        <use href="#word" stroke="#bfe3ee" strokeWidth="26" opacity=".5" filter="url(#lgh)" />
      </svg>

      <svg className="logo lgf" {...box}>
        <defs>
          <radialGradient id="lfg">
            <stop offset="0" stopColor="#7d97a9" stopOpacity=".34" />
            <stop offset="1" stopColor="#7d97a9" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g className="lfog1">
          <ellipse cx="330" cy="250" rx="360" ry="44" fill="url(#lfg)" />
          <ellipse cx="940" cy="262" rx="340" ry="40" fill="url(#lfg)" />
        </g>
        <g className="lfog2">
          <ellipse cx="640" cy="238" rx="560" ry="34" fill="url(#lfg)" opacity=".7" />
        </g>
      </svg>
    </GlitchFrame>
  );
}
