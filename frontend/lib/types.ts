/**
 * Domain types — Section 7.2 Key Component Specifications
 */

export type ProductCategory =
  | "dairy"
  | "bakery"
  | "beverages"
  | "snacks"
  | "fresh_produce"
  | "meat"
  | "frozen"
  | "household"
  | "personal_care"
  | "alcohol";

export type AlertType =
  | "stockout"
  | "low_stock"
  | "planogram_violation"
  | "spoilage_risk"
  | "misplaced_item"
  | "price_tag_missing"
  | "unusual_depletion";

export type AlertSeverity = "critical" | "high" | "medium" | "low" | "info";

export interface ShelfIssue {
  type: string;
  severity: string;
  description?: string;
}

export interface Store {
  id: number;
  name: string;
  chain: "Konzum" | "Spar" | "Plodine" | "Tommy" | "Studenac" | string;
  city: string;
  healthScore: number;
  occupancyAvg: number;
  activeAlerts: number;
  stockoutCount: number;
  revenueAtRisk: number;
  lastScanAt: string;
}

export interface Aisle {
  id: number;
  storeId: number;
  name: string;
  aisleNumber: number;
  category: ProductCategory | string;
  occupancyPct: number;
  complianceScore: number;
  productCount: number;
  issues: ShelfIssue[];
}

export interface ShelfScanResult {
  scanId: number;
  timestamp: string;
  overallOccupancy: number;
  productsDetected: number;
  emptySlots: number;
  detections: DetectedProduct[];
  issues: ShelfIssue[];
  geminiInsight: string;
  processingTimeMs: number;
}

export interface DetectedProduct {
  productName: string;
  sku?: string;
  boundingBox: { x: number; y: number; w: number; h: number };
  confidence: number;
  quantityEstimated: number;
  shelfPosition: number;
}

export interface Alert {
  id: number;
  storeId: number;
  aisleId?: number;
  productName?: string;
  alertType: AlertType | string;
  severity: AlertSeverity;
  title: string;
  description: string;
  recommendedAction: string;
  revenueImpact: number;
  createdAt: string;
  isResolved: boolean;
}

export interface DepletionForecast {
  productName: string;
  currentQuantity: number;
  depletionRatePerHour: number;
  hoursToStockout: number;
  predictedStockoutTime: string;
  recommendedRestockQty: number;
  urgency: "critical" | "high" | "medium" | "low";
}

/** API (FastAPI) — snake_case */
export interface StoreApiRow {
  id: number;
  name: string;
  chain: string;
  city: string | null;
  health_score: number | null;
  status: string;
  last_scan_at: string | null;
  occupancy_avg: number;
  active_alerts: number;
}

export interface StoreKpisApi {
  store_id: number;
  store_name: string;
  health_score: number;
  occupancy_avg: number;
  stockout_count: number;
  active_alerts: number;
  predicted_stockouts_24h: number;
  waste_risk_items: number;
  revenue_at_risk_eur: number;
  scan_coverage_pct: number;
}

export interface HeatmapCellApi {
  aisle_id: number;
  aisle_number: number | null;
  category: string | null;
  shelf_row: number;
  occupancy_pct: number;
}

export interface HeatmapApi {
  store_id: number;
  store_name: string;
  grid: HeatmapCellApi[];
  aisles: {
    id: number;
    name: string | null;
    aisle_number: number | null;
    category: string | null;
    occupancy_pct: number | null;
    compliance_score: number | null;
    total_shelves: number | null;
  }[];
}

export interface AlertApi {
  id: number;
  store_id: number;
  aisle_id: number | null;
  product_id: number | null;
  alert_type: string;
  severity: string;
  title: string | null;
  description: string | null;
  recommended_action: string | null;
  estimated_revenue_impact: number | null;
  is_resolved: boolean;
  created_at: string;
}

export interface DepletionApi {
  product_id: number;
  product_name: string;
  current_quantity: number;
  depletion_rate_per_hour: number;
  predicted_stockout_time: string;
  recommended_restock_quantity: number;
  confidence: number;
}

export interface DailyBriefApi {
  store_id: number;
  brief: string;
  generated_at: string;
}
