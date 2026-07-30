"use client";
import { Search } from "lucide-react";
import { useLibraryStore } from "@/stores/libraryStore";
import { Select } from "@/components/ui/select";
import { filterAndSort, toCardData, totalCircuits, type SortMode } from "@/lib/library/selectors";
import { CircuitCard } from "../CircuitCard";

const GRID_STYLE = { gridTemplateColumns: "repeat(auto-fill,minmax(202px,1fr))" } as const;

const SORT_OPTIONS = [
  { value: "id", label: "ID A–Z" },
  { value: "comp", label: "Compensation" },
  { value: "stages", label: "Stages ↓" },
  { value: "results", label: "Measured first" },
];

/** Circuits browser — search/sort sub-header over the filterable card grid. */
export function CircuitsView() {
  const { selId, classSel, sourceSel, compSel, search, sort } = useLibraryStore();
  const data = useLibraryStore((s) => s.data);
  const setSearch = useLibraryStore((s) => s.setSearch);
  const setSort = useLibraryStore((s) => s.setSort);
  const openDetail = useLibraryStore((s) => s.openDetail);

  const list = filterAndSort(data, { classSel, sourceSel, compSel, search, sort });

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center gap-2.5 border-b border-border bg-bg px-4 py-2.5">
        <span className="text-[14px] font-semibold tracking-[-0.01em]">Circuits</span>
        <span className="font-mono text-[10.5px] text-faint">
          {list.length} of {totalCircuits(data)} shown
        </span>
        <div className="flex-1" />
        <div className="flex h-7 w-[210px] items-center gap-1.5 rounded-md border border-border bg-panel px-2.5">
          <Search className="h-3 w-3 shrink-0 text-faint" aria-hidden />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search id / topology / paper…"
            className="w-full bg-transparent text-[11.5px] text-fg outline-hidden placeholder:text-faint"
          />
        </div>
        <span className="text-[10.5px] text-muted">Sort</span>
        <Select
          selectSize="xs"
          value={sort}
          onChange={(e) => setSort(e.target.value as SortMode)}
          options={SORT_OPTIONS}
          className="w-[150px]"
        />
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3.5">
        <div className="grid gap-2.5" style={GRID_STYLE}>
          {list.map((c) => (
            <CircuitCard key={c.id} card={toCardData(c, data.measured, selId)} pdks={c.pdks} variant="grid" onOpen={() => openDetail(c.id)} />
          ))}
        </div>
      </div>
    </div>
  );
}
