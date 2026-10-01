from fastapi import APIRouter, Depends

from app.core.responce_models.temperature_responce_model import (
    MonthlyTemperatureSummariesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import MonthlyTemperatureSummariesParameters

router = APIRouter()


@router.post("/", response_model=MonthlyTemperatureSummariesResponce)
def get_monthly_temperature_summaries(
    params: MonthlyTemperatureSummariesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> MonthlyTemperatureSummariesResponce:
    """Retrieve monthly temperature summaries from PostgreSQL."""
    return repo.get_monthly_temperature_summaries(
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
