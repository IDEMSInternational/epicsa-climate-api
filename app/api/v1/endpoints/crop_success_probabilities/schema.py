from typing import Literal, List, Optional
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    water_requirements: List[int] | None = None
    planting_length: List[int] | None = None
    planting_dates: List[int] | None = None
    start_before_season: bool | None = None
