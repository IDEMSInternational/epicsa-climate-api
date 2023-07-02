from typing import Literal, List, Optional
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    water_requirements: Optional[List[int]] = []
    planting_length: Optional[List[int]] = []
    planting_dates: Optional[List[int]] = []
    start_before_season: Optional[bool] = None
