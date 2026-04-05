from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product, ProductCategory
from schemas.product import CategorySummary, ProductDetail, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=list[CategorySummary])
def product_categories(db: Session = Depends(get_db)) -> list[CategorySummary]:
    rows = (
        db.query(
            Product.category,
            func.count(Product.id),
            func.avg(Product.unit_price),
        )
        .group_by(Product.category)
        .all()
    )
    per_map: dict[str, int] = {}
    for cat, cnt in (
        db.query(Product.category, func.count(Product.id))
        .filter(Product.is_perishable.is_(True))
        .group_by(Product.category)
        .all()
    ):
        key = cat.value if cat and hasattr(cat, "value") else str(cat)
        per_map[key] = int(cnt)

    out: list[CategorySummary] = []
    for cat, cnt, avg_p in rows:
        cval = cat.value if cat and hasattr(cat, "value") else (str(cat) if cat else "unknown")
        out.append(
            CategorySummary(
                category=cval,
                product_count=int(cnt),
                avg_unit_price=float(avg_p) if avg_p is not None else None,
                perishable_count=per_map.get(cval, 0),
            )
        )
    return out


@router.get("", response_model=list[ProductOut])
def list_products(
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[Product]:
    q = db.query(Product).order_by(Product.id)
    if category:
        try:
            q = q.filter(Product.category == ProductCategory(category))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category") from None
    return q.all()


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDetail:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    vel = float(p.avg_daily_sales or 0.0)
    base = ProductOut.model_validate(p, from_attributes=True)
    return ProductDetail(**base.model_dump(), sales_velocity_units_per_day=vel)
