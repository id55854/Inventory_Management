"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiUrl } from "@/lib/api";

export function AlertBadge({ storeId }: { storeId: number }) {
  const [n, setN] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          apiUrl(`/alerts/summary?store_id=${storeId}`),
          { cache: "no-store" }
        );
        if (!res.ok) return;
        const data = await res.json();
        if (!cancelled) setN(data.total_unresolved ?? 0);
      } catch {
        if (!cancelled) setN(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [storeId]);

  return (
    <Link
      href={`/alerts?store=${storeId}`}
      className="flex items-center gap-2 rounded-md border border-[var(--rp-border)] bg-[var(--rp-panel)] px-3 py-1.5 text-sm tabular-nums hover:border-[var(--rp-accent)]/50"
    >
      <span aria-hidden>🔔</span>
      <span>{n === null ? "—" : `${n} alerts`}</span>
    </Link>
  );
}
