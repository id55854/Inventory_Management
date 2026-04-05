import type { AisleHeatColumn } from "@/lib/heatmap";

function heatColor(pct: number): string {
  if (pct >= 80) return "bg-emerald-500/90";
  if (pct >= 55) return "bg-amber-500/85";
  if (pct >= 35) return "bg-orange-500/80";
  return "bg-rose-600/85";
}

export function ShelfHeatmap({ columns }: { columns: AisleHeatColumn[] }) {
  if (!columns.length) {
    return (
      <div className="rounded-xl border border-dashed border-[var(--rp-border)] bg-[var(--rp-panel)]/50 p-8 text-center text-sm text-[var(--rp-muted)]">
        No aisle data for this store.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-[var(--rp-fg)]">Store floor heatmap</h2>
        <span className="text-xs text-[var(--rp-muted)]">Occupancy by aisle</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
        {columns.map((col) => (
          <div
            key={col.aisleId}
            className="flex flex-col gap-2 rounded-lg border border-[var(--rp-border)] bg-[var(--rp-bg)]/40 p-3"
          >
            <div className="flex items-start justify-between gap-1">
              <p className="line-clamp-2 text-xs font-medium leading-snug text-[var(--rp-fg)]">
                {col.label}
              </p>
              {col.alert ? (
                <span
                  className="shrink-0 rounded px-1 text-[10px] font-semibold uppercase text-rose-400"
                  title="Below threshold"
                >
                  !
                </span>
              ) : null}
            </div>
            <div
              className={`flex h-16 items-end justify-center rounded-md ${heatColor(col.occupancyPct)}`}
              title={`${col.occupancyPct}% full`}
            >
              <span className="mb-1 text-lg font-bold tabular-nums text-white drop-shadow">
                {col.occupancyPct}%
              </span>
            </div>
            <p className="text-[11px] capitalize text-[var(--rp-muted)]">{col.category}</p>
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-[var(--rp-muted)]">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-4 rounded bg-emerald-500/90" /> Strong
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-4 rounded bg-amber-500/85" /> OK
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-4 rounded bg-orange-500/80" /> Low
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-4 rounded bg-rose-600/85" /> Critical
        </span>
      </div>
    </div>
  );
}
