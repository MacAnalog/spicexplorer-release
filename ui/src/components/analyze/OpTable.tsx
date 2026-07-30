"use client";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import { EmptyState } from "@/components/ui/empty-state";
import { useWaveviewStore } from "@/stores/waveviewStore";
import { formatEng } from "@/lib/utils";
import { groupScalars } from "@/lib/waveview/selectors";

/**
 * OP tab — the DC operating point as tables instead of a plot. Columns are
 * data-driven: device rows appear only when the raw actually saved device
 * params (@m…[gm] vectors); node/branch scalars render as a name/value list.
 */
export function OpTable() {
  const scalars = useWaveviewStore((s) => s.scalars);

  if (!scalars) {
    return <EmptyState minHeight="min-h-40">Loading operating point…</EmptyState>;
  }
  const entries = Object.entries(scalars.scalars);
  if (!entries.length) {
    return (
      <EmptyState minHeight="min-h-40" bordered>
        No OP scalars in this dataset.
      </EmptyState>
    );
  }
  const { rows, columns, other } = groupScalars(scalars.scalars);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-auto">
      {rows.length > 0 && (
        <table className="w-full">
          <Thead>
            <Th>device</Th>
            {columns.map((c) => (
              <Th key={c} className="text-right">
                {c}
              </Th>
            ))}
          </Thead>
          <tbody>
            {rows.map((r) => (
              <Tr key={r.dev}>
                <Td className="font-mono">{r.dev}</Td>
                {columns.map((c) => (
                  <Td key={c} className="text-right font-mono">
                    {c in r.params ? formatEng(r.params[c]) : "—"}
                  </Td>
                ))}
              </Tr>
            ))}
          </tbody>
        </table>
      )}
      {other.length > 0 && (
        <table className="w-full">
          <Thead>
            <Th>scalar</Th>
            <Th className="text-right">value</Th>
          </Thead>
          <tbody>
            {other.map(([name, value]) => (
              <Tr key={name}>
                <Td className="font-mono">{name}</Td>
                <Td className="text-right font-mono">{formatEng(value)}</Td>
              </Tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="border-t border-hairline px-3 py-1.5 font-mono text-[9.5px] text-faint">
        {entries.length} scalars · GET /waveview/datasets/{"{id}"}/scalars
      </div>
    </div>
  );
}
