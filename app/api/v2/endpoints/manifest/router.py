from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.definitions import country_code
from app.schemas.manifest import CountryManifestResponse
from app.services.climate_repository import ClimateRepository, get_climate_repository

router = APIRouter()


def _parse_query_datetime(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    val_str = str(val).strip()
    # Handle space from unencoded + in query strings (e.g. '2026-09-23T19:51:21 00:00')
    if " " in val_str and not val_str.endswith("Z"):
        parts = val_str.rsplit(" ", 1)
        if len(parts) == 2 and (":" in parts[1] or parts[1].isdigit()):
            val_str = parts[0] + "+" + parts[1]
        else:
            val_str = val_str.replace(" ", "T")
    try:
        dt = datetime.fromisoformat(val_str)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid ISO-8601 timestamp format for 'since_timestamp': {val}",
        ) from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/{country}", response_model=CountryManifestResponse)
def get_manifest(
    country: country_code = Path(..., description="Two-letter country code (e.g. zm, mw, zw)"),
    station_id: Optional[str] = Query(None, description="Optional station identifier to filter to a single station"),
    since_timestamp: Optional[str] = Query(
        None, description="Only return stations and metrics with updates newer than this ISO-8601 timestamp"
    ),
    since_generation_id: Optional[str] = Query(
        None, description="Only return stations and metrics with updates newer than this generation definition ID"
    ),
    include_up_to_date: bool = Query(
        False,
        description="Whether to include stations and metrics that are already up to date when using since_timestamp or since_generation_id",
    ),
    repo: ClimateRepository = Depends(get_climate_repository),
) -> CountryManifestResponse:
    """
    Retrieve discovery manifest of data generations for a country or station.
    Supports fast change detection and delta sync via since_timestamp and since_generation_id.
    """
    parsed_timestamp = _parse_query_datetime(since_timestamp)
    return repo.get_country_manifest(
        country=country,
        station_id=station_id,
        since_timestamp=parsed_timestamp,
        since_generation_id=since_generation_id,
        include_up_to_date=include_up_to_date,
    )
