"""Product, SKU, Category models."""

import enum

from sqlalchemy import Boolean, Column, Enum, Float, Integer, String

from database import Base


class ProductCategory(str, enum.Enum):
    DAIRY = "dairy"
    BAKERY = "bakery"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    FRESH_PRODUCE = "fresh_produce"
    MEAT = "meat"
    FROZEN = "frozen"
    HOUSEHOLD = "household"
    PERSONAL_CARE = "personal_care"
    ALCOHOL = "alcohol"


def _enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [e.value for e in enum_cls]


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    ean = Column(String, nullable=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(Enum(ProductCategory, values_callable=_enum_values, native_enum=False), nullable=True)
    subcategory = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    shelf_life_days = Column(Integer, nullable=True)
    min_shelf_quantity = Column(Integer, default=3)
    max_shelf_quantity = Column(Integer, default=20)
    avg_daily_sales = Column(Float, nullable=True)
    supplier = Column(String, nullable=True)
    lead_time_hours = Column(Integer, default=24)
    is_perishable = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
