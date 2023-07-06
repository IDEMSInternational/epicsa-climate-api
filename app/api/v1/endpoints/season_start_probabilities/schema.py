from typing import Literal
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    start_dates: list[int] | None = None
