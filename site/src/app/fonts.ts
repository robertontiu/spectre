import localFont from "next/font/local";

/* Self-hosted variable fonts from Fontsource (SIL OFL, see src/fonts/OFL-*.txt). The
   latin-ext files are separate families later in the stack, so the browser only loads
   them for characters such as the ī in "Līdz rītam". */
export const syne = localFont({
  src: "../fonts/syne-latin-wght-normal.woff2",
  weight: "400 800",
  variable: "--font-syne",
  adjustFontFallback: false,
});
export const syneExt = localFont({
  src: "../fonts/syne-latin-ext-wght-normal.woff2",
  weight: "400 800",
  variable: "--font-syne-ext",
  adjustFontFallback: false,
  preload: false,
});
export const manrope = localFont({
  src: "../fonts/manrope-latin-wght-normal.woff2",
  weight: "200 800",
  variable: "--font-manrope",
  adjustFontFallback: false,
});
export const manropeExt = localFont({
  src: "../fonts/manrope-latin-ext-wght-normal.woff2",
  weight: "200 800",
  variable: "--font-manrope-ext",
  adjustFontFallback: false,
  preload: false,
});

export const fontVariables = [syne, syneExt, manrope, manropeExt].map((f) => f.variable).join(" ");
