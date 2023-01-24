from typing import Dict, List, Optional
from pydantic import BaseModel


class StationBase(BaseModel):
    label: Optional[str] = None
    latitude: float
    longitude: float


# Properties to receive on item creation


class StationCreate(StationBase):
    latitude: float
    longitude: float


class StationUpdate(StationBase):
    pass

# Properties shared by models stored in DB


class StationInDBBase(StationBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client


class Station(StationInDBBase):
    pass
