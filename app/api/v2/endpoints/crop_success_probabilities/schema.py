from pydantic import BaseModel, Field
from app.definitions import country_code


class CropSuccessProbabilitiesParameters(BaseModel):
    country: country_code = Field("mw_test", description="Two-letter country code (e.g. 'zm', 'zw', 'mw')")
    station_id: str = Field("Kasungu", description="Target station identifier")
