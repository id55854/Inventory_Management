import { Suspense } from "react";
import { ScanWorkspace } from "@/components/scan/ScanWorkspace";
import { apiGet } from "@/lib/api";
import type { StoreApiRow } from "@/lib/types";

async function loadStores(): Promise<StoreApiRow[]> {
  try {
    return await apiGet<StoreApiRow[]>("/stores");
  } catch {
    return [];
  }
}

export default async function ScanPage() {
  const stores = await loadStores();

  return (
    <Suspense
      fallback={
        <div className="p-6 text-sm text-[var(--rp-muted)]">Loading scan…</div>
      }
    >
      <ScanWorkspace initialStores={stores} />
    </Suspense>
  );
}
