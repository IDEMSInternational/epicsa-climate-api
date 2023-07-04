from typing import Literal
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    water_requirements: list[int] | None = None
    planting_length: list[int] | None = None
    planting_dates: list[int] | None = None
    start_before_season: bool | None = None
