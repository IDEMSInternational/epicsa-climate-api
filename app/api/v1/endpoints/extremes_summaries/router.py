from typing import OrderedDict

from app.epicsawrap_link import extremes_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.core.responce_models.extremes_summaries_responce_model import ExtremesSummariesResponce

from .schema import (
    ExtremesSummariesParameters,
)

router = APIRouter()


@router.post("/")#,response_model=ExtremesSummariesResponce)
def get_extremes_summaries(
    params: ExtremesSummariesParameters,
) -> OrderedDict:
    if (params.override == None):
        params.override = False
    return run_epicsa_function_and_get_dataframe(
        extremes_summaries,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        summaries=params.summaries,
    )
       
