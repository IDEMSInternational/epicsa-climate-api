from fastapi import APIRouter

from app.api.v1.endpoints.station.router import router as station_router
from app.api.v1.endpoints.annual_rainfall_summaries.router import router as annual_rainfall_summaries_router

v1_router = APIRouter()
v1_router.include_router(station_router, prefix="/station", tags=["login"])
v1_router.include_router(annual_rainfall_summaries_router, prefix="/annual_rainfall_summaries", tags=["login"])
