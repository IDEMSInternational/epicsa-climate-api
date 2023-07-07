from typing import OrderedDict

from epicsa_python.epicsa import season_start_probabilities
from fastapi import APIRouter, Depends, HTTPException

from app.utils.response import get_dataframe_response

from .schema import (
    SeasonStartProbabilitiesParameters,
)

router = APIRouter()


@router.post("/")
def get_season_start_probabilities(
    params: SeasonStartProbabilitiesParameters,
) -> OrderedDict:
    """
    TODO.
    """
    result: OrderedDict = season_start_probabilities(
        params.country,
        params.station_id,
        params.start_dates,
    )
    # TODO move to shared function
    # `get_dataframe_response()` function cannot cope with categorical data.
    #    So convert categorical columns to strings
    data_frame = result["data"]
    for col in data_frame.columns:
        print(data_frame[col].values)
        if data_frame[col].dtype.name == "category":
            data_frame[col] = data_frame[col].astype(str)

    # ensure that data frame can be serialized
    result["data"] = get_dataframe_response(data_frame)

    return result