from typing import Dict
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
    start_rains: StartRains
    end_rains: EndRains
    end_season : EndSeason
    seasonal_length : SeasonalLength
    seasonal_total_rainfall: SeasonalTotalRainfall
    mean_tmax : Temp
    mean_tmin : Temp
    max_tmax : Temp
    min_tmin : Temp    
    annual_rain : AnnualRain
    season_start_probabilities : SeasonStartProbabilities
    seasonal_rain : SeasonalRain    
    extremes_tmin : ExtremesTemp
    extremes_tmax : ExtremesTemp
    extremes_rain : ExtremesRain
    crops_success : CropsSuccess

class StationAndDefintionResponce(StationDataResponce):
    data : StationDefinitionDataResponce

