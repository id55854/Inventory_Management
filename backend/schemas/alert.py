from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    aisle_id: int | None
    product_id: int | None
    alert_type: str
    severity: str
    title: str | None
    description: str | None
    recommended_action: str | None
    estimated_revenue_impact: float | None
    is_resolved: bool
    created_at: datetime

    @field_validator("alert_type", "severity", mode="before")
    @classmethod
    def _enum_str(cls, v):
        if v is None:
            return None
        return v.value if hasattr(v, "value") else str(v)


class AlertSummaryOut(BaseModel):
    by_severity: dict[str, int]
    total_unresolved: int


class RestockRecommendation(BaseModel):
    alert_id: int
    product_id: int | None
    product_name: str | None
    recommended_quantity: int
    rationale: str
    urgency: str
    estimated_revenue_if_unaddressed_eur: float | None
