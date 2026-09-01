from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class SelectQueryRequest(BaseModel):
    table_name: Literal[
        "crop",
        "definition",
        "station",
        "summary",
        "summary_station_metadata",
    ]
    columns: list[str] = Field(
        default_factory=list,
        description="Optional list of allowed columns. Empty means all allowed columns.",
    )
    station_id: str = Field(..., min_length=1, max_length=255)
    order_by: str | None = Field(
        default=None,
        description="Optional sort column. Must be allowed for the selected table.",
    )
    order_direction: Literal["asc", "desc"] = "desc"
    max_rows: int = Field(100, ge=1, le=1000)


class SelectQueryResponse(BaseModel):
    columns: list[str]
    row_count: int
    rows: list[dict[str, Any]]
