from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code

summary_name = Literal[
    "mean_tmin", 
    "mean_tmax",
    "min_tmin",
    "min_tmax",
    "max_tmin",
    "max_tmax"]



class AnnualTemperatureSummariesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "1"
    summaries: list[summary_name] = [
        "mean_tmin", 
        "mean_tmax",
        "min_tmin",
        "min_tmax",
        "max_tmin",
        "max_tmax"

    ]


