from typing import List, Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code

summary_name = Literal[
    "monthly_rain",
    "total_rain",
]


class MonthlyRainfallSummariesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "MAGOYE AGROMET"
    summaries: Optional[List[summary_name]] = [
        "monthly_rain",
    ]
    override: Optional[bool] = False
