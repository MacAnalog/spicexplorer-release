"use client";
import { UI } from "@/config";
import { useLibraryStore } from "@/stores/libraryStore";
import { headStats, toCardData, totalCircuits } from "@/lib/library/selectors";
import { Hatch } from "../Hatch";
import { Chip } from "../chips";
import { CircuitCard } from "../CircuitCard";

const GRID_STYLE = { gridTemplateColumns: "repeat(auto-fill,minmax(202px,1fr))" } as const;

/** The landing shows a taste of the catalog, not all of it — the full filterable
 *  grid lives in the Circuits browser. Measured circuits surface first. */
const HOME_GRID_CAP = UI.library.home.gridCap;

/** Home landing — head stats, the featured reference case, and a capped grid. */
export function HomeView() {
  const data = useLibraryStore((s) => s.data);
  const selId = useLibraryStore((s) => s.selId);
  const openDetail = useLibraryStore((s) => s.openDetail);
  const goCircuits = useLibraryStore((s) => s.goCircuits);

  return (
    <div className="min-h-0 flex-1 overflow-y-auto px-[18px] py-4">
      <div className="mb-3">
        <div className="text-[20px] font-semibold tracking-[-0.015em]">{UI.library.home.title}</div>
        <div className="mt-0.5 text-[11.5px] text-muted">
          {totalCircuits(data)} {UI.library.home.taglineAfterCount}
        </div>
      </div>

      {/* head stats */}
      <div className="mb-4 grid grid-cols-5 gap-[9px]">
        {headStats(data).map((s) => (
          <div key={s.label} className="rounded-lg border border-border bg-panel px-3 py-2.5">
            <div className="text-[9px] uppercase tracking-wider text-faint">{s.label}</div>
            <div className="mt-0.5 font-mono text-[19px] font-semibold">{s.count}</div>
          </div>
        ))}
      </div>

      {/* featured reference case */}
      <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.08em] text-faint">{UI.library.home.featuredHeading}</div>
      <button
        type="button"
        onClick={() => openDetail(UI.library.home.featuredCircuit)}
        className="mb-[18px] flex w-full flex-wrap gap-3.5 rounded-[11px] border border-border bg-panel p-3.5 text-left transition hover:border-[#c7d2fe] hover:shadow-[0_6px_18px_-10px_rgba(79,70,229,0.3)]"
      >
        <Hatch label="amp_018_telescopic_cascode.sch" heightClass="h-36" className="w-[236px] shrink-0 rounded-lg border-border" />
        <div className="flex min-w-[240px] flex-1 flex-col">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[15px] font-semibold tracking-[-0.01em]">Telescopic Cascode OTA</span>
            <Chip bg="#eef2ff" fg="#4f46e5">amplifier</Chip>
            <span className="font-mono text-[9px] text-faint">amp_018_telescopic_cascode · NEWCAS 2026</span>
          </div>
          <div className="mt-1 text-[11px] text-muted">
            Bundled reference case on ihp-sg13g2 — recorded baseline (default sizing), ready to optimize.
          </div>
          <div className="my-3 grid grid-cols-4 gap-2">
            <FeaturedKpi label="DC gain" value="52.8" unit="dB" />
            <FeaturedKpi label="UGF" value="55.9" unit="MHz" />
            <FeaturedKpi label="Phase margin" value="−397" unit="°" valueClass="text-tertiary" />
            <FeaturedKpi label="H(s) check" value="52.2 ✓" valueClass="text-ok" />
          </div>
          <div className="mt-auto flex items-center gap-1.5">
            <Chip bg="#fef3c7" fg="#b45309" className="font-normal">ihp-sg13g2</Chip>
            <Chip bg="#ecfeff" fg="#0891b2" className="font-normal">sky130</Chip>
            <Chip bg="#eef2ff" fg="#4f46e5" className="font-normal">gf180mcu</Chip>
            <span className="ml-1 text-[10px] text-faint">5 analyses · symbolic cross-check ✓</span>
          </div>
        </div>
      </button>

      {/* browse — a capped, measured-first sampler; the Circuits tab is the real browser */}
      <div className="mb-2 flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-faint">Browse</span>
        <div className="h-px flex-1 bg-hairline" />
        <button type="button" onClick={goCircuits} className="text-[10.5px] text-primary hover:underline">
          Open browser →
        </button>
      </div>
      <div className="grid gap-2.5" style={GRID_STYLE}>
        {[...data.circuits]
          .sort((a, b) => Number(b.id in data.measured) - Number(a.id in data.measured))
          .slice(0, HOME_GRID_CAP)
          .map((c) => (
            <CircuitCard key={c.id} card={toCardData(c, data.measured, selId)} pdks={c.pdks} variant="home" onOpen={() => openDetail(c.id)} />
          ))}
        {data.circuits.length > HOME_GRID_CAP && (
          <button
            type="button"
            onClick={goCircuits}
            className="flex min-h-[120px] flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-border bg-bg text-center transition hover:border-[#c7d2fe] hover:bg-primary-soft"
          >
            <span className="font-mono text-[16px] font-semibold text-primary">
              +{data.circuits.length - HOME_GRID_CAP}
            </span>
            <span className="text-[10.5px] font-medium text-muted">
              more circuits in the browser →
            </span>
            <span className="text-[9px] text-faint">filters: class · source · compensation</span>
          </button>
        )}
      </div>
    </div>
  );
}

function FeaturedKpi({ label, value, unit, valueClass }: { label: string; value: string; unit?: string; valueClass?: string }) {
  return (
    <div>
      <div className="text-[9px] uppercase text-faint">{label}</div>
      <div className={`font-mono text-[14px] font-semibold ${valueClass ?? ""}`}>
        {value}
        {unit && <span className="text-[9px] font-normal text-muted"> {unit}</span>}
      </div>
    </div>
  );
}
