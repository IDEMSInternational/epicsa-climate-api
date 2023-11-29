from typing import OrderedDict

from epicsa_python.epicsa import annual_temperature_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe

from .schema import (
    AnnualTemperatureSummariesParameters,
)

router = APIRouter()


@router.post("/")
def get_annual_temperature_summaries(
    params: AnnualTemperatureSummariesParameters,
) -> OrderedDict:
    
    return run_epicsa_function_and_get_dataframe(
        annual_temperature_summaries,
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )



