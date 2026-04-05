import type { HeatmapApi } from "./types";

export interface AisleHeatColumn {
  aisleId: number;
  aisleNumber: number | null;
  label: string;
  category: string;
  occupancyPct: number;
  alert?: boolean;
}

/** One column per aisle — avg occupancy across shelf rows; flag low occupancy as alert. */
export function aisleColumnsFromHeatmap(data: HeatmapApi): AisleHeatColumn[] {
  const sums = new Map<number, { sum: number; n: number }>();
  for (const c of data.grid) {
    const cur = sums.get(c.aisle_id) || { sum: 0, n: 0 };
    cur.sum += c.occupancy_pct;
    cur.n += 1;
    sums.set(c.aisle_id, cur);
  }

  return data.aisles.map((a) => {
    const agg = sums.get(a.id);
    const occ =
      agg && agg.n > 0 ? agg.sum / agg.n : (a.occupancy_pct ?? 0);
    const cat = (a.category || "aisle").replace(/_/g, " ");
    const label =
      a.name ||
      `Aisle ${a.aisle_number ?? a.id} — ${cat}`;
    return {
      aisleId: a.id,
      aisleNumber: a.aisle_number,
      label,
      category: cat,
      occupancyPct: Math.round(occ * 10) / 10,
      alert: occ < 40,
    };
  });
}
