from typing import OrderedDict

from app.epicsawrap_link import season_start_probabilities
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.core.responce_models.season_start_probabilities import SeasonStartProbabilitiesResponce

from .schema import (
    SeasonStartProbabilitiesParameters,
)

router = APIRouter()


@router.post("/")#,response_model=SeasonStartProbabilitiesResponce)
def get_season_start_probabilities(
    params: SeasonStartProbabilitiesParameters,
) -> OrderedDict:
    if (params.override == None):
        params.override = False
    return run_epicsa_function_and_get_dataframe(
        season_start_probabilities,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        start_dates=params.start_dates,
    )