from pydantic import BaseModel
from app.definitions import country_code

class Station(BaseModel):
    country_code: country_code
    district: str
    elevation: int
    latitude: float
    longitude: float
    station_id: int
    station_name: str
    
# TODO - define more cleanly (or generate from R?)
# This should then either be merged with station or a 'definition' child property
class StationDefinition(BaseModel):
    annual_rain:str