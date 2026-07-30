"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import type { XschemFile, Instance } from "@/lib/xschem/types";
import {
  layerColor,
  fileBBox,
  instanceTransform,
  isSubcircuit,
  type BBox,
} from "@/lib/xschem/render";

interface Props {
  sch: XschemFile;
  symbols: Map<string, XschemFile>;
  /** Called when the user clicks an instance whose symbol is a subcircuit. */
  onNavigateInto?: (inst: Instance) => void;
  /** Symbol refs whose .sch counterpart is known to exist (enables hover affordance). */
  navigableSymrefs?: Set<string>;
}

const PADDING = 40;
const MIN_VIEW = 50;
const MAX_VIEW = 200_000;

interface InspectorState {
  inst: Instance;
  clientX: number;
  clientY: number;
}

export function SchematicViewer({
  sch,
  symbols,
  onNavigateInto,
  navigableSymrefs,
}: Props) {
  // Overall bbox = schematic primitives + each instance's symbol bbox (after rotate/flip)
  const initialBox = useMemo<BBox>(() => computeOverallBBox(sch, symbols), [sch, symbols]);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [view, setView] = useState<BBox>(() => padBox(initialBox, PADDING));
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const [inspector, setInspector] = useState<InspectorState | null>(null);
  const dragState = useRef<{ x: number; y: number; view: BBox } | null>(null);

  // Reset view (and close any open inspector) when we navigate to a different schematic.
  useEffect(() => {
    setView(padBox(initialBox, PADDING));
    setInspector(null);
  }, [initialBox]);

  // Close inspector with Escape.
  useEffect(() => {
    if (!inspector) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setInspector(null);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [inspector]);

  function clientToSvg(clientX: number, clientY: number): { x: number; y: number } {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const rect = svg.getBoundingClientRect();
    const px = (clientX - rect.left) / rect.width;
    const py = (clientY - rect.top) / rect.height;
    return { x: view.x + px * view.w, y: view.y + py * view.h };
  }

  function onWheel(e: React.WheelEvent) {
    e.preventDefault();
    const factor = Math.exp(e.deltaY * 0.0015);
    const newW = clamp(view.w * factor, MIN_VIEW, MAX_VIEW);
    const newH = clamp(view.h * factor, MIN_VIEW, MAX_VIEW);
    const { x: cx, y: cy } = clientToSvg(e.clientX, e.clientY);
    // Keep the cursor pinned to the same model-space point.
    const ratioX = (cx - view.x) / view.w;
    const ratioY = (cy - view.y) / view.h;
    setView({
      x: cx - ratioX * newW,
      y: cy - ratioY * newH,
      w: newW,
      h: newH,
    });
  }

  function onMouseDown(e: React.MouseEvent) {
    if (e.button !== 0 && e.button !== 1) return;
    // Click on the background (the SVG itself, not an instance) closes the inspector.
    if (e.target === svgRef.current) setInspector(null);
    dragState.current = { x: e.clientX, y: e.clientY, view };
  }
  function onMouseMove(e: React.MouseEvent) {
    if (!dragState.current || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const dx = ((e.clientX - dragState.current.x) / rect.width) * dragState.current.view.w;
    const dy = ((e.clientY - dragState.current.y) / rect.height) * dragState.current.view.h;
    setView({
      x: dragState.current.view.x - dx,
      y: dragState.current.view.y - dy,
      w: dragState.current.view.w,
      h: dragState.current.view.h,
    });
  }
  function endDrag() {
    dragState.current = null;
  }

  function resetView() {
    setView(padBox(initialBox, PADDING));
  }

  return (
    <div className="relative h-full w-full">
      <svg
        ref={svgRef}
        className="h-full w-full cursor-grab bg-[#0b1220] active:cursor-grabbing"
        viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={endDrag}
        onMouseLeave={endDrag}
      >
        {/* Top-level wires */}
        {sch.wires.map((w, i) => (
          <line
            key={`w${i}`}
            x1={w.x1}
            y1={w.y1}
            x2={w.x2}
            y2={w.y2}
            stroke={layerColor(2)}
            strokeWidth={2}
            vectorEffect="non-scaling-stroke"
          />
        ))}

        {/* Top-level primitives */}
        {sch.primitives.map((p, i) => renderPrimitive(p, `p${i}`))}

        {/* Top-level texts (no parent rotation, so just render at their own rot/flip) */}
        {sch.texts.map((t, i) => renderTextReadable(t, 0, 0, t.x, t.y, `t${i}`))}

        {/* Instances: geometry inside a transformed group, text rendered as siblings so we
            can counter-rotate it for readability (matching xschem's auto-rotate behavior). */}
        {sch.instances.map((inst, idx) => {
          const sym = symbols.get(inst.symref);
          const navigable = isInstanceNavigable(inst, sym, navigableSymrefs);
          const labelName = inst.attrs["name"] ?? "";
          const labelTitle = `${inst.symref}${labelName ? ` — ${labelName}` : ""}${navigable ? " (subcircuit — click to descend; right-click to inspect)" : " (click to inspect)"}`;
          return (
            <g key={`i${idx}`}>
              <g
                transform={instanceTransform(inst)}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={(e) => {
                  e.stopPropagation();
                  if (navigable) {
                    onNavigateInto?.(inst);
                  } else {
                    setInspector({ inst, clientX: e.clientX, clientY: e.clientY });
                  }
                }}
                onContextMenu={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setInspector({ inst, clientX: e.clientX, clientY: e.clientY });
                }}
              >
                <title>{labelTitle}</title>
                {sym ? (
                  <>
                    {sym.primitives.map((p, i) => renderPrimitive(p, `sp${i}`))}
                    {hoveredIdx === idx && navigable && (
                      <SymbolHoverHalo bbox={fileBBox(sym)} />
                    )}
                  </>
                ) : (
                  <SymbolPlaceholder symref={inst.symref} />
                )}
              </g>
              {sym?.texts.map((t, i) => {
                const expanded = expandSymbolText(t, inst);
                const anchor = transformPoint({ x: t.x, y: t.y }, inst);
                return renderTextReadable(expanded, inst.rotate, inst.flip, anchor.x, anchor.y, `st${idx}_${i}`);
              })}
            </g>
          );
        })}
      </svg>

      {/* Floating inspector */}
      {inspector && (
        <InstanceInspector
          inst={inspector.inst}
          anchorX={inspector.clientX}
          anchorY={inspector.clientY}
          containerRef={svgRef}
          navigable={isInstanceNavigable(inspector.inst, symbols.get(inspector.inst.symref), navigableSymrefs)}
          onClose={() => setInspector(null)}
          onDescend={() => {
            const i = inspector.inst;
            setInspector(null);
            onNavigateInto?.(i);
          }}
        />
      )}

      {/* Floating controls */}
      <div className="pointer-events-none absolute right-3 top-3 flex flex-col gap-1 text-xs">
        <button
          type="button"
          onClick={resetView}
          className="pointer-events-auto rounded-sm border border-border bg-panel/90 px-2 py-1 text-fg hover:bg-panel"
        >
          Fit
        </button>
      </div>
    </div>
  );
}

interface InspectorProps {
  inst: Instance;
  anchorX: number;
  anchorY: number;
  containerRef: React.RefObject<SVGSVGElement | null>;
  navigable: boolean;
  onClose: () => void;
  onDescend: () => void;
}

function InstanceInspector({
  inst,
  anchorX,
  anchorY,
  containerRef,
  navigable,
  onClose,
  onDescend,
}: InspectorProps) {
  // Position the popover near the anchor, but keep it inside the SVG viewport.
  const PANEL_W = 360;
  const PANEL_MAX_H = 420;
  const rect = containerRef.current?.getBoundingClientRect();
  const left = rect
    ? Math.max(8, Math.min(anchorX - rect.left + 12, rect.width - PANEL_W - 8))
    : 12;
  const top = rect
    ? Math.max(8, Math.min(anchorY - rect.top + 12, rect.height - PANEL_MAX_H - 8))
    : 12;

  // Split attrs into single-line and multi-line groups for a cleaner layout.
  const entries = Object.entries(inst.attrs);
  const singleLine = entries.filter(([, v]) => !v.includes("\n"));
  const multiLine = entries.filter(([, v]) => v.includes("\n"));

  return (
    <div
      className="absolute z-10 flex flex-col overflow-hidden rounded-md border border-border bg-panel text-xs text-fg shadow-lg"
      style={{ left, top, width: PANEL_W, maxHeight: PANEL_MAX_H }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex items-center justify-between border-b border-border bg-bg/40 px-3 py-2">
        <div className="min-w-0">
          <div className="truncate font-medium">
            {inst.attrs["name"] ?? "(unnamed)"}
          </div>
          <div className="truncate text-[11px] text-muted">{inst.symref}</div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-muted hover:text-fg"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-auto p-3">
        {singleLine.length > 0 && (
          <table className="w-full">
            <tbody>
              {singleLine.map(([k, v]) => (
                <tr key={k} className="align-top">
                  <td className="pr-3 py-0.5 text-muted">{k}</td>
                  <td className="break-all py-0.5 font-mono text-[11px]">{v || <em className="text-muted">—</em>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {multiLine.map(([k, v]) => (
          <div key={k} className="mt-3">
            <div className="mb-1 text-muted">{k}</div>
            <pre className="max-h-48 overflow-auto rounded-sm border border-border bg-bg/60 p-2 font-mono text-[11px] leading-snug">
              {v}
            </pre>
          </div>
        ))}

        <div className="mt-3 text-[10px] text-muted">
          at ({inst.x}, {inst.y}) · rotate {inst.rotate * 90}° · flip {inst.flip ? "yes" : "no"}
        </div>
      </div>

      {navigable && (
        <div className="border-t border-border bg-bg/40 px-3 py-2">
          <button
            type="button"
            onClick={onDescend}
            className="w-full rounded-sm border border-primary/40 bg-primary/15 px-2 py-1 text-primary hover:bg-primary/25"
          >
            Descend into subcircuit ↓
          </button>
        </div>
      )}
    </div>
  );
}

function renderPrimitive(
  p: XschemFile["primitives"][number],
  key: string,
): React.ReactNode {
  const color = layerColor(p.layer);
  if (p.kind === "line") {
    return (
      <line
        key={key}
        x1={p.x1}
        y1={p.y1}
        x2={p.x2}
        y2={p.y2}
        stroke={color}
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
    );
  }
  if (p.kind === "box") {
    const x = Math.min(p.x1, p.x2);
    const y = Math.min(p.y1, p.y2);
    const w = Math.abs(p.x2 - p.x1);
    const h = Math.abs(p.y2 - p.y1);
    // Layer-5 boxes are pin markers — render filled.
    const fill = p.layer === 5 ? color : "none";
    return (
      <rect
        key={key}
        x={x}
        y={y}
        width={w}
        height={h}
        fill={fill}
        stroke={color}
        strokeWidth={1.2}
        vectorEffect="non-scaling-stroke"
      />
    );
  }
  if (p.kind === "polygon") {
    const points = p.points.map((pt) => `${pt.x},${pt.y}`).join(" ");
    return (
      <polyline
        key={key}
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
    );
  }
  if (p.kind === "arc") {
    // SVG's A command degenerates to nothing when start point == end point, so a 360°
    // arc (used by xschem for voltage/current source circles) renders as a circle instead.
    if (Math.abs(p.extentDeg) >= 360) {
      return (
        <circle
          key={key}
          cx={p.cx}
          cy={p.cy}
          r={p.r}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          vectorEffect="non-scaling-stroke"
        />
      );
    }
    return (
      <path
        key={key}
        d={arcPath(p.cx, p.cy, p.r, p.startDeg, p.extentDeg)}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
    );
  }
  return null;
}

/**
 * Render a text in "readable" orientation, matching xschem's display rule:
 * the effective on-screen rotation is the sum (parent_rot + text_rot) mod 4,
 * but 180° and 270° orientations snap back by 180° so labels stay upright.
 *
 * Parent flip is intentionally not applied to the glyphs — xschem keeps text
 * left-to-right regardless of instance mirroring.
 */
function renderTextReadable(
  t: XschemFile["texts"][number],
  parentRot: number,
  parentFlip: number,
  anchorX: number,
  anchorY: number,
  key: string,
): React.ReactNode {
  // xschem's own SVG exporter uses fontSize ≈ 21.5 * hsize.
  const fontSize = Math.max(1.5, 21.5 * t.hsize);
  const lineHeight = Math.max(1.5, 21.5 * t.vsize) * 1.15;
  // Combined rotation, then snap to readable: {2,3} → {0,1}.
  const combined = (parentRot + t.rotate) % 4;
  const displayRot = combined >= 2 ? combined - 2 : combined;
  const rotDeg = -displayRot * 90;
  // Glyphs are NEVER mirrored: xschem uses rotate+flip combinations as alignment hints,
  // not as "render the letters backwards" — its renderer always draws text upright/L-to-R.
  // Both the parent-instance flip and the text's own flip are intentionally ignored here.
  void parentFlip;
  void t.flip;
  // xschem positions text by the upper-left corner of the first glyph (not the SVG default
  // baseline). Approximate by shifting down by ~0.85 * fontSize along the text's own y axis.
  const baselineShift = fontSize * 0.85;
  const lines = t.text.split(/\r?\n/);
  return (
    <text
      key={key}
      x={anchorX}
      y={anchorY + baselineShift}
      fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
      fontSize={fontSize}
      fill="#cbd5e1"
      transform={`rotate(${rotDeg} ${anchorX} ${anchorY})`}
      style={{ pointerEvents: "none", whiteSpace: "pre" }}
      xmlSpace="preserve"
    >
      {lines.length === 1 ? (
        lines[0]
      ) : (
        lines.map((ln, i) => (
          <tspan key={i} x={anchorX} dy={i === 0 ? 0 : lineHeight}>
            {ln === "" ? " " : ln}
          </tspan>
        ))
      )}
    </text>
  );
}

/** xschem expands @<attr> inside symbol text from the instance's properties. */
function expandSymbolText(t: XschemFile["texts"][number], inst: Instance): typeof t {
  const text = t.text.replace(/@([A-Za-z_][A-Za-z0-9_]*)/g, (_m, key: string) => {
    if (key === "symname") return baseStem(inst.symref);
    return inst.attrs[key] ?? "";
  });
  return { ...t, text };
}

function baseStem(p: string): string {
  const last = p.split("/").pop() ?? p;
  return last.replace(/\.sym$/, "");
}

function SymbolPlaceholder({ symref }: { symref: string }) {
  return (
    <g>
      <rect
        x={-20}
        y={-20}
        width={40}
        height={40}
        fill="#1e293b"
        stroke="#f87171"
        strokeWidth={1.5}
        vectorEffect="non-scaling-stroke"
      />
      <text
        x={0}
        y={4}
        textAnchor="middle"
        fontSize={6}
        fill="#fca5a5"
        style={{ pointerEvents: "none" }}
      >
        ?
      </text>
      <title>{`Missing symbol: ${symref}`}</title>
    </g>
  );
}

function SymbolHoverHalo({ bbox }: { bbox: BBox }) {
  const pad = 6;
  return (
    <rect
      x={bbox.x - pad}
      y={bbox.y - pad}
      width={bbox.w + 2 * pad}
      height={bbox.h + 2 * pad}
      fill="none"
      stroke="#fde68a"
      strokeDasharray="4 3"
      strokeWidth={1.5}
      vectorEffect="non-scaling-stroke"
      style={{ pointerEvents: "none" }}
    />
  );
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, extentDeg: number): string {
  // xschem: angles in degrees, 0 = +x, CCW positive.
  const a0 = (startDeg * Math.PI) / 180;
  const a1 = ((startDeg + extentDeg) * Math.PI) / 180;
  const x0 = cx + r * Math.cos(a0);
  const y0 = cy - r * Math.sin(a0);
  const x1 = cx + r * Math.cos(a1);
  const y1 = cy - r * Math.sin(a1);
  const large = Math.abs(extentDeg) > 180 ? 1 : 0;
  const sweep = extentDeg < 0 ? 1 : 0;
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} ${sweep} ${x1} ${y1}`;
}

function isInstanceNavigable(
  inst: Instance,
  sym: XschemFile | undefined,
  navigableSymrefs?: Set<string>,
): boolean {
  if (navigableSymrefs && navigableSymrefs.has(inst.symref)) return true;
  if (sym && isSubcircuit(sym)) return true;
  return false;
}

function computeOverallBBox(sch: XschemFile, symbols: Map<string, XschemFile>): BBox {
  let box: BBox | null = null;
  const base = fileBBox(sch);
  box = box ? unionPair(box, base) : base;
  for (const inst of sch.instances) {
    const sym = symbols.get(inst.symref);
    if (!sym) continue;
    const sb = fileBBox(sym);
    // Instance places the symbol at (x, y) with rotation/flip; for bbox use a conservative
    // axis-aligned envelope by rotating the symbol's corners around (0, 0) and re-bounding.
    const corners = [
      { x: sb.x, y: sb.y },
      { x: sb.x + sb.w, y: sb.y },
      { x: sb.x, y: sb.y + sb.h },
      { x: sb.x + sb.w, y: sb.y + sb.h },
    ].map((p) => transformPoint(p, inst));
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const c of corners) {
      minX = Math.min(minX, c.x);
      minY = Math.min(minY, c.y);
      maxX = Math.max(maxX, c.x);
      maxY = Math.max(maxY, c.y);
    }
    const ib = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
    box = unionPair(box, ib);
  }
  return box ?? { x: 0, y: 0, w: 100, h: 100 };
}

function transformPoint(p: { x: number; y: number }, inst: Instance): { x: number; y: number } {
  let x = p.x, y = p.y;
  if (inst.flip) x = -x;
  const r = inst.rotate;
  // Must match instanceTransform's SVG `rotate(-rot*90)` so symbol-body geometry
  // and its text labels stay co-located: rotate(-90) maps (x, y) -> (y, -x).
  for (let i = 0; i < r; i++) {
    const nx = y;
    const ny = -x;
    x = nx;
    y = ny;
  }
  return { x: x + inst.x, y: y + inst.y };
}

function unionPair(a: BBox, b: BBox): BBox {
  const x1 = Math.min(a.x, b.x);
  const y1 = Math.min(a.y, b.y);
  const x2 = Math.max(a.x + a.w, b.x + b.w);
  const y2 = Math.max(a.y + a.h, b.y + b.h);
  return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
}

function padBox(b: BBox, pad: number): BBox {
  return { x: b.x - pad, y: b.y - pad, w: b.w + 2 * pad, h: b.h + 2 * pad };
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v));
}
