from typing import Literal, List, Optional
from pydantic import BaseModel

summary_name = Literal["annual_rain", "start_rains", "end_rains"]

country_name = Literal["zm", "mw"]


class AnnualRainfallSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "01122"
    summaries: Optional[List[summary_name]] = None
