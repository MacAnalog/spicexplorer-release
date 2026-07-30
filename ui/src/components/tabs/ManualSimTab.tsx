"use client";
import { ManualSimPanel } from "@/components/pvt/ManualSimPanel";

/**
 * Manual Sim view — design-centric "evaluate THIS point" (a hand-entered vector or
 * a stored checkpoint point), sharing the optimizer's evaluate() primitive so the
 * result is directly comparable to a real trial. Promoted out of the Optimize tab
 * into its own top-level view (ActivityBar utility group). PDK-gated like live runs;
 * ManualSimPanel renders its own empty/PDK-missing states, so this wrapper just
 * supplies the scrolling view frame.
 *
 * *:shrink-0 — the child is a Panel (overflow-hidden ⇒ flex auto-min-size 0), so
 * without this the column would crush it to fit and clip the result + log tails
 * instead of letting this container scroll.
 */
export function ManualSimTab() {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-auto p-3 *:shrink-0">
      <ManualSimPanel />
    </div>
  );
}
