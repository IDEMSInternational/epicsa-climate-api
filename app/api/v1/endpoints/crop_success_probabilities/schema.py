from typing import Literal
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "1"
    water_requirements: list[int] | None = [100, 200, 300]
    planting_length: list[int] | None = [20]
    planting_dates: list[int] | None = [25, 50, 75]
    start_before_season: bool | None = True
