from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code

summary_name = Literal[
    "mean_tmin", 
    "mean_tmax",
    "min_tmin",
    "min_tmax",
    "max_tmin",
    "max_tmax"
]


class MonthlyTemperatureSummariesParameters(BaseModel):
    country: country_code = "mw_test"
    station_id: str = "Kasungu"
    summaries: list[summary_name] = [
        "mean_tmin", 
        "mean_tmax",
        "min_tmin",
        "min_tmax",
        "max_tmin",
        "max_tmax"
        ]
    override: Optional[bool] = False