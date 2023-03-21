from typing import Optional, List
from pydantic import BaseModel

class AnnualRainfallSummariesParameters(BaseModel):
    country: str
    station_id: str
    summaries: List[str] = None
