from typing import Any, List, OrderedDict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from .schema import AnnualRainfallSummariesParameters

# todo
# from app.epicsa_python.main import annual_rainfall_summaries
from epicsa_python.epicsa import annual_rainfall_summaries

from app.utils.response import get_dataframe_response

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(params: AnnualRainfallSummariesParameters) -> OrderedDict:
    """
    TODO.
    """
    result_json = annual_rainfall_summaries(
        params.country, params.station_id, params.summaries
    )
    print("result_json ", result_json)
    result_json["data"] = get_dataframe_response(result_json["data"])
    return result_json
