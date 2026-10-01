from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class CropRecord(BaseModel):
    """
    Schema representing a record in the 'crop' table.
    Contains agricultural crop success and rainfall metrics for a station and season.
    """
    station_id: Optional[str] = Field(None, description="Station identifier")
    year: Optional[str] = Field(None, description="Year or agricultural season identifier")
    plant_day: Optional[float] = Field(None, description="Planting day of year (day number)")
    plant_length: Optional[float] = Field(None, description="Length of crop growing period in days")
    rain_total: Optional[float] = Field(None, description="Total rainfall during crop growing period (mm)")
    include_start_condition: Optional[bool] = Field(None, description="Whether start-of-season conditions were applied")
    summary_type: Optional[str] = Field(None, description="Type of summary (e.g. crop_success)")
    summary_element: Optional[str] = Field(None, description="Climate element summarized")
    summary_value: Optional[str] = Field(None, description="Statistical summary result value")
    definition_id: Optional[str] = Field(None, description="Associated statistical definition ID")
    status: Optional[str] = Field(None, description="Record validation or processing status")
    time_stamp: Optional[datetime] = Field(None, description="Timestamp of record creation or last update")

    class Config:
        orm_mode = True


class DefinitionRecord(BaseModel):
    """
    Schema representing a record in the 'definition' table.
    Defines statistical criteria, parameters, and metadata for climate summaries.
    """
    definition_id: Optional[str] = Field(None, description="Unique definition identifier (NOT NULL in DB)")
    time_stamp: Optional[datetime] = Field(None, description="Timestamp of definition creation/update (NOT NULL in DB)")
    summary_element: Optional[str] = Field(None, description="Summarized element (e.g. rainfall, temperature)")
    summary_type: Optional[str] = Field(None, description="Type of statistical summary")
    definition_value: Optional[Dict[str, Any]] = Field(None, description="JSON object containing definition parameters and thresholds")
    accreditation: Optional[str] = Field(None, description="Authoritative source or accreditation body")

    class Config:
        orm_mode = True


class StationRecord(BaseModel):
    """
    Schema representing a record in the 'station' table.
    Contains geospatial metadata and status for meteorological stations.
    """
    station_id: Optional[str] = Field(None, description="Unique meteorological station identifier (NOT NULL in DB)")
    station_name: Optional[str] = Field(None, description="Human-readable station name")
    latitude: Optional[float] = Field(None, description="Geographic latitude in decimal degrees")
    longitude: Optional[float] = Field(None, description="Geographic longitude in decimal degrees")
    elevation: Optional[float] = Field(None, description="Station elevation above sea level in meters")
    district: Optional[str] = Field(None, description="Administrative district name")
    country_code: Optional[str] = Field(None, description="Country code (e.g. zm, mw, zw)")
    time_stamp: Optional[datetime] = Field(None, description="Timestamp of record creation or update")
    status: Optional[str] = Field(None, description="Operational status of the station")

    class Config:
        orm_mode = True


class SummaryRecord(BaseModel):
    """
    Schema representing a record in the 'summary' table.
    Contains precomputed climate and weather statistics across time dimensions.
    """
    station_id: Optional[str] = Field(None, description="Station identifier (NOT NULL in DB)")
    definition_id: Optional[str] = Field(None, description="Definition identifier (NOT NULL in DB)")
    time_type: Optional[str] = Field(None, description="Time dimension type (e.g. annual, monthly)")
    time_value: Optional[str] = Field(None, description="Time dimension value (e.g. year '2024')")
    summary_type: Optional[str] = Field(None, description="Summary calculation type")
    summary_element: Optional[str] = Field(None, description="Climate element (e.g. rain, temp)")
    summary_name: Optional[str] = Field(None, description="Name of specific summary metric")
    summary_value: Optional[str] = Field(None, description="Calculated summary metric value")
    time_stamp: Optional[datetime] = Field(None, description="Timestamp of calculation (NOT NULL in DB)")
    status: Optional[str] = Field(None, description="Processing status (NOT NULL in DB)")

    class Config:
        orm_mode = True


class SummaryStationMetadataRecord(BaseModel):
    """
    Schema representing a record in the 'summary_station_metadata' table.
    Indexes which summary types and definitions are available for a given station.
    """
    station_id: Optional[str] = Field(None, description="Station identifier (NOT NULL in DB)")
    summary_type: Optional[str] = Field(None, description="Summary type available for this station")
    definition_id: Optional[str] = Field(None, description="Definition identifier")
    time_stamp: Optional[datetime] = Field(None, description="Record timestamp (NOT NULL in DB)")

    class Config:
        orm_mode = True


DatabaseTableName = Literal[
    "crop",
    "definition",
    "station",
    "summary",
    "summary_station_metadata",
]

DATABASE_TABLE_MODELS = {
    "crop": CropRecord,
    "definition": DefinitionRecord,
    "station": StationRecord,
    "summary": SummaryRecord,
    "summary_station_metadata": SummaryStationMetadataRecord,
}
