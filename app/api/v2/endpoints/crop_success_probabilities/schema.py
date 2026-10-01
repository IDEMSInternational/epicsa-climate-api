from typing import List, Optional
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "mw_test"
    station_id: str = "Kasungu"
    water_requirements: Optional[List[int]] = None
    planting_length: Optional[List[int]] = None
    planting_dates: Optional[List[int]] = None
    start_before_season: Optional[bool] = True
