from typing import Dict, List, Optional
from pydantic import BaseModel
from app.definitions import country_code
from app.core.responce_models.definitions_responce_model import AnnualRain, CropsSuccess, EndRains, EndSeason, SeasonStartProbabilities, SeasonalRain, Temp, SeasonalLength, SeasonalTotalRainfall, StartRains


class StationDataResponce(BaseModel):
    station_id: str
    station_name: str 
    latitude: float
    longitude: float
    elevation: float
    district: str
    country_code: country_code      

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
    definitions_id: list[str]
    climsoft_list: Optional[list[Optional[str]]]
    data : StationDefinitionDataResponce

class StationListResponce(BaseModel):
    data : List[StationDataResponce]
