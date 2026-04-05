from pydantic import BaseModel, Field


class AnalyzeShelfRequest(BaseModel):
    image_base64: str
    context: str | None = None


class AnalyzeShelfResponse(BaseModel):
    summary: str
    issues: list[dict]
    recommendations: list[str]


class StoreReportRequest(BaseModel):
    store_id: int = Field(..., ge=1)


class StoreReportResponse(BaseModel):
    report: str
    key_actions: list[str]


class DailyBriefResponse(BaseModel):
    store_id: int
    brief: str
    generated_at: str
