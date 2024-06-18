from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional
from app.definitions import  country_code, language_code as lang_code


FormatType = Literal["html","pdf"]

class Forecast(BaseModel):
    country_code
    date: datetime
    filename:str
    type:str
    format: FormatType