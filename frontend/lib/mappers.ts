import type { Alert, AlertApi, DepletionApi, DepletionForecast } from "./types";

export function mapAlert(a: AlertApi): Alert {
  return {
    id: a.id,
    storeId: a.store_id,
    aisleId: a.aisle_id ?? undefined,
    productName: undefined,
    alertType: a.alert_type,
    severity: a.severity as Alert["severity"],
    title: a.title || "",
    description: a.description || "",
    recommendedAction: a.recommended_action || "",
    revenueImpact: a.estimated_revenue_impact ?? 0,
    createdAt: a.created_at,
    isResolved: a.is_resolved,
  };
}

export function mapDepletion(d: DepletionApi): DepletionForecast {
  const end = new Date(d.predicted_stockout_time).getTime();
  const hours = Math.max(0, (end - Date.now()) / 3_600_000);
  let urgency: DepletionForecast["urgency"] = "low";
  if (hours < 2) urgency = "critical";
  else if (hours < 6) urgency = "high";
  else if (hours < 24) urgency = "medium";

  return {
    productName: d.product_name,
    currentQuantity: d.current_quantity,
    depletionRatePerHour: d.depletion_rate_per_hour,
    hoursToStockout: Math.round(hours * 10) / 10,
    predictedStockoutTime: d.predicted_stockout_time,
    recommendedRestockQty: d.recommended_restock_quantity,
    urgency,
  };
}
