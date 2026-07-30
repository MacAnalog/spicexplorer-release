"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface SliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (v: number) => void;
  /** Optional vertical marker value (rendered as labelled tick). */
  markerValue?: number;
  markerLabel?: string;
  className?: string;
}

/**
 * Custom track-style slider matching the Observatory design:
 * 28px container, 2px rail, 12px circular thumb, optional marker tick.
 */
export function Slider({
  value,
  min,
  max,
  step,
  onChange,
  markerValue,
  markerLabel = "target",
  className,
}: SliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);

  const span = max - min || 1;
  const pct = ((value - min) / span) * 100;
  const markerPct =
    markerValue !== undefined ? ((markerValue - min) / span) * 100 : null;

  const setFromClientX = useCallback(
    (clientX: number) => {
      const el = trackRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      let v = min + ratio * span;
      if (step) v = Math.round(v / step) * step;
      onChange(v);
    },
    [min, span, step, onChange],
  );

  useEffect(() => {
    if (!dragging) return;
    const onMove = (e: MouseEvent) => setFromClientX(e.clientX);
    const onUp = () => setDragging(false);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [dragging, setFromClientX]);

  return (
    <div
      ref={trackRef}
      className={cn("relative h-7 cursor-pointer select-none", className)}
      onMouseDown={(e) => {
        setDragging(true);
        setFromClientX(e.clientX);
      }}
    >
      <div className="absolute left-0 right-0 top-[13px] h-[2px] rounded-[1px] bg-border" />
      <div
        className="absolute top-[13px] h-[2px] rounded-[1px] bg-primary"
        style={{ left: 0, width: `${pct}%` }}
      />
      {markerPct !== null && (
        <div
          className="absolute top-2 h-3 w-px bg-muted"
          style={{ left: `${markerPct}%` }}
        >
          <span className="absolute left-1/2 top-3.5 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] text-muted">
            {markerLabel}
          </span>
        </div>
      )}
      <div
        className="absolute top-2 h-3 w-3 rounded-full border-2 border-primary bg-panel"
        style={{ left: `${pct}%`, transform: "translateX(-50%)" }}
      />
    </div>
  );
}
