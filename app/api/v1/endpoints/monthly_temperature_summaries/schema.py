from typing import Literal, List, Optional
from pydantic import BaseModel

summary_name = Literal["mean_tmin", "mean_tmax"]

country_name = Literal["zm", "mw"]


class MonthlyTemperatureSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    summaries: Optional[List[summary_name]] = ["mean_tmin", "mean_tmax"]
