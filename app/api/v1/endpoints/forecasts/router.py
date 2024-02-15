from io import BytesIO
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse,FileResponse
from google.cloud import storage
from typing import get_args, List
from app.definitions import country_code
from app.utils.model import with_fallback
from .schema import Forecast, ForecastType
import os

client = storage.Client.from_service_account_json('service-account.json')

#TODO buckets will need to be configurable from outside the source code
forecast_buckets = {
    "zm": "zambia_pdf_forecasts",
    "mw": "malawi_pdf_forecasts"
}


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()


def get_metadata_from_name(filename: str):
    parts = filename.split("-")
    if len(parts) > 2:
        return {
            "district": parts[0],
            "type" : with_fallback(parts[1],ForecastType,None),
            "language" : parts[2]
            }
    else:
        return {
            "district": None,
            "type" : None,
            "language" : None
            } 

def get_forecasts_from_buckets(bucket_name : str):
    pdfs:   List[Forecast] = []
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name.endswith('.pdf'):
            metadata = get_metadata_from_name(blob.name.split(".")[0])
            forecast=Forecast(
                id=blob.id,
                date_modified=blob.updated,
                language= metadata["language"],
                filename=blob.name,
                district = metadata["district"],
                type =metadata["type"]
            )
            pdfs.append(forecast)
    return pdfs

def get_file_from_bucket(bucket_name : str, file_name:str):
    bucket = client.bucket(bucket_name) 
    blob = bucket.blob(file_name)
    try:
        return blob.download_as_bytes()
    except Exception as e:
        return None

@router.get("/", response_model=List[str])
def list_endpoints(request:Request) :   
    """
    List available forecast endpoints
    """
    codes = get_args(country_code)
    endpoints = [
        str(request.url) +   code
        for code in codes
    ]
    return endpoints

@router.get("/{country_code}",response_model=List[Forecast])
def list_forecasts(*,country_code:country_code) :
    """
    Get available forecasts for country
    """
    bucket = forecast_buckets[country_code] 
    if bucket:
        return  get_forecasts_from_buckets(bucket)
    else:
        raise HTTPException(status_code==404,  detail=f"Country not found: {country_code}")




@router.get("/{country_code}/{file_name}")
def get_forecast(*, country_code: country_code, file_name: str) :
    """
    Get forecast file
    """
    bucket = forecast_buckets[country_code] 
    if bucket:
        content = get_file_from_bucket(bucket, file_name)
        if content == None:
            raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
        return StreamingResponse(BytesIO(content), 
                                media_type="application/pdf", 
                                headers={"Content-Disposition": f"attachment; filename={file_name}"})
    else: #This should never be reached. due to how country is passed in
        raise HTTPException(status_code=404, detail=f"Country not found: {country_code}")
    
   




   
