from typing import Dict, Optional
from pydantic import BaseModel
from app.definitions import country_code
from app.core.responce_models.definitions_responce_model import AnnualRain, CropsSuccess, EndRains, EndSeason, ExtremesRain, ExtremesTemp, SeasonStartProbabilities, SeasonalRain, Temp, SeasonalLength, SeasonalTotalRainfall, StartRains


class StationDataResponce(BaseModel):
    country_code: country_code
    district: str
    elevation: int
    latitude: float
    longitude: float
    station_id: int
    station_name: str 

class StationDefinitionDataResponce(BaseModel):
    start_rains: Optional[StartRains]
    end_rains: Optional[EndRains]
    end_season : Optional[EndSeason]
    seasonal_length : Optional[SeasonalLength]
    seasonal_total_rainfall: Optional[SeasonalTotalRainfall]
    mean_tmax : Optional[Temp]
    mean_tmin : Optional[Temp]
    max_tmax : Optional[Temp]
    min_tmin : Optional[Temp] 
    annual_rain : Optional[AnnualRain]
    season_start_probabilities : Optional[SeasonStartProbabilities]
    seasonal_rain : Optional[SeasonalRain ]   
    extremes_tmin : Optional[ExtremesTemp]
    extremes_tmax : Optional[ExtremesTemp]
    extremes_rain : Optional[ExtremesRain]
    crops_success : Optional[CropsSuccess]

class StationAndDefintionResponce(StationDataResponce):
    data : StationDefinitionDataResponce

