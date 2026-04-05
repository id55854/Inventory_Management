import type { DepletionForecast } from "@/lib/types";
import { TrendingDown } from "lucide-react";

export function StockoutPrediction({ items }: { items: DepletionForecast[] }) {
  return (
    <div className="flex min-h-[280px] flex-col rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)]">
      <div className="flex items-center gap-2 border-b border-[var(--rp-border)] px-4 py-3">
        <TrendingDown className="h-4 w-4 text-[var(--rp-muted)]" aria-hidden />
        <h2 className="text-sm font-semibold">Depletion forecast</h2>
      </div>
      <ul className="flex-1 divide-y divide-[var(--rp-border)] overflow-auto">
        {items.length === 0 ? (
          <li className="px-4 py-8 text-center text-sm text-[var(--rp-muted)]">
            No forecasts available.
          </li>
        ) : (
          items.map((f, i) => (
            <li key={`${f.productName}-${i}`} className="px-4 py-3">
              <p className="text-sm font-medium text-[var(--rp-fg)]">
                <span className="mr-1" aria-hidden>
                  📉
                </span>
                {f.productName}
              </p>
              <p className="mt-1 text-xs text-[var(--rp-muted)]">
                Stockout in{" "}
                <span className="font-medium text-[var(--rp-fg)]">
                  {f.hoursToStockout < 48
                    ? `${f.hoursToStockout}h`
                    : `${Math.round(f.hoursToStockout / 24)}d`}
                </span>
                {" · "}
                <span
                  className={
                    f.urgency === "critical"
                      ? "text-rose-400"
                      : f.urgency === "high"
                        ? "text-orange-400"
                        : "text-[var(--rp-muted)]"
                  }
                >
                  {f.urgency}
                </span>
              </p>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
