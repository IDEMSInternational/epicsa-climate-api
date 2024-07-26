from typing import Any, Dict, OrderedDict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from app.core.responce_models.rainfall_summaries_responce_model import AnnualRainfallSummariesResponce
from .schema import AnnualRainfallSummariesParameters
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType,  get_run_epicsa_function, handle_epicsa_request
from app.epicsawrap_link import annual_rainfall_summaries

router = APIRouter()



@router.post("/", response_model=AnnualRainfallSummariesResponce)
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)
) -> AnnualRainfallSummariesResponce:
    if params.override is None:
        params.override = False
    return handle_epicsa_request(
        epicsa_function=annual_rainfall_summaries,
        response_model=AnnualRainfallSummariesResponce,
        run_epicsa_function=run_epicsa_function,
        country=params.country,
        station_id=params.station_id,
        override=params.override,
        summaries=params.summaries,
    )
