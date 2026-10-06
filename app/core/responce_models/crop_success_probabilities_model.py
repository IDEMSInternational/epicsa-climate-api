from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.responce_models.definitions_responce_model import CropsSuccess, EndRains, GridRange, StartRains

class CropSuccessProbabilitiesMetadata(BaseModel):
    start_rains: Optional[StartRains]
    end_rains: Optional[EndRains]
    crops_success: Optional[CropsSuccess]

class CropSuccessProbabilitiesdata(BaseModel):
    station: str = Field(..., description="Station identifier")
    total_rain: int = Field(..., description="Crop water requirement threshold in mm (e.g. 200 to 1200 mm)")
    plant_day: int = Field(..., description="Planting day relative to season start July 1 (e.g. 123=31-Oct, 138=15-Nov, 153=30-Nov, 168=15-Dec, 183=30-Dec)")
    plant_length: int = Field(..., description="Crop growth cycle / duration in days (e.g. 60 to 150 days)")
    prop_success_with_start: float = Field(..., description="Probability of crop success (0.0-1.0) when planting only after rainy season start criteria are satisfied")
    prop_success_no_start: float = Field(..., description="Probability of crop success (0.0-1.0) when planting on the calendar day regardless of rainy season start condition")

class CropSuccessProbabilitiesResponce(BaseModel):
    generation_id: Optional[str] = None
    generation_timestamp: Optional[datetime] = None
    metadata: CropSuccessProbabilitiesMetadata 
    data: list[CropSuccessProbabilitiesdata]