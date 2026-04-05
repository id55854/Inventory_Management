from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StoreListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chain: str
    city: str | None
    health_score: float | None
    status: str
    last_scan_at: datetime | None


class StoreSummary(BaseModel):
    """List stores with aggregates (Section 5)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chain: str
    city: str | None
    health_score: float | None
    status: str
    last_scan_at: datetime | None
    occupancy_avg: float = Field(description="Average aisle occupancy %")
    active_alerts: int = 0


class AisleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    aisle_number: int | None
    category: str | None
    occupancy_pct: float | None
    compliance_score: float | None = None
    total_shelves: int | None = None


class ShelfStateBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shelf_position: int | None
    timestamp: datetime
    occupancy_pct: float | None
    product_counts: dict | list | None = None
    detected_issues: list | dict | None = None
    scan_id: int | None = None


class AisleDetail(BaseModel):
    aisle: AisleBrief
    shelf_states: list[ShelfStateBrief]


class StoreDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    chain: str
    city: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    status: str
    health_score: float | None
    total_aisles: int | None
    total_shelves: int | None
    last_scan_at: datetime | None
    created_at: datetime | None
    occupancy_avg: float


class HeatmapCell(BaseModel):
    aisle_id: int
    aisle_number: int | None
    category: str | None
    shelf_row: int
    occupancy_pct: float


class HeatmapResponse(BaseModel):
    store_id: int
    store_name: str
    grid: list[HeatmapCell]
    aisles: list[AisleBrief]
