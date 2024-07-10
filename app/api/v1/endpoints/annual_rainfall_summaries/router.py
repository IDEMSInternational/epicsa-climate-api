from typing import OrderedDict

from app.epicsawrap_link import annual_rainfall_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.core.responce_models.rainfall_summaries_responce_model import AnnualRainfallSummariesResponce

from .schema import (
    AnnualRainfallSummariesParameters,
)

router = APIRouter()


@router.post("/", response_model=AnnualRainfallSummariesResponce)
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters
) -> OrderedDict:
    if (params.override == None):
        params.override = False
    return run_epicsa_function_and_get_dataframe(
        annual_rainfall_summaries,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        summaries=params.summaries,
    )
       
