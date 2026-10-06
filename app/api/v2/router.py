from fastapi import APIRouter

from app.api.v2.endpoints.annual_rainfall_summaries.router import (
    router as annual_rainfall_summaries_router,
)
from app.api.v2.endpoints.annual_temperature_summaries.router import (
    router as annual_temperature_summaries_router,
)
from app.api.v2.endpoints.crop_success_probabilities.router import (
    router as crop_success_probabilities_router,
)
from app.api.v2.endpoints.monthly_temperature_summaries.router import (
    router as monthly_temperature_summaries_router,
)
from app.api.v2.endpoints.season_start_probabilities.router import (
    router as season_start_probabilities_router,
)
from app.api.v2.endpoints.select_query.router import (
    router as select_query_router,
)
from app.api.v2.endpoints.documents.router import (
    router as documents_router,
)
from app.api.v2.endpoints.station.router import router as station_router
from app.api.v2.endpoints.status.router import router as status_router
from app.api.v2.endpoints.manifest.router import router as manifest_router

v2_router = APIRouter()

v2_router.include_router(status_router, prefix="/status", tags=["v2: Testing"])
v2_router.include_router(
    annual_rainfall_summaries_router,
    prefix="/annual_rainfall_summaries",
    tags=["v2: Climate"],
)
v2_router.include_router(
    annual_temperature_summaries_router,
    prefix="/annual_temperature_summaries",
    tags=["v2: Climate"],
)
v2_router.include_router(
    crop_success_probabilities_router,
    prefix="/crop_success_probabilities",
    tags=["v2: Climate"],
)
v2_router.include_router(
    monthly_temperature_summaries_router,
    prefix="/monthly_temperature_summaries",
    tags=["v2: Climate"],
)
v2_router.include_router(
    season_start_probabilities_router,
    prefix="/season_start_probabilities",
    tags=["v2: Climate"],
)
v2_router.include_router(
    station_router,
    prefix="/station",
    tags=["v2: Metadata"],
)
v2_router.include_router(
    select_query_router,
    prefix="/select_query",
    tags=["v2: Database"],
)
v2_router.include_router(
    documents_router,
    prefix="/documents",
    tags=["v2: Documents"],
)
v2_router.include_router(
    manifest_router,
    prefix="/manifest",
    tags=["v2: Discovery"],
)
