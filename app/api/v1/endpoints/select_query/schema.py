from typing import Any

from pydantic import BaseModel, Field


class SelectQueryRequest(BaseModel):
    sql: str = Field(..., description="SQL query to execute. SELECT statements only.")
    params: list[Any] = Field(default_factory=list)
    max_rows: int = Field(1000, ge=1, le=10000)


class SelectQueryResponse(BaseModel):
    columns: list[str]
    row_count: int
    rows: list[dict[str, Any]]
