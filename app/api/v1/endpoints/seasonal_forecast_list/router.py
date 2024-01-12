from typing import OrderedDict
from fastapi import APIRouter, HTTPException
from app.core.webScrape.webscraper import scrape_webpage, mw_seasonal_forecast_list_url

from .schema import (
    SeasonalForecastListParameters,
)

router = APIRouter()


@router.post("/")
def get_seasonal_forecast_list(
    params: SeasonalForecastListParameters,
) -> OrderedDict:
        
    if params.country == "mw":
        districts = scrape_webpage(mw_seasonal_forecast_list_url)
        return {"districts": districts}   
    else:
        raise HTTPException(status_code=404, detail=f"Seasonal Forecasts not set up '{params.country}'")




