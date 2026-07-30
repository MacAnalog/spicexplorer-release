// Typed AST for xschem .sch / .sym files.
// The format is documented at https://xschem.sourceforge.io/stefan/xschem_man/

export interface XschemFile {
  version: string | null;
  globalAttrs: Record<string, string>;
  // K block — symbol-level properties (type=subcircuit, format=, template=, etc.)
  kindAttrs: Record<string, string>;
  primitives: Primitive[];
  texts: TextItem[];
  wires: Wire[];
  instances: Instance[];
}

export type Primitive = LineItem | BoxItem | PolygonItem | ArcItem;

export interface LineItem {
  kind: "line";
  layer: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  attrs: Record<string, string>;
}

export interface BoxItem {
  kind: "box";
  layer: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  attrs: Record<string, string>;
}

export interface PolygonItem {
  kind: "polygon";
  layer: number;
  points: { x: number; y: number }[];
  attrs: Record<string, string>;
}

export interface ArcItem {
  kind: "arc";
  layer: number;
  cx: number;
  cy: number;
  r: number;
  startDeg: number;
  extentDeg: number;
  attrs: Record<string, string>;
}

export interface TextItem {
  text: string;
  x: number;
  y: number;
  rotate: number; // 0..3 (multiples of 90)
  flip: number; // 0 | 1
  hsize: number;
  vsize: number;
  attrs: Record<string, string>;
}

export interface Wire {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  attrs: Record<string, string>;
}

export interface Instance {
  symref: string; // e.g. "sg13g2_pr/sg13_lv_nmos.sym" or "devices/ipin.sym"
  x: number;
  y: number;
  rotate: number; // 0..3
  flip: number; // 0 | 1
  attrs: Record<string, string>; // name=M5, model=sg13_lv_nmos, lab=vss, ...
}
