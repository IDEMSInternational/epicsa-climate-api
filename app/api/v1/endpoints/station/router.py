from fastapi import APIRouter, Depends
from typing import OrderedDict

from app.epicsawrap_link import station_metadata
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function, handle_epicsa_request
from app.definitions import country_code
from app.core.responce_models.station_responce_model import StationListResponce,StationAndDefintionResponce

router = APIRouter()


@router.get("/{country}",response_model=StationListResponce)
def read_stations(
    country: country_code,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function) 
) -> OrderedDict:
    return handle_epicsa_request(
        station_metadata,
        response_model=StationListResponce,
        run_epicsa_function=run_epicsa_function,
        country=country,
        station_id="",
        include_definitions=False,
    )

@router.get("/{country}/{station_id}",response_model=StationAndDefintionResponce)
def read_stations(
    country: country_code, 
    station_id:str,
    run_epicsa_function: RunEpicsaFunctionType = Depends(get_run_epicsa_function)   
) -> OrderedDict:
    return handle_epicsa_request(
        station_metadata,
        response_model=StationAndDefintionResponce,
        run_epicsa_function=run_epicsa_function,
        has_dataframe=False,
        country=country,
        station_id=station_id,
        include_definitions=True,
    )
    

