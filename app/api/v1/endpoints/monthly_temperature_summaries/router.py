from typing import OrderedDict

from app.epicsawrap_link import monthly_temperature_summaries
from fastapi import APIRouter, Depends
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function, handle_epicsa_request
from app.core.responce_models.temperature_responce_model import MonthlyTemperatureSummariesResponce

from .schema import (
    MonthlyTemperatureSummariesParameters,
)

router = APIRouter()


@router.post("/",response_model=MonthlyTemperatureSummariesResponce)
def get_monthly_temperature_summaries(
    params: MonthlyTemperatureSummariesParameters,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
) -> OrderedDict:
    if (params.override == None):
        params.override = False
    return handle_epicsa_request(
        monthly_temperature_summaries,
        response_model=MonthlyTemperatureSummariesResponce,
        run_epicsa_function=run_epicsa_function,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        summaries=params.summaries,
    )