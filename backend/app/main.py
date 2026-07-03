from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import merchant_auth, reservations, surprise_bags

from app import models
from app.db import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Foodtopia API",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(merchant_auth.router)
app.include_router(surprise_bags.router)
app.include_router(reservations.router)
