from fastapi import APIRouter, Depends

from app.core.responce_models.rainfall_summaries_responce_model import (
    AnnualRainfallSummariesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import AnnualRainfallSummariesParameters

router = APIRouter()


@router.post("/", response_model=AnnualRainfallSummariesResponce)
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> AnnualRainfallSummariesResponce:
    """Retrieve annual rainfall summaries from PostgreSQL."""
    return repo.get_annual_rainfall_summaries(
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
