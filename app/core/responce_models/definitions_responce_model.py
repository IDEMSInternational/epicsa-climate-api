from datetime import date
from pydantic import BaseModel
from typing import Dict, List, Optional

class AnnualRain(BaseModel):
    annual_rain: Optional[bool]
    n_rain : Optional[bool]
    na_rm : Optional[bool]
    na_prop : Optional[float]
    na_n : Optional[int]
    na_consec : Optional[int]
    na_n_non : Optional[int]

class StartRains(BaseModel):
    threshold: Optional[int]
    start_day: Optional[int]
    end_day: Optional[int]
    total_rainfall: Optional[bool]
    amount_rain: Optional[int]
    over_days: Optional[int]
    proportion: Optional[bool]
    prob_rain_day: Optional[float]
    number_rain_days: Optional[bool]
    min_rain_days: Optional[int]
    rain_day_interval: Optional[int]
    dry_spell: Optional[bool]
    spell_max_dry_days: Optional[int]
    spell_interval: Optional[int]
    dry_period: Optional[bool]
    period_interval: Optional[int]
    max_rain: Optional[int]
    period_max_dry_days: Optional[int]
    _last_updated: Optional[date]

class EndRains(BaseModel):
  #  s_start_doy: Optional[int]
    start_day: Optional[int]
    end_day: Optional[int]
    interval_length: Optional[int]
    min_rainfall: Optional[int]
    
class EndSeason(BaseModel):
  #  s_start_doy : Optional[int]
    start_day: Optional[int]
    end_day: Optional[int]
    capacity: Optional[int]
    water_balance_max: Optional[int]
    evaporation: Optional[str]
    evaporation_value: Optional[int]
   
class SeasonalRain(BaseModel):
  #  seasonal_rain: Optional[bool]
    total_rain: Optional[int] | Optional[bool]
    end_type: Optional[str]
    n_rain: Optional[bool]
    rain_day: Optional[float]
    na_rm: Optional[bool]
    na_prop: Optional[float]
    na_n: Optional[int]
    na_consec: Optional[int]
    na_n_non: Optional[int]

class SeasonalLength(BaseModel):
    end_type : Optional[str]

class SeasonalTotalRainfall(BaseModel):
    na_prop: Optional[float]

class Temp(BaseModel):
    to: Optional[str]
    na_rm : Optional[bool]

class ExtremesRain(BaseModel):
    type: Optional[str]
    value : Optional[int]

class ExtremesTemp(BaseModel):   
    direction: Optional[str]
    type: Optional[str]
    value: Optional[int]

class CropsSuccess(BaseModel):
    water_requirements : Optional[Dict[str, int]] #val1, val2, valx
    planting_dates: Optional[Dict[str, int]] #val1, val2, valx
    planting_length: Optional[Dict[str, int]] #val1, val2, valx
    start_check: Optional[bool]

class SeasonStartProbabilities(BaseModel):
    specified_day: Optional[Dict[str, int]]