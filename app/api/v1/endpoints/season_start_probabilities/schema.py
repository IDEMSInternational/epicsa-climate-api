from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_code = "zm_workshops"
    station_id: str = "zambia_eastern"
    start_dates: list[int] | None = [200, 220, 250, 270, 300, 320]
    override: Optional[bool] = False
