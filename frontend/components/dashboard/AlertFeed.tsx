import Link from "next/link";
import type { Alert } from "@/lib/types";

const severityStyle: Record<string, string> = {
  critical: "border-l-rose-500 bg-rose-500/5",
  high: "border-l-orange-500 bg-orange-500/5",
  medium: "border-l-amber-400 bg-amber-400/5",
  low: "border-l-sky-500 bg-sky-500/5",
  info: "border-l-zinc-500 bg-zinc-500/5",
};

function dot(sev: string): string {
  if (sev === "critical") return "🔴";
  if (sev === "high") return "🟠";
  if (sev === "medium") return "🟡";
  if (sev === "low") return "🟢";
  return "⚪";
}

export function AlertFeed({
  alerts,
  storeId,
}: {
  alerts: Alert[];
  storeId: number;
}) {
  return (
    <div className="flex h-full min-h-[280px] flex-col rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)]">
      <div className="flex items-center justify-between border-b border-[var(--rp-border)] px-4 py-3">
        <h2 className="text-sm font-semibold">Alert feed</h2>
        <span className="text-xs text-[var(--rp-muted)]">Live queue</span>
      </div>
      <ul className="flex-1 divide-y divide-[var(--rp-border)] overflow-auto">
        {alerts.length === 0 ? (
          <li className="px-4 py-8 text-center text-sm text-[var(--rp-muted)]">
            No active alerts for this store.
          </li>
        ) : (
          alerts.map((a) => (
            <li
              key={a.id}
              className={`border-l-4 px-4 py-3 ${severityStyle[a.severity] || severityStyle.info}`}
            >
              <p className="text-sm font-medium text-[var(--rp-fg)]">
                <span className="mr-1.5" aria-hidden>
                  {dot(a.severity)}
                </span>
                {a.title}
              </p>
              <p className="mt-1 line-clamp-2 text-xs text-[var(--rp-muted)]">{a.description}</p>
            </li>
          ))
        )}
      </ul>
      <div className="border-t border-[var(--rp-border)] p-3">
        <Link
          href={`/alerts?store=${storeId}`}
          className="block text-center text-sm font-medium text-[var(--rp-accent)] hover:underline"
        >
          View all alerts →
        </Link>
      </div>
    </div>
  );
}
