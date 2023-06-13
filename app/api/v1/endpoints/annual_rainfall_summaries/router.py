from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from .schema import AnnualRainfallSummariesParameters

# todo
# from app.epicsa_python.main import annual_rainfall_summaries
from epicsa_python.epicsa import annual_rainfall_summaries

from app.utils.response import get_dataframe_response

router = APIRouter()


@router.post("/")
def get_annual_rainfall_summaries(params: AnnualRainfallSummariesParameters) -> JSONResponse:
    """
    TODO.
    """
    result_json = annual_rainfall_summaries(params.country, params.station_id, params.summaries)
    print("result_json ", result_json)
    #return result_json
    return JSONResponse(content=result_json)
