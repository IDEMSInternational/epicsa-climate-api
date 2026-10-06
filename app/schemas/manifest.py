from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

GenerationMetricStatus = Literal["no_data", "up_to_date", "update_available"]


class GenerationMetricInfo(BaseModel):
    """Metadata about a specific climate metric generation for a station."""
    available: bool = Field(..., description="Whether this metric has data available for this station")
    status: GenerationMetricStatus = Field(..., description="Availability or update status relative to query parameters")
    generation_id: Optional[str] = Field(None, description="Latest batch definition/generation ID")
    generation_timestamp: Optional[datetime] = Field(None, description="Timestamp of the generation")


class StationManifestEntry(BaseModel):
    """Manifest entry for a single station showing generation statuses across all metrics."""
    station_id: str = Field(..., description="Station identifier")
    station_name: str = Field(..., description="Station human-readable name")
    has_updates: bool = Field(..., description="True if any metric has an update available")
    latest_timestamp: Optional[datetime] = Field(None, description="Latest timestamp across all metrics for this station")
    generations: Dict[str, GenerationMetricInfo] = Field(
        ...,
        description="Map of climate metric keys (annual_rain, annual_temperature, monthly_temperature, crops, season_start_probabilities) to their generation info",
    )


class CountryManifestResponse(BaseModel):
    """Manifest response representing climate data generation inventory for a country."""
    country_code: str = Field(..., description="Country code (e.g. zm, mw, zw)")
    has_updates: bool = Field(..., description="True if any station has an update available")
    latest_timestamp: Optional[datetime] = Field(None, description="Latest generation timestamp across all stations in the country")
    station_count: int = Field(..., description="Number of stations returned in this manifest")
    stations: List[StationManifestEntry] = Field(..., description="List of station manifest entries")
