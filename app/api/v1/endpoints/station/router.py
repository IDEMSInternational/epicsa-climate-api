from fastapi import APIRouter, Depends, HTTPException
from typing import Literal, OrderedDict
from app.epicsawrap_link import station_metadata
from fastapi import APIRouter
from app.api.v1.endpoints.epicsa_data import run_epicsa_function_and_get_dataframe
from app.definitions import country_name


router = APIRouter()

@router.get("/")
def read_stations() -> OrderedDict:
    return run_epicsa_function_and_get_dataframe(
        station_metadata,
        country="",
        station_id="",
        include_definitions=True,
    )

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

