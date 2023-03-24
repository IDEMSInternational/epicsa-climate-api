from typing import Literal, List, Optional
from pydantic import BaseModel

summary_name = Literal[
    "seasonal_rainfall",
    "seasonal_raindays",
    "start_rains",
    "end_season",
    "length_season"
    ]

country_name = Literal["zm","mw"]   

class AnnualRainfallSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "01122"
    summaries: Optional[List[summary_name]] = None
