from typing import OrderedDict

from epicsa_python.epicsa import annual_rainfall_summaries
from fastapi import APIRouter, Depends, HTTPException

from app.utils.response import get_dataframe_response

from .schema import (
    AnnualRainfallSummariesParameters,
)

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
    # TODO move to shared function
    # `get_dataframe_response()` function cannot cope with categorical data.
    #    So convert categorical columns to strings
    data_frame = result["data"]
    for col in data_frame.columns:
        if data_frame[col].dtype.name == "category":
            data_frame[col] = data_frame[col].astype(str)

    # ensure that data frame can be serialized
    result["data"] = get_dataframe_response(data_frame)

    return result
