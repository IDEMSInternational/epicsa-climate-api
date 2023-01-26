from fastapi import APIRouter

from app.api.v1.endpoints.station.router import router as station_router

v1_router = APIRouter()
v1_router.include_router(station_router, prefix="/station", tags=["login"])
