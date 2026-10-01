from fastapi import APIRouter, Depends

from app.definitions import country_code
from app.core.responce_models.station_responce_model import (
    StationListResponce,
    StationAndDefintionResponce,
)
from app.services.climate_repository import ClimateRepository, get_climate_repository

router = APIRouter()


@router.get("/{country}", response_model=StationListResponce)
def read_stations(
    country: country_code,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> StationListResponce:
    """Retrieve all stations for a given country code."""
    stations = repo.get_stations_by_country(country)
    return StationListResponce(data=stations)


@router.get("/{country}/{station_id}", response_model=StationAndDefintionResponce)
def read_station_detail(
    country: country_code,
    station_id: str,
    repo: ClimateRepository = Depends(get_climate_repository),
) -> StationAndDefintionResponce:
    """Retrieve station metadata and climate definitions for a station."""
    return repo.get_station_detail(country=country, station_id=station_id)
