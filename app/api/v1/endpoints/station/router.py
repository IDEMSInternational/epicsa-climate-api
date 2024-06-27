from fastapi import APIRouter
from typing import OrderedDict, List
from app.epicsawrap_link import station_metadata
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.definitions import country_code
from app.core.responce_models.station_responce_model import StationDataResponce,StationAndDefintionResponce
from .schema import Station

router = APIRouter()

@router.get("/")#,response_model=List[StationDataResponce])
def read_stations() -> OrderedDict:
    res = run_epicsa_function_and_get_dataframe(
        station_metadata,
        country="",
        station_id="",
        include_definitions=False,
    )
    return res['data']

@router.get("/{country}")#,response_model=List[StationDataResponce])
def read_stations(country: country_code ) -> OrderedDict:
    res = run_epicsa_function_and_get_dataframe(
        station_metadata,
        country=country,
        station_id="",
        include_definitions=False,
    )
    return res['data']

@router.get("/{country}/{station_id}")#,response_model=StationAndDefintionResponce)
def read_stations(country: country_code, station_id:str ): #-> OrderedDict:
    res = station_metadata(
        country=country,
        station_id=station_id,
        include_definitions=True,
    )
    return res

