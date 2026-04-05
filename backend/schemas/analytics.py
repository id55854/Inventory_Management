from datetime import datetime

from pydantic import BaseModel


class StoreKPIs(BaseModel):
    store_id: int
    store_name: str
    health_score: float
    occupancy_avg: float
    stockout_count: int
    active_alerts: int
    predicted_stockouts_24h: int
    waste_risk_items: int
    revenue_at_risk_eur: float
    scan_coverage_pct: float


class DepletionForecast(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    depletion_rate_per_hour: float
    predicted_stockout_time: datetime
    recommended_restock_quantity: int
    confidence: float


class DashboardGlobal(BaseModel):
    """GET /analytics/dashboard — all stores."""

    store_count: int
    avg_health_score: float
    occupancy_avg: float
    active_alerts: int
    total_stockouts: int
    predicted_stockouts_24h: int
    waste_risk_items: int
    revenue_at_risk_eur: float


class TrendsResponse(BaseModel):
    store_id: int | None
    days: int
    category: str | None
    series: list[dict]


class WasteRiskItem(BaseModel):
    product_id: int
    product_name: str
    category: str | None
    shelf_life_days: int | None
    days_to_expiry_estimate: int
    risk_score: float
    recommended_action: str


class StoreBenchmark(BaseModel):
    store_id: int
    store_name: str
    chain: str
    health_score: float | None
    occupancy_avg: float
    active_alerts: int
    revenue_at_risk_eur: float


class ComparisonsResponse(BaseModel):
    stores: list[StoreBenchmark]
