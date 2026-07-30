// Parser for xschem .sch and .sym files.
//
// File format (line-based, but {...} property blocks may span multiple lines):
//   v {xschem version=...}
//   G {...}   K {...}   V {...}   S {...}   E {...}
//   L <layer> <x1> <y1> <x2> <y2> {props}
//   B <layer> <x1> <y1> <x2> <y2> {props}
//   P <layer> <n> <x1> <y1> ... {props}
//   A <layer> <cx> <cy> <r> <start> <ext> {props}
//   T {text} <x> <y> <rot> <flip> <hs> <vs> {props}
//   N <x1> <y1> <x2> <y2> {props}
//   C {symref} <x> <y> <rot> <flip> {props}

import type {
  XschemFile,
  Instance,
  Wire,
  TextItem,
  LineItem,
  BoxItem,
  PolygonItem,
  ArcItem,
} from "./types";

class Tokenizer {
  private text: string;
  private pos: number = 0;

  constructor(text: string) {
    this.text = text;
  }

  done(): boolean {
    this.skipWs();
    return this.pos >= this.text.length;
  }

  /** Skip spaces, tabs, newlines, and `*`-style xschem comments (lines starting with `*`). */
  private skipWs(): void {
    while (this.pos < this.text.length) {
      const c = this.text[this.pos];
      if (c === " " || c === "\t" || c === "\r" || c === "\n") {
        this.pos++;
        continue;
      }
      // xschem allows `*`-comments at start of a line inside .sym files.
      if (
        c === "*" &&
        (this.pos === 0 || this.text[this.pos - 1] === "\n")
      ) {
        while (this.pos < this.text.length && this.text[this.pos] !== "\n") {
          this.pos++;
        }
        continue;
      }
      break;
    }
  }

  /** Read a {...} block, respecting nesting and double-quoted strings. Returns inner text.
   *
   *  Quote handling matches xschem's lexical rule: a `"` only opens a quoted region when it
   *  immediately follows an `=` (i.e. as part of `key="value"`). Stray closing quotes elsewhere
   *  (e.g. `value=5u pwl(...)"}`, which appears in some xschem files) are treated as literal
   *  text. Without this, an unbalanced `"` would swallow the closing `}` of the property block.
   */
  readBraced(): string {
    this.skipWs();
    if (this.text[this.pos] !== "{") {
      throw new Error(
        `Expected '{' at position ${this.pos}, got ${JSON.stringify(this.text.slice(this.pos, this.pos + 20))}`,
      );
    }
    this.pos++; // consume {
    const start = this.pos;
    let depth = 1;
    let inQuote = false;
    while (this.pos < this.text.length && depth > 0) {
      const c = this.text[this.pos];
      if (inQuote) {
        if (c === "\\" && this.pos + 1 < this.text.length) {
          this.pos += 2;
          continue;
        }
        if (c === '"') {
          inQuote = false;
        }
      } else {
        if (c === '"' && this.pos > start && this.text[this.pos - 1] === "=") {
          inQuote = true;
        } else if (c === "{") {
          depth++;
        } else if (c === "}") {
          depth--;
          if (depth === 0) {
            const inner = this.text.slice(start, this.pos);
            this.pos++; // consume }
            return inner;
          }
        }
      }
      this.pos++;
    }
    throw new Error(`Unclosed '{' starting at position ${start}`);
  }

  /** Read the next whitespace-separated token (not a {block}). */
  readWord(): string {
    this.skipWs();
    const start = this.pos;
    while (this.pos < this.text.length) {
      const c = this.text[this.pos];
      if (c === " " || c === "\t" || c === "\r" || c === "\n" || c === "{") break;
      this.pos++;
    }
    if (this.pos === start) {
      throw new Error(`Expected token at position ${this.pos}`);
    }
    return this.text.slice(start, this.pos);
  }

  /** Peek the next non-whitespace char without consuming. */
  peek(): string {
    this.skipWs();
    return this.text[this.pos] ?? "";
  }

  readNumber(): number {
    const w = this.readWord();
    const n = Number(w);
    if (!Number.isFinite(n)) {
      throw new Error(`Expected number, got ${JSON.stringify(w)}`);
    }
    return n;
  }
}

/** Parse a property block like `name=M5 l=X_DUT_M5_L spiceprefix=X`.
 *  Values may be bare (terminated by whitespace) or "double-quoted" (may contain spaces).
 *  Newlines are treated as whitespace. */
