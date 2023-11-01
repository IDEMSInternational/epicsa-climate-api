from fastapi import APIRouter, Depends, HTTPException

from .schema import Station

router = APIRouter()


@router.get("/")
def read_stations() -> list[Station]:
    """
    Retrieve stations.
    """
    raise HTTPException(status_code=404, detail="Method not yet implemented")


@router.get("/{id}")
def read_station(*, id: int) -> Station:
    """
    Get station by ID.
    """
    raise HTTPException(status_code=404, detail="Method not yet implemented")
