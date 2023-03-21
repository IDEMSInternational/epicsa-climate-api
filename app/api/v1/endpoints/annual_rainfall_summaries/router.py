from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from .schema import AnnualRainfallSummariesParameters

# todo
# from app.epicsa_python.main import annual_rainfall_summaries
from epicsa_python.epicsa import annual_rainfall_summaries

from app.utils.response import get_dataframe_response

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(params: AnnualRainfallSummariesParameters):
    """
    TODO.
    """
    df = annual_rainfall_summaries(params.country, params.station_id, params.summaries)
    return get_dataframe_response(df)
