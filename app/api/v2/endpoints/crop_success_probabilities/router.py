from fastapi import APIRouter, Depends

from app.core.responce_models.crop_success_probabilities_model import (
    CropSuccessProbabilitiesResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository
from .schema import CropSuccessProbabilitiesParameters

router = APIRouter()


@router.post("/", response_model=CropSuccessProbabilitiesResponce)
def get_crop_success_probabilities(
    params: CropSuccessProbabilitiesParameters,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> CropSuccessProbabilitiesResponce:
    """Retrieve crop success probabilities from PostgreSQL."""
    return repo.get_crop_success_probabilities(
        country=params.country,
        station_id=params.station_id,
    )
