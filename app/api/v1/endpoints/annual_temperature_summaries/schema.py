from typing import Literal, List, Optional
from pydantic import BaseModel

summary_name = Literal["mean_tmin", "mean_tmax"]

country_name = Literal["zm", "mw"]


class AnnualTemperatureSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    summaries: List[summary_name] | None = None
