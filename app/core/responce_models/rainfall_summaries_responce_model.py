from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import AnnualRain, EndRains, EndSeason, SeasonalLength, SeasonalRain, StartRains

class AnnualRainfallSummariesMetadata(BaseModel):
    annual_rain: Optional[AnnualRain]
    start_rains: Optional[StartRains]
    end_rains:Optional[EndRains]
    end_season:Optional[EndSeason]
    seasonal_rain:Optional[SeasonalRain]
    seasonal_length: Optional[SeasonalLength]

class AnnualRainfallSummariesdata(BaseModel):
    station: str
    year: int
    annual_rain: Optional[float] 
    n_rain: Optional[int]
    start_rains_doy: Optional[int] 
    start_rains_date: Optional[str] | object #rpy2 has issue with no recognising null strings
    end_rains_doy: Optional[int] 
    end_rains_date: Optional[str] | object #rpy2 has issue with no recognising null strings
    seasonal_rain:Optional[int] 
    season_length: Optional[float]   
    end_season_doy:Optional[int] 
    end_season_date:Optional[str] | object #rpy2 has issue with no recognising null strings  
     

class AnnualRainfallSummariesResponce(BaseModel):
    metadata: AnnualRainfallSummariesMetadata
    data: list[AnnualRainfallSummariesdata]