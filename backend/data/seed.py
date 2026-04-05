"""
Generate realistic synthetic data for the RetailPulse prototype.
Models a Konzum-like grocery chain with 5 stores in Zagreb / Split.
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from models.alert import Alert, AlertSeverity, AlertType
from models.product import Product, ProductCategory
from models.scan import ShelfScan
from models.store import Aisle, ShelfState, Store, StoreStatus

_DATA_DIR = Path(__file__).resolve().parent

# Croatian grocery product catalog (representative sample) — Section 8
PRODUCTS_HR: list[dict[str, Any]] = [
    {
        "name": "Dukat Mlijeko 1L 2.8%",
        "brand": "Dukat",
        "category": "dairy",
        "price": 1.19,
        "shelf_life": 10,
        "avg_daily_sales": 45,
        "perishable": True,
    },
    {
        "name": "Vindija 'z bregov Jogurt 500g",
        "brand": "Vindija",
        "category": "dairy",
        "price": 0.89,
        "shelf_life": 14,
        "avg_daily_sales": 30,
        "perishable": True,
    },
    {
        "name": "Dukat Svježi Sir 500g",
        "brand": "Dukat",
        "category": "dairy",
        "price": 2.49,
        "shelf_life": 7,
        "avg_daily_sales": 15,
        "perishable": True,
    },
    {
        "name": "Meggle Maslac 250g",
        "brand": "Meggle",
        "category": "dairy",
        "price": 2.99,
        "shelf_life": 30,
        "avg_daily_sales": 12,
        "perishable": True,
    },
    {
        "name": "Président Camembert 250g",
        "brand": "Président",
        "category": "dairy",
        "price": 3.49,
        "shelf_life": 21,
        "avg_daily_sales": 8,
        "perishable": True,
    },
    {
        "name": "Mlinar Kruh Bijeli 500g",
        "brand": "Mlinar",
        "category": "bakery",
        "price": 1.29,
        "shelf_life": 3,
        "avg_daily_sales": 60,
        "perishable": True,
    },
    {
        "name": "Pekara Dubravica Pecivo 6x",
        "brand": "Dubravica",
        "category": "bakery",
        "price": 1.99,
        "shelf_life": 2,
        "avg_daily_sales": 35,
        "perishable": True,
    },
    {
        "name": "Jana Voda 1.5L",
        "brand": "Jana",
        "category": "beverages",
        "price": 0.59,
        "shelf_life": 365,
        "avg_daily_sales": 80,
        "perishable": False,
    },
    {
        "name": "Coca-Cola 2L",
        "brand": "Coca-Cola",
        "category": "beverages",
        "price": 1.89,
        "shelf_life": 180,
        "avg_daily_sales": 50,
        "perishable": False,
    },
    {
        "name": "Cedevita Naranča 900g",
        "brand": "Cedevita",
        "category": "beverages",
        "price": 4.99,
        "shelf_life": 365,
        "avg_daily_sales": 15,
        "perishable": False,
    },
    {
        "name": "Ožujsko Pivo 0.5L",
        "brand": "Ožujsko",
        "category": "alcohol",
        "price": 1.19,
        "shelf_life": 180,
        "avg_daily_sales": 40,
        "perishable": False,
    },
    {
        "name": "Franck Čips Paprika 150g",
        "brand": "Franck",
        "category": "snacks",
        "price": 1.79,
        "shelf_life": 180,
        "avg_daily_sales": 25,
        "perishable": False,
    },
    {
        "name": "Kraš Napolitanke 420g",
        "brand": "Kraš",
        "category": "snacks",
        "price": 3.29,
        "shelf_life": 365,
        "avg_daily_sales": 20,
        "perishable": False,
    },
    {
        "name": "Dorina Čokolada Mliječna 80g",
        "brand": "Kraš",
        "category": "snacks",
        "price": 1.29,
        "shelf_life": 365,
        "avg_daily_sales": 35,
        "perishable": False,
    },
    {
        "name": "Kikiriški Bamba 150g",
        "brand": "Štark",
        "category": "snacks",
        "price": 1.49,
        "shelf_life": 180,
        "avg_daily_sales": 18,
        "perishable": False,
    },
    {
        "name": "Jabuke Idared 1kg",
        "brand": "Domestic",
        "category": "fresh_produce",
        "price": 1.99,
        "shelf_life": 14,
        "avg_daily_sales": 25,
        "perishable": True,
    },
    {
        "name": "Banane 1kg",
        "brand": "Import",
        "category": "fresh_produce",
        "price": 1.49,
        "shelf_life": 5,
        "avg_daily_sales": 40,
        "perishable": True,
    },
    {
        "name": "Rajčica Cherry 250g",
        "brand": "Domestic",
        "category": "fresh_produce",
        "price": 2.49,
        "shelf_life": 5,
        "avg_daily_sales": 20,
        "perishable": True,
    },
    {
        "name": "PIK Pileća Prsa 500g",
        "brand": "PIK Vrbovec",
        "category": "meat",
        "price": 4.99,
        "shelf_life": 5,
        "avg_daily_sales": 22,
        "perishable": True,
    },
    {
        "name": "Gavrilović Kulen 200g",
        "brand": "Gavrilović",
        "category": "meat",
        "price": 5.99,
        "shelf_life": 30,
        "avg_daily_sales": 10,
        "perishable": True,
    },
    {
        "name": "Saponia Nila Deterdžent 3L",
        "brand": "Saponia",
        "category": "household",
        "price": 6.99,
        "shelf_life": 730,
        "avg_daily_sales": 8,
        "perishable": False,
    },
    {
        "name": "Labud Toaletni Papir 10x",
        "brand": "Labud",
        "category": "household",
        "price": 4.49,
        "shelf_life": 730,
        "avg_daily_sales": 15,
        "perishable": False,
    },
]

STORES: list[dict[str, Any]] = [
    {
        "name": "Konzum Ilica 231",
        "chain": "Konzum",
        "city": "Zagreb",
        "lat": 45.8131,
        "lng": 15.9540,
        "aisles": 8,
    },
    {
        "name": "Konzum Avenue Mall",
        "chain": "Konzum",
        "city": "Zagreb",
        "lat": 45.7775,
        "lng": 15.9250,
        "aisles": 12,
    },
    {
        "name": "Spar Heinzelova",
        "chain": "Spar",
        "city": "Zagreb",
        "lat": 45.8089,
        "lng": 16.0025,
        "aisles": 10,
    },
    {
        "name": "Plodine City Center One",
        "chain": "Plodine",
        "city": "Zagreb",
        "lat": 45.8005,
        "lng": 15.9076,
        "aisles": 9,
    },
    {
        "name": "Tommy Split Joker",
        "chain": "Tommy",
        "city": "Split",
        "lat": 43.5147,
        "lng": 16.4435,
        "aisles": 7,
    },
]

AISLE_CATEGORIES = [
    "dairy",
    "bakery",
    "beverages",
    "snacks",
    "fresh_produce",
    "meat",
    "frozen",
    "household",
    "personal_care",
    "alcohol",
]


def _slug_sku(name: str, idx: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower())[:32].strip("-")
    return f"HR-{base}-{idx:04d}" if base else f"HR-SKU-{idx:05d}"


def _category_enum(cat: str) -> ProductCategory:
    return ProductCategory(cat)


def generate_shelf_state_history(days: int = 30) -> list[dict[str, Any]]:
    """30 days of shelf state snapshots (every 2 hours) — Section 8."""
    states: list[dict[str, Any]] = []
    now = datetime.utcnow()

    for store in STORES:
        for aisle_num, category in enumerate(AISLE_CATEGORIES[: store["aisles"]], 1):
            for day_offset in range(days, 0, -1):
                for hour in range(6, 22, 2):
                    timestamp = now - timedelta(days=day_offset, hours=24 - hour)
                    weekday = timestamp.weekday()

                    hour_factor = max(0.3, 1.0 - (hour - 6) * 0.05)
                    weekend_factor = 0.85 if weekday >= 4 else 1.0
                    perishable_cats = {"dairy", "bakery", "fresh_produce", "meat"}
                    category_factor = 0.8 if category in perishable_cats else 0.95
                    noise = random.uniform(-0.1, 0.1)

                    occupancy = max(
                        5.0,
                        min(
                            100.0,
                            100.0 * hour_factor * weekend_factor * category_factor + noise * 100,
                        ),
                    )

                    if random.random() < 0.03:
                        occupancy = random.uniform(0, 15)

                    states.append(
                        {
                            "store_name": store["name"],
                            "aisle_number": aisle_num,
                            "category": category,
                            "timestamp": timestamp,
                            "occupancy_pct": round(occupancy, 1),
                        }
                    )

    return states


def _alert_type(t: str) -> AlertType:
    return AlertType(t)


def _alert_severity(s: str) -> AlertSeverity:
    return AlertSeverity(s)


def generate_active_alerts() -> list[dict[str, Any]]:
    """Generate realistic current alerts — Section 8."""
    alert_templates = [
        {
            "type": "stockout",
            "severity": "critical",
            "title": "{product} — STOCKOUT",
            "description": "No units detected on shelf for {hours}h",
            "action": "Immediately restock {qty} units from backroom",
            "revenue_impact": lambda p: p["price"] * p["avg_daily_sales"] * 0.5,
        },
        {
            "type": "low_stock",
            "severity": "high",
            "title": "{product} — stockout in {hours}h",
            "description": "Only {remaining} units remaining, depleting at {rate}/hour",
            "action": "Restock {qty} units before {time}",
            "revenue_impact": lambda p: p["price"] * p["avg_daily_sales"] * 0.2,
        },
        {
            "type": "spoilage_risk",
            "severity": "medium",
            "title": "{product} — expiry risk",
            "description": "{qty} units approaching expiry in {days} days",
            "action": "Move to front of shelf, consider markdown pricing",
            "revenue_impact": lambda p: p["price"] * 5,
        },
        {
            "type": "planogram_violation",
            "severity": "low",
            "title": "{product} — wrong position",
            "description": "Detected in Aisle {wrong_aisle}, should be in Aisle {right_aisle}",
            "action": "Relocate to correct shelf position",
            "revenue_impact": lambda _: 0,
        },
    ]

    alerts: list[dict[str, Any]] = []
    for store in STORES:
        n_alerts = random.randint(3, 12)
        for _ in range(n_alerts):
            product = random.choice(PRODUCTS_HR)
            template = random.choice(alert_templates)
            fmt = {
                "product": product["name"],
                "hours": random.randint(1, 8),
                "qty": random.randint(5, 30),
                "remaining": random.randint(1, 5),
                "rate": round(random.uniform(0.5, 4.0), 1),
                "time": "14:00",
                "days": random.randint(1, 3),
                "wrong_aisle": random.randint(1, 8),
                "right_aisle": random.randint(1, 8),
            }
            alerts.append(
                {
                    "store": store["name"],
                    "aisle": random.randint(1, store["aisles"]),
                    "product": product["name"],
                    "type": template["type"],
                    "severity": template["severity"],
                    "title": template["title"].format(**fmt),
                    "description": template["description"].format(**fmt),
                    "recommended_action": template["action"].format(**fmt),
                    "revenue_impact": round(template["revenue_impact"](product), 2),
                    "created_at": datetime.utcnow() - timedelta(minutes=random.randint(5, 480)),
                }
            )

    return alerts


def _write_json_exports() -> None:
    """Persist catalog and layouts for Section 3 data files."""
    products_path = _DATA_DIR / "products_hr.json"
    stores_path = _DATA_DIR / "store_layouts.json"
    products_path.write_text(
        json.dumps(PRODUCTS_HR, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    layouts = [
        {
            "name": s["name"],
            "chain": s["chain"],
            "city": s["city"],
            "latitude": s["lat"],
            "longitude": s["lng"],
            "aisle_count": s["aisles"],
            "aisle_categories": AISLE_CATEGORIES[: s["aisles"]],
        }
        for s in STORES
    ]
    stores_path.write_text(json.dumps(layouts, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_database(db: Session) -> None:
    """Idempotent seed: products, stores, aisles, shelf history, alerts, sample scan."""
    if db.query(Store).first() is not None:
        return

    _write_json_exports()

    product_by_name: dict[str, Product] = {}
    for i, p in enumerate(PRODUCTS_HR, start=1):
        cat = p["category"]
        prod = Product(
            sku=_slug_sku(p["name"], i),
            ean=f"385{i:011d}"[:13],
            name=p["name"],
            name_en=None,
            brand=p["brand"],
            category=_category_enum(cat),
            subcategory=None,
            unit_price=p["price"],
            shelf_life_days=p["shelf_life"],
            min_shelf_quantity=3,
            max_shelf_quantity=20,
            avg_daily_sales=float(p["avg_daily_sales"]),
            supplier=None,
            lead_time_hours=24,
            is_perishable=bool(p["perishable"]),
            image_url=None,
        )
        db.add(prod)
        db.flush()
        product_by_name[p["name"]] = prod

    store_rows: dict[str, tuple[Store, list[Aisle]]] = {}
    for s in STORES:
        n_aisles = s["aisles"]
        total_shelves = n_aisles * 5
        st = Store(
            name=s["name"],
            chain=s["chain"],
            address=None,
            city=s["city"],
            latitude=s["lat"],
            longitude=s["lng"],
            status=StoreStatus.ACTIVE,
            total_aisles=n_aisles,
            total_shelves=total_shelves,
            health_score=round(random.uniform(61.0, 95.0), 1),
            last_scan_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            created_at=datetime.utcnow(),
        )
        db.add(st)
        db.flush()

        aisles: list[Aisle] = []
        for aisle_num, category in enumerate(AISLE_CATEGORIES[:n_aisles], 1):
            aisle = Aisle(
                store_id=st.id,
                name=f"Aisle {aisle_num} — {category.replace('_', ' ').title()}",
                aisle_number=aisle_num,
                category=category,
                total_shelves=5,
                occupancy_pct=round(random.uniform(55.0, 98.0), 1),
                compliance_score=round(random.uniform(70.0, 100.0), 1),
                last_scan_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            )
            db.add(aisle)
            db.flush()
            aisles.append(aisle)
        store_rows[s["name"]] = (st, aisles)

    # Shelf state time series
    for row in generate_shelf_state_history(days=30):
        st, aisles = store_rows[row["store_name"]]
        aisle = next((a for a in aisles if a.aisle_number == row["aisle_number"]), aisles[0])
        db.add(
            ShelfState(
                aisle_id=aisle.id,
                shelf_position=random.randint(1, 5),
                timestamp=row["timestamp"],
                occupancy_pct=row["occupancy_pct"],
                product_counts=None,
                detected_issues=None,
                scan_id=None,
            )
        )

    # Sample shelf scan (no image file)
    first_store, first_aisles = next(iter(store_rows.values()))
    db.add(
        ShelfScan(
            store_id=first_store.id,
            aisle_id=first_aisles[0].id if first_aisles else None,
            image_path=None,
            scan_type="seed",
            timestamp=datetime.utcnow(),
            processing_time_ms=42,
            products_detected=12,
            empty_slots_detected=2,
            overall_occupancy=78.5,
            confidence_score=0.82,
            raw_detections=None,
            gemini_summary="Seed data: shelf looks adequately stocked with minor gaps.",
        )
    )

    for a in generate_active_alerts():
        st, aisles = store_rows[a["store"]]
        aisle_obj = next((x for x in aisles if x.aisle_number == a["aisle"]), aisles[0])
        prod = product_by_name.get(a["product"])
        db.add(
            Alert(
                store_id=st.id,
                aisle_id=aisle_obj.id,
                product_id=prod.id if prod else None,
                alert_type=_alert_type(a["type"]),
                severity=_alert_severity(a["severity"]),
                title=a["title"],
                description=a["description"],
                recommended_action=a["recommended_action"],
                estimated_revenue_impact=a["revenue_impact"],
                is_resolved=False,
                resolved_at=None,
                created_at=a["created_at"],
            )
        )

    db.commit()
