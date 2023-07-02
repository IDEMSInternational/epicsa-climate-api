from typing import OrderedDict

from epicsa_python.epicsa import crop_success_probabilities
from fastapi import APIRouter, Depends, HTTPException

from app.utils.response import get_dataframe_response

from .schema import (
    CropSuccessProbabilitiesParameters,
)

router = APIRouter()


@router.post("/")
def get_crop_success_probabilities(
    params: CropSuccessProbabilitiesParameters,
) -> OrderedDict:
    """
    TODO.
    """
    # For lists, Fast API does not handle None default parameter values as expected.
    #    So convert empty lists to 'None' values
    if params.water_requirements == []:
        params.water_requirements = None
    if params.planting_length == []:
        params.planting_length = None
    if params.planting_dates == []:
        params.planting_dates = None

    result: OrderedDict = crop_success_probabilities(
        params.country,
        params.station_id,
        params.water_requirements,
        params.planting_length,
        params.planting_dates,
        params.start_before_season,
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
