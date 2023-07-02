from typing import Literal, List, Optional
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_name = "zm"
    station_id: str = "16"
    start_dates: Optional[List[int]] = []
