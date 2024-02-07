from typing import OrderedDict

from app.epicsawrap_link import monthly_temperature_summaries
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe

from .schema import (
    MonthlyTemperatureSummariesParameters,
)

router = APIRouter()


@router.post("/")
def get_monthly_temperature_summaries(
    params: MonthlyTemperatureSummariesParameters,
) -> OrderedDict:
    
    return run_epicsa_function_and_get_dataframe(
        monthly_temperature_summaries,
        country=params.country,
        station_id=params.station_id,
        summaries=params.summaries,
    )