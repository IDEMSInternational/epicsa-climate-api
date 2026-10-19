from fastapi import APIRouter, Depends

from app.core.responce_models.rainfall_summaries_responce_model import (
    MonthlyRainfallSummariesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import MonthlyRainfallSummariesParameters

router = APIRouter()


@router.post("/", response_model=MonthlyRainfallSummariesResponce)
def get_monthly_rainfall_summaries(
    params: MonthlyRainfallSummariesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> MonthlyRainfallSummariesResponce:
    """Retrieve monthly rainfall summaries from PostgreSQL."""
    return repo.get_monthly_rainfall_summaries(
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
