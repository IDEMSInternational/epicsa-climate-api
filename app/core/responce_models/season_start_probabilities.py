from datetime import date
from pydantic import BaseModel, confloat, conint
from typing import Dict, List, Optional, Union

from app.core.responce_models.definitions_responce_model import SeasonStartProbabilities, StartRains

class SeasonStartProbabilitiesMetadata(BaseModel):
    start_rains: Optional[StartRains]
    season_start_probabilities:Optional[SeasonStartProbabilities]

class SeasonStartProbabilitiesdata(BaseModel):
    station: str
    day: int
    proportion : float

class SeasonStartProbabilitiesResponce(BaseModel):
    metadata: SeasonStartProbabilitiesMetadata
    data: List[SeasonStartProbabilitiesdata]


