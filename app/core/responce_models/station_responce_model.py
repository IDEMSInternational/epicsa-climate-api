from typing import List, Optional
from pydantic import BaseModel, validator
from app.definitions import country_code
from app.core.responce_models.definitions_responce_model import AnnualRain, CropsSuccess, EndRains, EndSeason, SeasonStartProbabilities, SeasonalRain, Temp, SeasonalLength, SeasonalTotalRainfall, StartRains

def _is_missing(v) -> bool:
    """Helper: check if a value is None, empty dict, or NA_character_ string."""
    return v is None or v == {} or (isinstance(v, str) and v.strip() == "NA_character_")

class StationDataResponce(BaseModel):
    station_id: str
    station_name: str 
    latitude: Optional[float]
    longitude: Optional[float]
    elevation: Optional[float]
    district: Optional[str]
    country_code: country_code
    
    @validator("station_name", pre=True, always=True)
    def normalize_station_name(cls, v, values):
        # If missing, fall back to station_id
        if _is_missing(v):
            return values.get("station_id")
        return str(v)

    @validator("district", pre=True, always=True)
    def normalize_district(cls, v):
        # Missing => None
        if _is_missing(v):
            return None
        return str(v)

class StationDefinitionDataResponce(BaseModel):
    start_rains: Optional[StartRains]
    end_rains: Optional[EndRains]
    end_season : Optional[EndSeason]
    seasonal_length : Optional[SeasonalLength]
    annual_rain : Optional[AnnualRain]
    seasonal_rain : Optional[SeasonalRain]   
    min_tmin : Optional[Temp] 
    max_tmin : Optional[Temp]
    mean_tmin : Optional[Temp]
    min_tmax : Optional[Temp]
    max_tmax : Optional[Temp]
    mean_tmax : Optional[Temp]
    crops_success : Optional[CropsSuccess]
    season_start_probabilities : Optional[SeasonStartProbabilities]
    seasonal_total_rainfall: Optional[SeasonalTotalRainfall]
    

class StationAndDefintionResponce(StationDataResponce):
    definitions_id: list[str|object]
    climsoft_list: Optional[list[Optional[str]]]
    data : StationDefinitionDataResponce

class StationListResponce(BaseModel):
    data : List[StationDataResponce]
