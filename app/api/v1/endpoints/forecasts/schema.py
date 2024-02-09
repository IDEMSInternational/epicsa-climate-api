from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional
from app.definitions import  country_code, language_code as lang_code

class Forecast(BaseModel):
    country_code
    date_modified:datetime 
    district:Optional[str]=None
    filename:str
    id:str
    language_code:Optional[lang_code] = None
    type:Optional[Literal["downscale_forecast"]] = None