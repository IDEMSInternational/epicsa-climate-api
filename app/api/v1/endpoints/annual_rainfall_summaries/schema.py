from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code

summary_name_annual_rainfall = Literal[
    "annual_rain",
    "start_rains",
    "end_rains",
    "end_season",
    "seasonal_rain",
    "seasonal_length",
]


class AnnualRainfallSummariesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "test_1"
    summaries: list[summary_name_annual_rainfall] = [
        "annual_rain",
        "start_rains",
        "end_rains",
        "end_season",
        "seasonal_rain",
        "seasonal_length",
    ]

