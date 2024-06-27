from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "zm_workshops"
    station_id: str = "zambia_eastern"
    water_requirements: Optional[list[int]] | None = None#[100, 200, 300]
    planting_length: Optional[list[int]] | None = None#[20]
    planting_dates: Optional[list[int]] | None = None#[25, 50, 75]
    start_before_season: Optional[bool] | None = None
    override: Optional[bool] = False
