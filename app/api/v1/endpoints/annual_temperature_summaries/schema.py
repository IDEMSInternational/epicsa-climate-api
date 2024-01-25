from typing import Literal
from pydantic import BaseModel
from app.definitions import country_name

summary_name = Literal["mean_tmin", "mean_tmax"]



class AnnualTemperatureSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    summaries: list[summary_name] = [
        "mean_tmin", 
        "mean_tmax"
    ]
