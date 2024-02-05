from typing import Literal
from pydantic import BaseModel
from app.definitions import country_name

summary_name_extremes_summaries = Literal[
    "extremes_rain",
    "extremes_tmin",
    "extremes_tmax",
]

class ExtremesSummariesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "test_1"
    summaries: list[summary_name_extremes_summaries] = [
        "extremes_rain",
        "extremes_tmin",
        "extremes_tmax",
    ]



