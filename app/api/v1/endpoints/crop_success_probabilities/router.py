from typing import OrderedDict

from app.epicsawrap_link  import crop_success_probabilities
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.core.responce_models.crop_success_probabilities_model import CropSuccessProbabilitiesResponce

from .schema import (
    CropSuccessProbabilitiesParameters,
)

router = APIRouter()


@router.post("/")#,response_model=CropSuccessProbabilitiesResponce)
def get_crop_success_probabilities(
    params: CropSuccessProbabilitiesParameters,
) -> OrderedDict:
    if (params.override == None):
        params.override = False    
    return run_epicsa_function_and_get_dataframe(
        crop_success_probabilities,
        country=params.country,
        station_id=params.station_id,
        water_requirements=params.water_requirements,
        planting_length=params.planting_length,
        planting_dates=params.planting_dates,
        start_before_season=params.start_before_season,
        override=params.override,
    )

