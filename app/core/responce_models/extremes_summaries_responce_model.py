from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import ExtremesRain, ExtremesTemp

class ExtremesSummariesMetadata(BaseModel):
    extremes_rain: Optional[ExtremesRain]
    extremes_tmin : Optional[ExtremesTemp]
    extremes_tmax : Optional[ExtremesTemp]

class ExtremesSummariesdata(BaseModel):
    station: str
    date: float #should be date
    year: int
    month : int
    doy: int
    day: int
    tmax: float
    tmin: float
    rain: float


class ExtremesSummariesResponce(BaseModel):
    metadata: ExtremesSummariesMetadata
    data: list[ExtremesSummariesdata]
