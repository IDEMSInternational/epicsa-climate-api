from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code

summary_name_extremes_summaries = Literal[
    "extremes_rain",
    "extremes_tmin",
    "extremes_tmax",
]

class ExtremesSummariesParameters(BaseModel):
    country: country_code = "mw_test"
    station_id: str = "Kasungu"
    summaries: list[summary_name_extremes_summaries] = [
        "extremes_rain",
        "extremes_tmin",
        "extremes_tmax",
    ]
    override: Optional[bool] = False


