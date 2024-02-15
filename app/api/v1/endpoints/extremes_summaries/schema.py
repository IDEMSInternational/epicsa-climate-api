from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code

summary_name_extremes_summaries = Literal[
    "extremes_rain",
    "extremes_tmin",
    "extremes_tmax",
]

class ExtremesSummariesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "test_1"
    summaries: list[summary_name_extremes_summaries] = [
        "extremes_rain",
        "extremes_tmin",
        "extremes_tmax",
    ]



