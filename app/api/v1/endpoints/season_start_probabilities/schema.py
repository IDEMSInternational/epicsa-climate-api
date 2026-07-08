from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code


class SeasonStartProbabilitiesParameters(BaseModel):
    country: country_code = "zm"
    station_id: str = "CHIPATA MET"
    start_dates: list[int] | None = None
    override: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "country": "zm",
                "station_id": "CHIPATA MET"
            }
        }