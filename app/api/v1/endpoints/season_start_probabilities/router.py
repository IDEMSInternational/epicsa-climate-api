from typing import OrderedDict

from app.epicsawrap_link import season_start_probabilities
from fastapi import APIRouter, Depends
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function, handle_epicsa_request
from app.core.responce_models.season_start_probabilities import SeasonStartProbabilitiesResponce

from .schema import (
    SeasonStartProbabilitiesParameters,
)

router = APIRouter()


@router.post("/",response_model=SeasonStartProbabilitiesResponce)
def get_season_start_probabilities(
    params: SeasonStartProbabilitiesParameters,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
) -> OrderedDict:
    # Build kwargs dict, only including optional parameters if they have values
    kwargs = {
        "country": params.country,
        "station_id": params.station_id,
    }
    
    # Only include optional parameters if they are provided (not None)
    if params.override is not None:
        kwargs["override"] = params.override
    if params.start_dates is not None:
        kwargs["start_dates"] = params.start_dates
    

    return handle_epicsa_request(
        season_start_probabilities,
        response_model=SeasonStartProbabilitiesResponce,
        run_epicsa_function=run_epicsa_function,
        **kwargs
    )