from typing import Literal, Optional
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
    country: country_code = "mw_test"
    station_id: str = "Kasungu"
    summaries: list[summary_name_annual_rainfall] = [
        "annual_rain",
        "start_rains",
        "end_rains",
        "end_season",
        "seasonal_rain",
        "seasonal_length",
    ]
    override: Optional[bool] = False

