from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import Temp

class TemperatureSummariesMetadata(BaseModel):
    mean_tmin: Optional[Temp]
    mean_tmax: Optional[Temp]
    min_tmin: Optional[Temp] 
    min_tmax: Optional[Temp]
    max_tmin: Optional[Temp]
    max_tmax: Optional[Temp]

class AnnualTempartureSummariesdata(BaseModel):
    station: str
    year: int
    mean_tmin: Optional[float] 
    mean_tmax: Optional[float] 
    min_tmin: Optional[float] 
    min_tmax: Optional[float]
    max_tmin: Optional[float]
    max_tmax: Optional[float]

class MonthlyTempartureSummariesdata(AnnualTempartureSummariesdata):
    month : int

class AnnualTemperatureSummariesResponce(BaseModel):
    metadata: TemperatureSummariesMetadata
    data: list[AnnualTempartureSummariesdata]

class MonthlyTemperatureSummariesResponce(BaseModel):
    metadata: TemperatureSummariesMetadata
    data: list[MonthlyTempartureSummariesdata]