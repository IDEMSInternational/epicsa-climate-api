from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "16"
    water_requirements: list[int] | None = None
    planting_length: list[int] | None = None
    planting_dates: list[int] | None = None
    start_before_season: bool | None = None
