from typing import Literal
from pydantic import BaseModel
from app.definitions import country_name


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    start_dates: list[int] | None = None
