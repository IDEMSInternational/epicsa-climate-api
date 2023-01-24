from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from . import schema, crud

router = APIRouter()


@router.get("/", response_model=List[schema.Station])
def read_stations(
    db: Session = Depends(get_session),
) -> Any:
    """
    Retrieve stations.
    """
    stations = crud.station.get_multi(db)
    print('stations', stations)
    return stations


@router.get("/{id}", response_model=schema.Station)
def read_station(
    *,
    db: Session = Depends(get_session),
    id: int,
) -> Any:
    """
    Get station by ID.
    """
    return {id: 1}
