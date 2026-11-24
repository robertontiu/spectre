import "./brand.css";

const WRAITH =
  "M60 23C66.5 25 71.5 31 73.5 38.5C75.3 45.5 75.2 52 74 58C80.5 61 87.5 64.5 91 70.5C93 75 97 86 99 100L90.5 108L86.5 100.5L81.5 112L76 102L70 114.5L64 103L58 115.5L52 103L46 113.5L40.5 102L35 110L21 100C23 86 27 75 34.5 70.5C38.5 64.5 45 61 50.8 58C49.6 52 49.6 45.5 51.5 38.5C53.5 31 54.5 25 60 23Z";

const art = { viewBox: "0 0 120 120", "aria-hidden": true } as const;

/**
 * The tonal hooded wraith, carved out by a cold backlight with an eclipse-like corona and
 * two eye glints. The same drawing is the favicon (app/icon.svg).
 */
export function Badge() {
  return (
    <div className="badge" aria-hidden="true">
      {/* Each moving part is its own SVG, so the motion runs on the compositor; animating
          groups inside one SVG repainted the badge every frame. */}
      <svg className="corona" {...art}>
        <defs>
          <radialGradient id="bco">
            <stop offset=".56" stopColor="#bfe9f5" stopOpacity="0" />
            <stop offset=".68" stopColor="#e0f6fc" stopOpacity=".9" />
            <stop offset=".77" stopColor="#9fcfe2" stopOpacity=".42" />
            <stop offset=".88" stopColor="#4a6f88" stopOpacity=".1" />
            <stop offset="1" stopColor="#4a6f88" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bfl">
            <stop offset="0" stopColor="#e2f6fc" stopOpacity=".6" />
            <stop offset="1" stopColor="#e2f6fc" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bdk">
            <stop offset="0" stopColor="#03050a" />
            <stop offset=".7" stopColor="#020307" />
            <stop offset=".84" stopColor="#03050b" stopOpacity=".55" />
            <stop offset="1" stopColor="#05070d" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bbl" cy=".42" r=".55">
            <stop offset="0" stopColor="#e6f8fd" stopOpacity=".95" />
            <stop offset=".35" stopColor="#a9d6e6" stopOpacity=".5" />
            <stop offset=".7" stopColor="#4f7890" stopOpacity=".16" />
            <stop offset="1" stopColor="#4f7890" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="bwr" x1="0" y1="23" x2="0" y2="115" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#0a1019" />
            <stop offset=".5" stopColor="#03050a" />
            <stop offset=".62" stopColor="#03050a" stopOpacity=".88" />
            <stop offset=".84" stopColor="#03050a" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="bfv">
            <stop offset="0" stopColor="#000" />
            <stop offset=".7" stopColor="#000" stopOpacity=".8" />
            <stop offset="1" stopColor="#000" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bey">
            <stop offset="0" stopColor="#e8f8ff" stopOpacity=".95" />
            <stop offset=".45" stopColor="#9fd4ea" stopOpacity=".35" />
            <stop offset="1" stopColor="#9fd4ea" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="beh">
            <stop offset="0" stopColor="#9fd4ea" stopOpacity=".3" />
            <stop offset="1" stopColor="#9fd4ea" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bfg">
            <stop offset="0" stopColor="#7d97a9" stopOpacity=".3" />
            <stop offset="1" stopColor="#7d97a9" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="60" cy="60" r="60" fill="url(#bco)" />
        <ellipse cx="80" cy="34" rx="30" ry="24" fill="url(#bfl)" />
        <ellipse cx="36" cy="90" rx="18" ry="14" fill="url(#bfl)" opacity=".4" />
      </svg>
      <svg {...art}>
        <circle cx="60" cy="60" r="46" fill="url(#bdk)" />
      </svg>
      <svg className="backl" {...art}>
        <ellipse cx="60" cy="50" rx="36" ry="38" fill="url(#bbl)" />
      </svg>
      <svg {...art}>
        {/* The hood: two soft rims, then the body. */}
        <path d={WRAITH} fill="none" stroke="url(#bwr)" strokeWidth="5" strokeOpacity=".3" strokeLinejoin="round" />
        <path d={WRAITH} fill="none" stroke="url(#bwr)" strokeWidth="2.4" strokeOpacity=".55" strokeLinejoin="round" />
        <path d={WRAITH} fill="url(#bwr)" />
        <ellipse cx="60" cy="46" rx="9" ry="12" fill="url(#bfv)" />
      </svg>
      <svg className="glint" {...art}>
        <ellipse cx="60" cy="46.5" rx="8" ry="3" fill="url(#beh)" />
        <ellipse cx="56.6" cy="46.6" rx="2.7" ry="1.25" fill="url(#bey)" transform="rotate(8 56.6 46.6)" />
        <ellipse cx="63.4" cy="46.6" rx="2.7" ry="1.25" fill="url(#bey)" transform="rotate(-8 63.4 46.6)" />
      </svg>
      <svg className="fog" {...art}>
        <ellipse cx="44" cy="98" rx="40" ry="11" fill="url(#bfg)" />
        <ellipse cx="80" cy="104" rx="36" ry="10" fill="url(#bfg)" />
      </svg>
    </div>
  );
}
