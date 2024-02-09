from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "16"
    start_dates: list[int] | None = None
