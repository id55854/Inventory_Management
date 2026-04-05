import { mapAlert, mapDepletion } from "@/lib/mappers";
import type { AisleHeatColumn } from "@/lib/heatmap";
import type {
  DailyBriefApi,
  DepletionApi,
  HeatmapApi,
  StoreKpisApi,
  AlertApi,
} from "@/lib/types";

export type DashboardPayload = {
  kpis: StoreKpisApi;
  heatmap: HeatmapApi;
  columns: AisleHeatColumn[];
  alerts: ReturnType<typeof mapAlert>[];
  depletion: ReturnType<typeof mapDepletion>[];
  brief: DailyBriefApi;
  effectiveStoreId: number;
  apiOffline: boolean;
};

/** Shown when the backend cannot be reached (e.g. missing NEXT_PUBLIC_API_URL on Vercel). */
export function offlineDashboardPayload(storeId: number): DashboardPayload {
  const kpis: StoreKpisApi = {
    store_id: storeId,
    store_name: "API unavailable",
    health_score: 0,
    occupancy_avg: 0,
    stockout_count: 0,
    active_alerts: 0,
    predicted_stockouts_24h: 0,
    waste_risk_items: 0,
    revenue_at_risk_eur: 0,
    scan_coverage_pct: 0,
  };

  const heatmap: HeatmapApi = {
    store_id: storeId,
    store_name: "API unavailable",
    grid: [],
    aisles: [],
  };

  const brief: DailyBriefApi = {
    store_id: storeId,
    brief:
      "The dashboard could not reach your API. In Vercel → Project → Settings → Environment Variables, set NEXT_PUBLIC_API_URL to your deployed API origin (no trailing slash), redeploy, then refresh.",
    generated_at: new Date().toISOString(),
  };

  const alertsRaw: AlertApi[] = [];
  const depletionRaw: DepletionApi[] = [];

  return {
    kpis,
    heatmap,
    columns: [],
    alerts: alertsRaw.map(mapAlert),
    depletion: depletionRaw.map(mapDepletion),
    brief,
    effectiveStoreId: storeId,
    apiOffline: true,
  };
}
