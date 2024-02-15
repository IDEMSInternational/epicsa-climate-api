from fastapi import APIRouter
from typing import OrderedDict, List
from app.epicsawrap_link import station_metadata
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.definitions import country_name
from .schema import Station

router = APIRouter()

@router.get("/",response_model=List[Station])
def read_stations() -> OrderedDict:
    res= run_epicsa_function_and_get_dataframe(
        station_metadata,
        country="",
        station_id="",
        include_definitions=True,
    )
    return res['data']

@router.get("/{country}")
def read_stations(country: country_name ) -> OrderedDict:
    return run_epicsa_function_and_get_dataframe(
        station_metadata,
        country=country,
        station_id="",
        include_definitions=True,
    )

@router.get("/{country}/{station_id}")
def read_stations(country: country_name, station_id:str ) -> OrderedDict:
    return run_epicsa_function_and_get_dataframe(
        station_metadata,
        country=country,
        station_id=station_id,
        include_definitions=True,
    )

