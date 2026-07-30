"use client";
import { cn } from "@/lib/utils";
import { useLibraryStore, type LibraryTab } from "@/stores/libraryStore";
import { useLibraryWizardStore } from "@/stores/libraryWizardStore";
import { strapMeta, filterAndSort, tbList } from "@/lib/library/selectors";

const TABS: { id: LibraryTab; label: string }[] = [
  { id: "home", label: "Home" },
  { id: "circuits", label: "Circuits" },
  { id: "templates", label: "Templates" },
  { id: "testbenches", label: "Testbenches" },
];

/** Tab strip / breadcrumb (38px) — the 4 tabs, or a back-chip breadcrumb in
 *  detail view; right side carries the Register button + a mono summary. */
export function LibraryTabStrip() {
  const tab = useLibraryStore((s) => s.tab);
  const detailOpen = useLibraryStore((s) => s.detailOpen);
  const selId = useLibraryStore((s) => s.selId);
  const classSel = useLibraryStore((s) => s.classSel);
  const sourceSel = useLibraryStore((s) => s.sourceSel);
  const compSel = useLibraryStore((s) => s.compSel);
  const tbClassSel = useLibraryStore((s) => s.tbClassSel);
  const search = useLibraryStore((s) => s.search);
  const sort = useLibraryStore((s) => s.sort);
  const data = useLibraryStore((s) => s.data);
  const setTab = useLibraryStore((s) => s.setTab);
  const goBack = useLibraryStore((s) => s.goBack);
  const openWizard = useLibraryWizardStore((s) => s.openWizard);

  // per-tab filtered row count, so the strap reflects active filters
  const found =
    tab === "testbenches"
      ? tbList(data, tbClassSel, "").length
      : filterAndSort(data, { classSel, sourceSel, compSel, search, sort }).length;
  const strap = strapMeta(data, tab, detailOpen, selId, found);

  return (
    <div className="flex h-[38px] shrink-0 items-center gap-2.5 border-b border-border bg-panel px-3.5">
      <span className="text-[11px] font-bold tracking-wider">Library</span>
      <span className="text-[#d4d4d8]">·</span>

      {detailOpen ? (
        <div className="flex min-w-0 items-center gap-1.5">
          <button
            type="button"
            onClick={goBack}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-md bg-hairline px-2.5 py-1 text-[11px] font-medium text-muted transition hover:bg-[#ececef]"
          >
            ‹ Circuits
          </button>
          <span className="text-[#d4d4d8]">▸</span>
          <span className="truncate font-mono text-[11px]">{selId}</span>
        </div>
      ) : (
        <div className="flex gap-0.5">
          {TABS.map((t) => {
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={cn(
                  "rounded-md px-3 py-1 text-[11px] transition",
                  active ? "bg-fg font-semibold text-white" : "font-medium text-muted hover:bg-hairline",
                )}
              >
                {t.label}
              </button>
            );
          })}
        </div>
      )}

      <div className="flex-1" />
      <button
        type="button"
        onClick={() => openWizard("circuit")}
        className="inline-flex h-6 items-center rounded-md bg-primary px-2.5 text-[11px] font-semibold text-white transition hover:bg-[#4338ca]"
      >
        + Register item
      </button>
      <span className="hidden font-mono text-[10px] text-faint sm:inline">{strap}</span>
    </div>
  );
}
