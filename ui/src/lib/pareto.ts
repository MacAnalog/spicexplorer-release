/**
 * O(n²) non-dominated (Pareto) front over 2-D points. `n` is small (typically
 * < 2000 evaluated points), so the quadratic sweep is fine. Direction per axis
 * follows the spec goal: `minimize` → smaller is better, anything else → larger
 * is better (matching the feasible-region logic in MetricScatterChart).
 */
export interface XYPoint {
  x: number;
  y: number;
}

export function paretoFront<T extends XYPoint>(
  pts: T[],
  goalX: string,
  goalY: string,
  targetX?: number | null,
  targetY?: number | null,
): T[] {
  // Map each axis to a "smaller is better" key. For an `exact` goal, "better" = CLOSER to target
  // (|value - target|), NOT larger — the old code treated every non-minimize goal as larger-better,
  // which gave a wrong frontier for exact-goal axes (BUG-B45). Falls back to larger-better with no target.
  const key = (goal: string, target: number | null | undefined) => {
    if (goal === "minimize") return (a: number) => a;
    if (goal === "exact" && target != null) return (a: number) => Math.abs(a - target);
    return (a: number) => -a;
  };
  const kx = key(goalX, targetX);
  const ky = key(goalY, targetY);
  const atLeastX = (a: number, b: number) => kx(a) <= kx(b);
  const atLeastY = (a: number, b: number) => ky(a) <= ky(b);
  const strictX = (a: number, b: number) => kx(a) < kx(b);
  const strictY = (a: number, b: number) => ky(a) < ky(b);
  const dominated = (p: T) =>
    pts.some(
      (q) =>
        q !== p &&
        atLeastX(q.x, p.x) &&
        atLeastY(q.y, p.y) &&
        (strictX(q.x, p.x) || strictY(q.y, p.y)),
    );
  const front = pts.filter((p) => !dominated(p));
  // Sort along x so a connecting line reads as a frontier.
  return front.sort((a, b) => a.x - b.x);
}
