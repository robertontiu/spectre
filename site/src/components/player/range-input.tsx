import { cx } from "@/lib/cx";
import type { ComponentProps, CSSProperties } from "react";

type RangeInputProps = Omit<ComponentProps<"input">, "type" | "style"> & {
  /** Filled part of the track, 0-1 (drawn by WebKit; Firefox uses ::-moz-range-progress). */
  progress: number;
};

/** A slim range slider whose filled part takes the track's accent colour. */
export function RangeInput({ progress, className, ...props }: RangeInputProps) {
  const style = { "--p": `${(progress * 100).toFixed(2)}%` } as CSSProperties;
  return <input type="range" className={cx("range", className)} style={style} {...props} />;
}
