from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "1"
    water_requirements: list[int] | None = [300, 500, 700]
    planting_length: list[int] | None = [120, 180]
    planting_dates: list[int] | None = [92, 122, 153]
    start_before_season: bool | None = True
