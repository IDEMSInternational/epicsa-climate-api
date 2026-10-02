from pydantic import BaseModel
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = "mw_test"
    station_id: str = "Kasungu"
