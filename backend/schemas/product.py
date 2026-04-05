from pydantic import BaseModel, ConfigDict, field_validator


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    ean: str | None
    name: str
    name_en: str | None
    brand: str | None
    category: str | None
    subcategory: str | None
    unit_price: float | None
    shelf_life_days: int | None
    min_shelf_quantity: int | None
    max_shelf_quantity: int | None
    avg_daily_sales: float | None
    supplier: str | None
    lead_time_hours: int | None
    is_perishable: bool
    image_url: str | None

    @field_validator("category", mode="before")
    @classmethod
    def _category_str(cls, v):
        if v is None:
            return None
        return v.value if hasattr(v, "value") else str(v)


class ProductDetail(ProductOut):
    sales_velocity_units_per_day: float


class CategorySummary(BaseModel):
    category: str
    product_count: int
    avg_unit_price: float | None
    perishable_count: int
