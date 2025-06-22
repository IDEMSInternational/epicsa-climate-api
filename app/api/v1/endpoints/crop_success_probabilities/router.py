from typing import OrderedDict

from app.epicsawrap_link  import crop_success_probabilities
from fastapi import APIRouter, Depends
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function, handle_epicsa_request
from app.core.responce_models.crop_success_probabilities_model import CropSuccessProbabilitiesResponce

from .schema import (
    CropSuccessProbabilitiesParameters,
)

router = APIRouter()


@router.post("/",response_model=CropSuccessProbabilitiesResponce)
def get_crop_success_probabilities(
    params: CropSuccessProbabilitiesParameters,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
) -> OrderedDict:
    return handle_epicsa_request(
        crop_success_probabilities,
        response_model=CropSuccessProbabilitiesResponce,
        run_epicsa_function=run_epicsa_function,
        country=params.country,
        station_id=params.station_id
    )

