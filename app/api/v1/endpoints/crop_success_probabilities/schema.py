from typing import Literal, List, Optional
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    water_requirements: List[int] = [100, 300, 800]
    crop_length: List[int] = [100, 150]
    planting_dates: List[int] = [90, 100, 110]
    start_before_season: bool = True
