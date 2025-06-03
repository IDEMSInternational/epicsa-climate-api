from datetime import date
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnnualRain(BaseModel):
    annual_rain: Optional[bool]
    n_rain : Optional[bool]
    rain_day : Optional[int]
    na_rm : Optional[bool]
    na_n : Optional[int]
    na_n_non : Optional[int]
    na_consec : Optional[int]
    na_prop : Optional[float]
    s_start_doy : Optional[float] 

class StartRains(BaseModel):
    start_day: Optional[int]
    end_day: Optional[int]
    threshold: Optional[int]  
    total_rainfall: Optional[bool]
    over_days: Optional[int]
    amount_rain: Optional[int]    
    proportion: Optional[bool]
    prob_rain_day: Optional[float]
    dry_spell: Optional[bool]
    spell_max_dry_days: Optional[int]
    spell_interval: Optional[int]
    dry_period: Optional[bool]
    max_rain: Optional[int]
    period_interval: Optional[int]
    period_max_dry_days: Optional[int]
    s_start_doy: Optional[int]
    number_rain_days: Optional[bool]
    min_rain_days: Optional[int]
    rain_day_interval: Optional[int]

class EndRains(BaseModel):
    start_day: Optional[int]
    end_day: Optional[int]
    output: Optional[str]
    min_rainfall: Optional[int]
    interval_length: Optional[int]    
    s_start_doy: Optional[int]
    
class EndSeason(BaseModel):
    start_day: Optional[int]
    end_day: Optional[int]
    water_balance_max: Optional[int]
    capacity: Optional[int]    
    evaporation: Optional[str]
    evaporation_value: Optional[int]
    s_start_doy: Optional[int]
   
class SeasonalRain(BaseModel):
    total_rain: Optional[int] | Optional[bool]    
    n_rain: Optional[bool]
    rain_day: Optional[float]
    na_rm: Optional[bool]
    na_n: Optional[int]
    na_n_non: Optional[int]
    na_consec: Optional[int]
    na_prop: Optional[float]  

class SeasonalLength(BaseModel):
    end_type : Optional[str]

class SeasonalTotalRainfall(BaseModel):
    na_prop: Optional[float]

class Temp(BaseModel):
    to: Optional[str] | Optional[List[str]]
    na_rm : Optional[bool]
    na_n: Optional[int]
    na_n_non : Optional[int]
    na_consec : Optional[int]
    na_prop: Optional[float]
    s_start_doy: Optional[int]

class GridRange(BaseModel):
    from_: Optional[int] = Field(alias="from")
    to : Optional[int]
    by : Optional[int]

class CropsSuccess(BaseModel):
    water_requirements : Optional[str|Dict[str,int]]
    planting_dates: Optional[str|Dict[str,int]]
    planting_length: Optional[str|Dict[str,int]]

class SeasonStartProbabilities(BaseModel):
    specified_day: Optional[list[int]|Dict[str,int]]