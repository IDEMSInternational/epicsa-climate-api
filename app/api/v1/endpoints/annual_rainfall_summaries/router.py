from typing import OrderedDict

from epicsa_python.epicsa import annual_rainfall_summaries
from fastapi import APIRouter, Depends, HTTPException

from app.utils.response import get_dataframe_response

from .schema import AnnualRainfallSummariesParameters

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(
    params: AnnualRainfallSummariesParameters,
) -> OrderedDict:
    """
    TODO.
    """
    result: OrderedDict = annual_rainfall_summaries(
        params.country, params.station_id, params.summaries
    )
    # ensure that data frame can be serialized
    result["data"] = get_dataframe_response(result["data"])

    return result
