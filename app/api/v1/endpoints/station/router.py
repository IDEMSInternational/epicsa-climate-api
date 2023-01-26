from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from .schema import Station
from app.epicsa_python.main import get_stations

router = APIRouter()


@router.get("/")
def read_stations() -> list[Station]:
    """
    Retrieve stations.
    """
    stations = get_stations()
    print('stations', stations)
    return stations


@router.get("/{id}")
def read_station(*, id: int) -> Station:
    """
    Get station by ID.
    """
    return {id: 1}
