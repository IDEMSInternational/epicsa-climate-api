from fastapi import APIRouter

from app.api.v1.endpoints.annual_rainfall_summaries.router import (
    router as annual_rainfall_summaries_router,
)
from app.api.v1.endpoints.annual_temperature_summaries.router import (
    router as annual_temperature_summaries_router,
)
from app.api.v1.endpoints.crop_success_probabilities.router import (
    router as crop_success_probabilities_router,
)
from app.api.v1.endpoints.monthly_temperature_summaries.router import (
    router as monthly_temperature_summaries_router,
)
from app.api.v1.endpoints.season_start_probabilities.router import (
    router as season_start_probabilities_router,
)
from app.api.v1.endpoints.seasonal_forecast_list.router import (
    router as seasonal_forecast_list_router,
)
from app.api.v1.endpoints.seasonal_forecast_pdf.router import (
    router as seasonal_forecast_pdf_router,
)
from app.api.v1.endpoints.station.router import router as station_router
from app.api.v1.endpoints.status.router import router as status_router

v1_router = APIRouter()

v1_router.include_router(status_router, prefix="/status", tags=["Testing"])

v1_router.include_router(
    annual_rainfall_summaries_router,
    prefix="/annual_rainfall_summaries",
    tags=["Climate"],
)
v1_router.include_router(
    annual_temperature_summaries_router,
    prefix="/annual_temperature_summaries",
    tags=["Climate"],
)
v1_router.include_router(
    crop_success_probabilities_router,
    prefix="/crop_success_probabilities",
    tags=["Climate"],
)
v1_router.include_router(
    monthly_temperature_summaries_router,
    prefix="/monthly_temperature_summaries",
    tags=["Climate"],
)
v1_router.include_router(
    season_start_probabilities_router,
    prefix="/season_start_probabilities",
    tags=["Climate"],
)
v1_router.include_router(
    seasonal_forecast_list_router,
    prefix="/seasonal_forecast_list",
    tags=["Forecast"],
)
v1_router.include_router(
    seasonal_forecast_pdf_router,
    prefix="/seasonal_forecast_pdf",
    tags=["Forecast"],
)
v1_router.include_router(station_router, prefix="/station", tags=["Work In Progress"])

