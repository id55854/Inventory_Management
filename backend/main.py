"""FastAPI app entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data.seed import seed_database
from database import Base, SessionLocal, engine
from routers import alerts, analytics, insights, products, scans, stores

# Import models so Base.metadata registers all tables
from models import Alert, Aisle, Product, ShelfScan, ShelfState, Store  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="RetailPulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stores.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
