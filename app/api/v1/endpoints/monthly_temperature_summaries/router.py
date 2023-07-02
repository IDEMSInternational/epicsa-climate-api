from typing import OrderedDict

from epicsa_python.epicsa import monthly_temperature_summaries
from fastapi import APIRouter, Depends, HTTPException

from app.utils.response import get_dataframe_response

from .schema import (
    MonthlyTemperatureSummariesParameters,
)

router = APIRouter()


@router.post("/")
def get_monthly_temperature_summaries(
    params: MonthlyTemperatureSummariesParameters,
) -> OrderedDict:
    """
    TODO.
    """
    # For lists, Fast API does not handle None default parameter values as expected.
    #    So convert empty lists to 'None' values
    if params.summaries == []:
        params.summaries = None

    result: OrderedDict = monthly_temperature_summaries(
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
