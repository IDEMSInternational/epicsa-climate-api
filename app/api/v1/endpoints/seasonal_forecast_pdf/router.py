from typing import OrderedDict
from fastapi import APIRouter, HTTPException
from app.core.webScrape.webscraper import scrape_webpage, mw_seasonal_forecast_list_url

from .schema import (
    SeasonalForecastPDFParameters,
)

router = APIRouter()


@router.post("/")
async def get_seasonal_forecast_list(
    params: SeasonalForecastPDFParameters,
)-> OrderedDict:
    if params.country == "mw":        
        district_links = scrape_webpage(mw_seasonal_forecast_list_url)
        # Check if link_text exists in the dictionary
        if params.district in district_links:
            return {"pdf_url": district_links[params.district ]}
        else:
            raise HTTPException(status_code=404, detail=f"PDF link not found for '{params.district}'")
    else:
        raise HTTPException(status_code=404, detail=f"Seasonal Forecasts not set up '{params.country}'")
  