export function parseAttrs(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  let i = 0;
  const n = text.length;
  while (i < n) {
    // Skip leading whitespace.
    while (i < n && /\s/.test(text[i])) i++;
    if (i >= n) break;
    // Read key (up to '=' or whitespace).
    const keyStart = i;
    while (i < n && text[i] !== "=" && !/\s/.test(text[i])) i++;
    const key = text.slice(keyStart, i);
    // Skip optional whitespace between the key and '=' (e.g. `dash = 4`).
    while (i < n && /\s/.test(text[i])) i++;
    if (i < n && text[i] === "=") {
      i++; // consume =
      // Skip optional whitespace between '=' and the value.
      while (i < n && /\s/.test(text[i])) i++;
      let value = "";
      if (text[i] === '"') {
        i++;
        const vs = i;
        while (i < n) {
          if (text[i] === "\\" && i + 1 < n) {
            i += 2;
            continue;
          }
          if (text[i] === '"') break;
          i++;
        }
        value = text.slice(vs, i);
        if (text[i] === '"') i++;
      } else {
        const vs = i;
        while (i < n && !/\s/.test(text[i])) i++;
        value = text.slice(vs, i);
      }
      out[key] = value;
    } else {
      // Bare token, no value.
      if (key) out[key] = "";
    }
  }
  return out;
}

export function parseXschem(text: string): XschemFile {
  const tk = new Tokenizer(text);
  const file: XschemFile = {
    version: null,
    globalAttrs: {},
    kindAttrs: {},
    primitives: [],
    texts: [],
    wires: [],
    instances: [],
  };

  while (!tk.done()) {
    const tag = tk.readWord();
    switch (tag) {
      case "v": {
        const inner = tk.readBraced();
        file.version = inner.trim();
        break;
      }
      case "G": {
        const inner = tk.readBraced();
        file.globalAttrs = parseAttrs(inner);
        break;
      }
      case "K": {
        const inner = tk.readBraced();
        file.kindAttrs = parseAttrs(inner);
        break;
      }
      case "V":
      case "S":
      case "E": {
        // Versions / selection / end-of-defs. We don't use them.
        tk.readBraced();
        break;
      }
      case "L": {
        const layer = tk.readNumber();
        const x1 = tk.readNumber();
        const y1 = tk.readNumber();
        const x2 = tk.readNumber();
        const y2 = tk.readNumber();
        const inner = tk.readBraced();
        file.primitives.push({
          kind: "line",
          layer,
          x1,
          y1,
          x2,
          y2,
          attrs: parseAttrs(inner),
        } as LineItem);
        break;
      }
      case "B": {
        const layer = tk.readNumber();
        const x1 = tk.readNumber();
        const y1 = tk.readNumber();
        const x2 = tk.readNumber();
        const y2 = tk.readNumber();
        const inner = tk.readBraced();
        file.primitives.push({
          kind: "box",
          layer,
          x1,
          y1,
          x2,
          y2,
          attrs: parseAttrs(inner),
        } as BoxItem);
        break;
      }
      case "P": {
        const layer = tk.readNumber();
        const npts = tk.readNumber();
        const points: { x: number; y: number }[] = [];
        for (let k = 0; k < npts; k++) {
          const x = tk.readNumber();
          const y = tk.readNumber();
          points.push({ x, y });
        }
        const inner = tk.readBraced();
        file.primitives.push({
          kind: "polygon",
          layer,
          points,
          attrs: parseAttrs(inner),
        } as PolygonItem);
        break;
      }
      case "A": {
        const layer = tk.readNumber();
        const cx = tk.readNumber();
        const cy = tk.readNumber();
        const r = tk.readNumber();
        const startDeg = tk.readNumber();
        const extentDeg = tk.readNumber();
        const inner = tk.readBraced();
        file.primitives.push({
          kind: "arc",
          layer,
          cx,
          cy,
          r,
          startDeg,
          extentDeg,
          attrs: parseAttrs(inner),
        } as ArcItem);
        break;
      }
      case "T": {
        const textBody = tk.readBraced();
        const x = tk.readNumber();
        const y = tk.readNumber();
        const rotate = tk.readNumber();
        const flip = tk.readNumber();
        const hsize = tk.readNumber();
        const vsize = tk.readNumber();
        const inner = tk.readBraced();
        const t: TextItem = {
          text: textBody,
          x,
          y,
          rotate,
          flip,
          hsize,
          vsize,
          attrs: parseAttrs(inner),
        };
        file.texts.push(t);
        break;
      }
      case "N": {
        const x1 = tk.readNumber();
        const y1 = tk.readNumber();
        const x2 = tk.readNumber();
        const y2 = tk.readNumber();
        const inner = tk.readBraced();
        const w: Wire = { x1, y1, x2, y2, attrs: parseAttrs(inner) };
        file.wires.push(w);
        break;
      }
      case "C": {
        const symref = tk.readBraced();
        const x = tk.readNumber();
        const y = tk.readNumber();
        const rotate = tk.readNumber();
        const flip = tk.readNumber();
        const inner = tk.readBraced();
        const inst: Instance = {
          symref,
          x,
          y,
          rotate,
          flip,
          attrs: parseAttrs(inner),
        };
        file.instances.push(inst);
        break;
      }
      default: {
        // Unknown record: try to consume an optional trailing {} block so we don't desync.
        if (tk.peek() === "{") {
          tk.readBraced();
        }
        break;
      }
    }
  }

  return file;
}
