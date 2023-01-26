from typing import Optional
from pydantic import BaseModel


class Station(BaseModel):
    id: int
    label: Optional[str] = None
    latitude: float
    longitude: float
