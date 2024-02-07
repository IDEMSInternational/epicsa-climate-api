from typing import OrderedDict

from app.epicsawrap_link import extremes_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe

from .schema import (
    ExtremesSummariesParameters,
)

router = APIRouter()


@router.post("/")
def get_extremes_summaries(
    params: ExtremesSummariesParameters,
) -> OrderedDict:
    
    return run_epicsa_function_and_get_dataframe(
        extremes_summaries,
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )
       
