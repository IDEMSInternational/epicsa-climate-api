from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import CropsSuccess, EndRains, StartRains

class CropSuccessProbabilitiesMetadata(BaseModel):
    start_rains: Optional[StartRains]
    end_rains:Optional[EndRains]
    crops_success:Optional[CropsSuccess]

class CropSuccessProbabilitiesdata(BaseModel):
    station: str
    water_requirements : int
    planting_dates : int
    planting_length : int
    prop_success : float

class CropSuccessProbabilitiesResponce(BaseModel):
    metadata: CropSuccessProbabilitiesMetadata
    data: list[CropSuccessProbabilitiesdata]