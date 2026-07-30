// SVG-rendering helpers for parsed xschem files.
// Pure functions: input is the parsed AST, output is SVG element data we can map
// onto JSX in the React viewer.

import type { XschemFile, Instance } from "./types";

// xschem layer → stroke color. Approximates the default light-on-dark palette;
// fine-tune as needed. Background is handled by the viewer (dark navy by default).
const LAYER_COLOR: Record<number, string> = {
  0: "#000000",
  1: "#d8d8d8",
  2: "#22d3ee", // wires (cyan)
  3: "#f59e0b",
  4: "#4ade80", // symbol lines (green)
  5: "#facc15", // pin markers (yellow)
  6: "#60a5fa",
  7: "#e879f9",
  8: "#a78bfa",
  9: "#fb923c",
  10: "#34d399",
  11: "#fca5a5",
  12: "#fde68a",
  13: "#a3e635",
  14: "#c084fc",
  15: "#94a3b8",
};

export function layerColor(n: number): string {
  return LAYER_COLOR[n] ?? "#e5e7eb";
}

export interface BBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

function unionBox(a: BBox | null, b: BBox): BBox {
  if (a === null) return b;
  const x1 = Math.min(a.x, b.x);
  const y1 = Math.min(a.y, b.y);
  const x2 = Math.max(a.x + a.w, b.x + b.w);
  const y2 = Math.max(a.y + a.h, b.y + b.h);
  return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
}

/** Bounding box of a parsed file in its local coordinate frame. */
export function fileBBox(file: XschemFile): BBox {
  let bb: BBox | null = null;
  for (const p of file.primitives) {
    if (p.kind === "line" || p.kind === "box") {
      const x = Math.min(p.x1, p.x2);
      const y = Math.min(p.y1, p.y2);
      const w = Math.abs(p.x2 - p.x1);
      const h = Math.abs(p.y2 - p.y1);
      bb = unionBox(bb, { x, y, w, h });
    } else if (p.kind === "polygon") {
      for (const pt of p.points) {
        bb = unionBox(bb, { x: pt.x, y: pt.y, w: 0, h: 0 });
      }
    } else if (p.kind === "arc") {
      bb = unionBox(bb, {
        x: p.cx - p.r,
        y: p.cy - p.r,
        w: 2 * p.r,
        h: 2 * p.r,
      });
    }
  }
  for (const w of file.wires) {
    const x = Math.min(w.x1, w.x2);
    const y = Math.min(w.y1, w.y2);
    bb = unionBox(bb, { x, y, w: Math.abs(w.x2 - w.x1), h: Math.abs(w.y2 - w.y1) });
  }
  for (const t of file.texts) {
    // Texts can extend beyond their (x, y) but we don't know font metrics here;
    // give them a small footprint so they affect the box mildly.
    bb = unionBox(bb, { x: t.x, y: t.y, w: 16 * t.hsize, h: 16 * t.vsize });
  }
  for (const c of file.instances) {
    // Symbol size unknown at parse time; rendering will expand the box when symbols are inlined.
    bb = unionBox(bb, { x: c.x - 20, y: c.y - 20, w: 40, h: 40 });
  }
  return bb ?? { x: 0, y: 0, w: 100, h: 100 };
}

/** SVG transform string for an xschem instance. xschem applies flip *before* rotate. */
export function instanceTransform(inst: Instance): string {
  const parts: string[] = [`translate(${inst.x}, ${inst.y})`];
  if (inst.rotate) {
    parts.push(`rotate(${-inst.rotate * 90})`); // SVG rotate is CCW positive; xschem rot is CW.
  }
  if (inst.flip) {
    parts.push("scale(-1, 1)");
  }
  return parts.join(" ");
}

/** True if a symbol file is marked as a subcircuit (has a navigable schematic). */
export function isSubcircuit(sym: XschemFile): boolean {
  return (sym.kindAttrs["type"] ?? "") === "subcircuit";
}
