from typing import Literal, List, Optional
from pydantic import BaseModel

summary_name_annual_rainfall = Literal[
    "annual_rain", "start_rains", "end_rains", "seasonal_length", "end_season"
]
summary_name = Literal["mean_tmin", "mean_tmax"]

country_name = Literal["zm", "mw"]


class AnnualRainfallSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "01122"
    summaries: Optional[List[summary_name_annual_rainfall]] = []
