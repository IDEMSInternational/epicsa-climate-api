from typing import OrderedDict
from app.core.responce_models.temperature_responce_model import AnnualTemperatureSummariesResponce

from app.epicsawrap_link  import annual_temperature_summaries
from fastapi import APIRouter, Depends
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function, handle_epicsa_request

from .schema import (
    AnnualTemperatureSummariesParameters,
)

router = APIRouter()


@router.post("/", response_model=AnnualTemperatureSummariesResponce)
def get_annual_temperature_summaries(
    params: AnnualTemperatureSummariesParameters,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
) -> OrderedDict:
    if (params.override == None):
        params.override = False
    return handle_epicsa_request(
        annual_temperature_summaries,
        response_model=AnnualTemperatureSummariesResponce,
        run_epicsa_function=run_epicsa_function,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        summaries=params.summaries,
    )



