"use client";

import { AlertBadge } from "./AlertBadge";
import type { StoreApiRow } from "@/lib/types";

/** Section 7.1 — top bar: logo, store selector, alert count. */
export function Header({
  stores,
  storeId,
  onStoreChange,
}: {
  stores: StoreApiRow[];
  storeId: number;
  onStoreChange: (id: number) => void;
}) {
  const sid = Number.isFinite(storeId) ? storeId : stores[0]?.id ?? 1;

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--rp-border)] bg-[var(--rp-header)]/95 backdrop-blur">
      <div className="flex h-14 items-center justify-between gap-4 px-4 md:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <span className="shrink-0 text-lg font-semibold tracking-tight text-[var(--rp-accent)]">
            RetailPulse
          </span>
          <span className="hidden text-[var(--rp-muted)] sm:inline">|</span>
          <label className="flex min-w-0 items-center gap-2 text-sm">
            <span className="hidden text-[var(--rp-muted)] sm:inline">Store</span>
            <select
              className="max-w-[min(100vw-8rem,20rem)] truncate rounded-md border border-[var(--rp-border)] bg-[var(--rp-panel)] px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-[var(--rp-accent)]"
              value={sid}
              onChange={(e) => onStoreChange(Number(e.target.value))}
            >
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <AlertBadge storeId={sid} />
      </div>
    </header>
  );
}
