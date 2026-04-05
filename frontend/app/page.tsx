import { KPICard } from "@/components/layout/KPICard";
import { ShelfHeatmap } from "@/components/dashboard/ShelfHeatmap";
import { AlertFeed } from "@/components/dashboard/AlertFeed";
import { StockoutPrediction } from "@/components/dashboard/StockoutPrediction";
import { AiInsightCard } from "@/components/dashboard/AiInsightCard";
import { apiGet } from "@/lib/api";
import { aisleColumnsFromHeatmap } from "@/lib/heatmap";
import { mapAlert, mapDepletion } from "@/lib/mappers";
import type {
  AlertApi,
  DailyBriefApi,
  DepletionApi,
  HeatmapApi,
  StoreApiRow,
  StoreKpisApi,
} from "@/lib/types";

async function loadDashboard(storeId: number) {
  const kpisPath = `/stores/${storeId}/kpis`;
  const heatPath = `/stores/${storeId}/heatmap`;
  const alertsPath = `/alerts?resolved=false&store_id=${storeId}&limit=12`;
  const depletionPath = `/analytics/depletion?store_id=${storeId}`;
  const briefPath = `/insights/daily-brief?store_id=${storeId}`;

  let kpis: StoreKpisApi;
  let heatmap: HeatmapApi;
  let alertsRaw: AlertApi[];
  let depletionRaw: DepletionApi[];
  let brief: DailyBriefApi;

  try {
    [kpis, heatmap, alertsRaw, depletionRaw, brief] = await Promise.all([
      apiGet<StoreKpisApi>(kpisPath),
      apiGet<HeatmapApi>(heatPath),
      apiGet<AlertApi[]>(alertsPath),
      apiGet<DepletionApi[]>(depletionPath),
      apiGet<DailyBriefApi>(briefPath),
    ]);
  } catch {
    const fallback = 1;
    [kpis, heatmap, alertsRaw, depletionRaw, brief] = await Promise.all([
      apiGet<StoreKpisApi>(`/stores/${fallback}/kpis`),
      apiGet<HeatmapApi>(`/stores/${fallback}/heatmap`),
      apiGet<AlertApi[]>(`/alerts?resolved=false&store_id=${fallback}&limit=12`),
      apiGet<DepletionApi[]>(`/analytics/depletion?store_id=${fallback}`),
      apiGet<DailyBriefApi>(`/insights/daily-brief?store_id=${fallback}`),
    ]);
  }

  const columns = aisleColumnsFromHeatmap(heatmap);
  const alerts = alertsRaw.slice(0, 8).map(mapAlert);
  const depletion = depletionRaw.slice(0, 5).map(mapDepletion);

  return {
    kpis,
    heatmap,
    columns,
    alerts,
    depletion,
    brief,
    effectiveStoreId: kpis.store_id,
  };
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: { store?: string };
}) {
  const stores = await apiGet<StoreApiRow[]>("/stores").catch(() => []);
  const defaultId = stores[0]?.id ?? 1;
  const raw = parseInt(searchParams.store || String(defaultId), 10);
  const storeId = Number.isFinite(raw) && raw > 0 ? raw : defaultId;

  const { kpis, columns, alerts, depletion, brief, effectiveStoreId } =
    await loadDashboard(storeId);

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-[var(--rp-fg)]">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-[var(--rp-muted)]">
          Real-time shelf intelligence for{" "}
          <span className="text-[var(--rp-fg)]">{kpis.store_name}</span>
          {effectiveStoreId !== storeId ? (
            <span className="text-amber-400/90"> (showing store {effectiveStoreId})</span>
          ) : null}
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KPICard
          title="Health score"
          value={`${Math.round(kpis.health_score)}/100`}
          subtitle="Composite store health"
          accent="emerald"
        />
        <KPICard
          title="Occupancy avg"
          value={`${kpis.occupancy_avg.toFixed(1)}%`}
          subtitle="Shelf fullness"
        />
        <KPICard
          title="Stockouts / alerts"
          value={kpis.stockout_count}
          subtitle={`${kpis.active_alerts} active alerts`}
          accent="amber"
        />
        <KPICard
          title="Revenue at risk"
          value={`€${kpis.revenue_at_risk_eur.toLocaleString("en-GB", { maximumFractionDigits: 0 })}`}
          subtitle={`${kpis.predicted_stockouts_24h} predicted 24h · scan ${kpis.scan_coverage_pct.toFixed(0)}%`}
          accent="rose"
        />
      </section>

      <ShelfHeatmap columns={columns} />

      <div className="grid gap-6 lg:grid-cols-2">
        <StockoutPrediction items={depletion} />
        <AlertFeed alerts={alerts} storeId={effectiveStoreId} />
      </div>

      <AiInsightCard text={brief.brief} />

      <p className="text-center text-xs text-[var(--rp-muted)]">
        Change store via the header selector. Backend OpenAPI:{" "}
        <code className="rounded bg-[var(--rp-panel)] px-1 py-0.5 text-[var(--rp-accent)]">
          {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/docs
        </code>
      </p>
    </div>
  );
}
