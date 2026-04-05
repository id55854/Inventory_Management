"use client";

import type { ShelfIssue, ShelfScanResult } from "@/lib/types";
import type { AnalyzeShelfApiResponse } from "@/lib/scan-api";

const severityRank: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
  info: 4,
};

function sortIssues(issues: ShelfIssue[]) {
  return [...issues].sort(
    (a, b) =>
      (severityRank[a.severity] ?? 99) - (severityRank[b.severity] ?? 99)
  );
}

export function AnalysisResults({
  result,
  report,
  reportLoading,
  onGenerateReport,
  selectedIndex,
  hoveredIndex,
  onSelectProduct,
  onHoverProduct,
  listRefs,
}: {
  result: ShelfScanResult;
  report: AnalyzeShelfApiResponse | null;
  reportLoading: boolean;
  onGenerateReport: () => void;
  selectedIndex: number | null;
  hoveredIndex: number | null;
  onSelectProduct: (i: number) => void;
  onHoverProduct: (i: number | null) => void;
  listRefs: React.MutableRefObject<(HTMLLIElement | null)[]>;
}) {
  const issuesSorted = sortIssues(result.issues);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-4">
        <h3 className="text-sm font-semibold text-[var(--rp-fg)]">Detected products</h3>
        <ul className="mt-3 max-h-64 divide-y divide-[var(--rp-border)] overflow-auto">
          {result.detections.map((d, i) => {
            const active = selectedIndex === i || hoveredIndex === i;
            return (
              <li
                key={`${d.productName}-${i}`}
                ref={(el) => {
                  listRefs.current[i] = el;
                }}
                className={`cursor-pointer py-2.5 text-sm transition-colors ${
                  active ? "bg-[var(--rp-accent)]/10" : "hover:bg-[var(--rp-bg)]/80"
                }`}
                onMouseEnter={() => onHoverProduct(i)}
                onMouseLeave={() => onHoverProduct(null)}
                onClick={() => onSelectProduct(i)}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-medium text-[var(--rp-fg)]">{d.productName}</span>
                  <span className="shrink-0 tabular-nums text-xs text-[var(--rp-muted)]">
                    {(d.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="mt-0.5 text-xs text-[var(--rp-muted)]">
                  Qty ~{d.quantityEstimated} · shelf row {d.shelfPosition}
                  {d.sku ? ` · ${d.sku}` : ""}
                </div>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-4">
          <h3 className="text-sm font-semibold text-[var(--rp-fg)]">Issues</h3>
          <ul className="mt-3 space-y-2">
            {issuesSorted.length === 0 ? (
              <li className="text-sm text-[var(--rp-muted)]">No issues flagged.</li>
            ) : (
              issuesSorted.map((iss, i) => (
                <li
                  key={`${iss.type}-${i}`}
                  className="flex items-start gap-2 rounded-lg border border-[var(--rp-border)] bg-[var(--rp-bg)]/50 px-3 py-2 text-sm"
                >
                  <span
                    className={`mt-0.5 h-2 w-2 shrink-0 rounded-full ${
                      iss.severity === "high" || iss.severity === "critical"
                        ? "bg-rose-500"
                        : iss.severity === "medium"
                          ? "bg-amber-400"
                          : "bg-sky-400"
                    }`}
                    aria-hidden
                  />
                  <div>
                    <span className="font-medium capitalize text-[var(--rp-fg)]">
                      {iss.type.replace(/_/g, " ")}
                    </span>
                    <span className="text-[var(--rp-muted)]"> · {iss.severity}</span>
                    {iss.description ? (
                      <p className="mt-0.5 text-xs text-[var(--rp-muted)]">{iss.description}</p>
                    ) : null}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>

        <div className="rounded-xl border border-[var(--rp-border)] bg-gradient-to-br from-[var(--rp-panel)] to-[var(--rp-bg)] p-4">
          <h3 className="text-sm font-semibold text-[var(--rp-accent)]">Gemini insight</h3>
          <p className="mt-2 text-sm leading-relaxed text-[var(--rp-muted)]">
            {result.geminiInsight}
          </p>
        </div>

        <div className="rounded-xl border border-[var(--rp-border)] bg-[var(--rp-panel)] p-4">
          <h3 className="text-sm font-semibold text-[var(--rp-fg)]">Restock & actions</h3>
          <ul className="mt-2 list-inside list-disc text-sm text-[var(--rp-muted)]">
            <li>
              Prioritize SKUs with low model confidence or low quantity estimates on the shelf.
            </li>
            <li>Cross-check gaps in the issues panel against empty facings in the image.</li>
          </ul>
          {report ? (
            <div className="mt-4 border-t border-[var(--rp-border)] pt-4">
              <p className="text-xs font-medium uppercase tracking-wide text-[var(--rp-muted)]">
                Full report
              </p>
              <p className="mt-2 text-sm text-[var(--rp-fg)]">{report.summary}</p>
              <ul className="mt-2 space-y-1 text-sm text-[var(--rp-muted)]">
                {report.recommendations.map((r, i) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          ) : null}
          <button
            type="button"
            onClick={onGenerateReport}
            disabled={reportLoading}
            className="mt-4 w-full rounded-lg border border-[var(--rp-accent)] bg-[var(--rp-accent)]/10 px-4 py-2.5 text-sm font-medium text-[var(--rp-accent)] hover:bg-[var(--rp-accent)]/20 disabled:opacity-50"
          >
            {reportLoading ? "Generating…" : "Generate report"}
          </button>
        </div>
      </div>
    </div>
  );
}
