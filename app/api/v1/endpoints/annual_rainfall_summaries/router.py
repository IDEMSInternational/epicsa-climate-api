from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from .schema import AnnualRainfallSummariesParameters
from app.epicsa_python.main import annual_rainfall_summaries

from app.utils.response import get_dataframe_response

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters
):
    """
    TODO.
    """
    df = annual_rainfall_summaries(params.station_id, params.summaries)
    return get_dataframe_response(df)
