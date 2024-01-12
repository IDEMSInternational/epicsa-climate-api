from typing import Literal
from pydantic import BaseModel

country_name = Literal["zm", "mw"]


class SeasonalForecastListParameters(BaseModel):
    country: country_name = "mw"