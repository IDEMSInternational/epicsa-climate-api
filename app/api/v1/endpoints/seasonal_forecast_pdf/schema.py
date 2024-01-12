from typing import Literal
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class SeasonalForecastPDFParameters(BaseModel):
    country: country_name = "mw"
    district: str = "balaka"