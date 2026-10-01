from fastapi import APIRouter, Depends

from app.core.responce_models.temperature_responce_model import (
    AnnualTemperatureSummariesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import AnnualTemperatureSummariesParameters

router = APIRouter()


@router.post("/", response_model=AnnualTemperatureSummariesResponce)
def get_annual_temperature_summaries(
    params: AnnualTemperatureSummariesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> AnnualTemperatureSummariesResponce:
    """Retrieve annual temperature summaries from PostgreSQL."""
    return repo.get_annual_temperature_summaries(
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
