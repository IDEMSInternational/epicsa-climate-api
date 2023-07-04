from typing import Literal
from pydantic import BaseModel

summary_name = Literal["mean_tmin", "mean_tmax"]

country_name = Literal["zm", "mw"]


class MonthlyTemperatureSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    summaries: list[summary_name] = ["mean_tmin", "mean_tmax"]
