from typing import Literal, Optional
from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "internal_tests"
    station_id: str = "Tamale"
