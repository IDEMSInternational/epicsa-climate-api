from typing import Optional, List
from pydantic import BaseModel

class AnnualRainfallSummariesParameters(BaseModel):
    station_id: str
    summaries: List[str] = None
