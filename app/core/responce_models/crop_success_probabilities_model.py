from datetime import date
from pydantic import BaseModel
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import CropsSuccess, EndRains, GridRange, StartRains

class CropSuccessProbabilitiesMetadata(BaseModel):
    start_rains: Optional[StartRains]
    end_rains:Optional[EndRains]
    crops_success:Optional[CropsSuccess]

class CropSuccessProbabilitiesdata(BaseModel):
    station: str
    total_rain : int
    plant_day : int
    plant_length : int
    prop_success_with_start : float
    prop_success_no_start : float

class CropSuccessProbabilitiesResponce(BaseModel):
    metadata: CropSuccessProbabilitiesMetadata 
    data: list[CropSuccessProbabilitiesdata]