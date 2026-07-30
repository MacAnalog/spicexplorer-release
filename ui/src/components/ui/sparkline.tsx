/**
 * Tiny inline-SVG sparkline for the run-history rail. No chart lib — just a
 * normalized polyline so it stays cheap to render many of them in a list.
 */
interface SparklineProps {
  values: number[];
  width?: number;
  height?: number;
  className?: string;
  /** Stroke color; defaults to the indigo accent. */
  color?: string;
}

export function Sparkline({
  values,
  width = 96,
  height = 22,
  className,
  color = "#4f46e5",
}: SparklineProps) {
  const pts = values.filter((v) => Number.isFinite(v));
  if (pts.length < 2) {
    return (
      <svg width={width} height={height} className={className} aria-hidden>
        <line
          x1={0}
          y1={height - 1}
          x2={width}
          y2={height - 1}
          stroke="#e4e4e7"
          strokeWidth={1}
        />
      </svg>
    );
  }

  const min = Math.min(...pts);
  const max = Math.max(...pts);
  const span = max - min || 1;
  const pad = 1.5;
  const x = (i: number) => (i / (pts.length - 1)) * (width - pad * 2) + pad;
  // Lower score is better, so draw min at the top for an intuitive "descending = improving" look.
  const y = (v: number) => height - pad - ((max - v) / span) * (height - pad * 2);

  const d = pts.map((v, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");

  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden
    >
      <path d={d} fill="none" stroke={color} strokeWidth={1.25} strokeLinejoin="round" />
    </svg>
  );
}
