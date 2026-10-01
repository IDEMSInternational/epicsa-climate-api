from fastapi import APIRouter, Depends

from app.core.responce_models.season_start_probabilities import (
    SeasonStartProbabilitiesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import SeasonStartProbabilitiesParameters

router = APIRouter()


@router.post("/", response_model=SeasonStartProbabilitiesResponce)
def get_season_start_probabilities(
    params: SeasonStartProbabilitiesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> SeasonStartProbabilitiesResponce:
    """Retrieve cumulative season start probabilities from PostgreSQL."""
    return repo.get_season_start_probabilities(
        country=params.country,
        station_id=params.station_id,
        start_dates=params.start_dates,
    )
