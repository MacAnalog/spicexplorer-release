"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Persisted, drag-adjustable size (px — width OR height) for a shell rail/bar.
 * SSR-safe: the first render uses `initial`; the stored value (localStorage,
 * per `key`) applies after mount. The setter clamps to [min, max] and persists.
 */
export function useRailSize(
  key: string,
  initial: number,
  min: number,
  max: number,
): [number, (n: number) => void] {
  const [size, setSize] = useState(initial);
  useEffect(() => {
    const stored = Number(window.localStorage.getItem(key));
    if (Number.isFinite(stored) && stored >= min && stored <= max) setSize(stored);
  }, [key, min, max]);
  const set = useCallback(
    (n: number) => {
      const clamped = Math.round(Math.min(max, Math.max(min, n)));
      setSize(clamped);
      try {
        window.localStorage.setItem(key, String(clamped));
      } catch {
        // storage full/blocked — the session still resizes, it just won't persist
      }
    },
    [key, min, max],
  );
  return [size, set];
}

/** Back-compat alias (earlier call sites named it by width). */
export const useRailWidth = useRailSize;

type Edge = "left" | "right" | "top" | "bottom";

interface ResizeHandleProps {
  /** Which edge of the panel the handle sits on (the edge the user drags). */
  edge: Edge;
  /** The panel's current size — keyboard steps are relative to it. */
  size: number;
  /** Map the pointer position (clientX for left/right, clientY for top/bottom)
   *  to the panel's new size (e.g. `x − rail.left` for a left rail). */
  compute: (clientXY: number) => number;
  onSize: (n: number) => void;
  /** Double-click restores this size. */
  resetTo?: number;
  label?: string;
}

/**
 * The drag strip on a panel's edge. The owning panel must be `relative`; its
 * size comes from `useRailSize` via an inline style. Pointer-captured drag,
 * arrow keys (16px steps toward/away per the edge), double-click to reset.
 * Content that scrolls must live in an inner wrapper, or the handle scrolls
 * away with it.
 */
export function ResizeHandle({
  edge,
  size,
  compute,
  onSize,
  resetTo,
  label = "Resize panel",
}: ResizeHandleProps) {
  const dragging = useRef(false);
  const horizontal = edge === "left" || edge === "right";
  return (
    <div
      role="separator"
      aria-orientation={horizontal ? "vertical" : "horizontal"}
      aria-label={label}
      tabIndex={0}
      onPointerDown={(e) => {
        dragging.current = true;
        e.currentTarget.setPointerCapture(e.pointerId);
        e.preventDefault();
      }}
      onPointerMove={(e) => {
        if (dragging.current) onSize(compute(horizontal ? e.clientX : e.clientY));
      }}
      onPointerUp={(e) => {
        dragging.current = false;
        e.currentTarget.releasePointerCapture(e.pointerId);
      }}
      onDoubleClick={resetTo != null ? () => onSize(resetTo) : undefined}
      onKeyDown={(e) => {
        // Arrows move the EDGE: → grows a right-edge handle / shrinks a left-edge
        // one; ↓ grows a bottom-edge handle / shrinks a top-edge one.
        const dir =
          (horizontal && e.key === "ArrowRight") || (!horizontal && e.key === "ArrowDown")
            ? 1
            : (horizontal && e.key === "ArrowLeft") || (!horizontal && e.key === "ArrowUp")
              ? -1
              : 0;
        if (dir) {
          e.preventDefault();
          onSize(size + 16 * dir * (edge === "right" || edge === "bottom" ? 1 : -1));
        }
      }}
      className={cn(
        "absolute z-10 touch-none outline-hidden",
        "hover:bg-primary/25 focus-visible:bg-primary/25 active:bg-primary/40",
        horizontal
          ? "inset-y-0 w-[5px] cursor-col-resize"
          : "inset-x-0 h-[5px] cursor-row-resize",
        edge === "right" && "right-[-2px]",
        edge === "left" && "left-[-2px]",
        edge === "top" && "top-[-2px]",
        edge === "bottom" && "bottom-[-2px]",
      )}
    />
  );
}
