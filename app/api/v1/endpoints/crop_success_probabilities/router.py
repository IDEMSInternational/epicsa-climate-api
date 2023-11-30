from typing import OrderedDict

from epicsa_python.epicsa import crop_success_probabilities
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe

from .schema import (
    CropSuccessProbabilitiesParameters,
)

router = APIRouter()


@router.post("/")
def get_crop_success_probabilities(
    params: CropSuccessProbabilitiesParameters,
) -> OrderedDict:
        
    return run_epicsa_function_and_get_dataframe(
        crop_success_probabilities,
        country=params.country,
        station_id=params.station_id,
        water_requirements=params.water_requirements,
        planting_length=params.planting_length,
        planting_dates=params.planting_dates,
        start_before_season=params.start_before_season,
    )

