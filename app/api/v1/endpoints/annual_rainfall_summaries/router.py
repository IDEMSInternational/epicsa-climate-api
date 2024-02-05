from typing import OrderedDict

from app.epicsawrap_link import annual_rainfall_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe

from .schema import (
    AnnualRainfallSummariesParameters,
)

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters,
) -> OrderedDict:
    
    return run_epicsa_function_and_get_dataframe(
        annual_rainfall_summaries,
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
       
