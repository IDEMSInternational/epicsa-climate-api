from io import BytesIO
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from app.definitions import country_name, Language,language_code
from google.cloud import storage
import os

client = storage.Client.from_service_account_json('service-account.json')

#TODO buckets will need to be configurable from outside the source code
zm__forecast_bucket = "zambia_pdf_forecasts"
mw_forecast_bucket = "malawi_pdf_forecasts"


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()


def get_metadata_from_name(filename: str):
    parts = filename.split("-")
    if len(parts) > 2:
        return {
            "district": parts[0],
            "type" : parts[1],
            "language" : parts[2]
            }
    else:
        return {
            "district": "error",
            "type" : "error",
            "language" : "error"
            } 

def get_forecasts_from_buckets(bucket_name : str):
    pdfs = []
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name.endswith('.pdf'):
            metadata = get_metadata_from_name(blob.name.split(".")[0])
            pdfs.append({
                "id":blob.id,
                "date_modified":blob.updated,
                "language": metadata["language"],
                "filename":blob.name,
                "district" : metadata["district"],
                "type" :metadata["type"]
                })
    return pdfs

def get_file_from_bucket(bucket_name : str, file_name:str):
    bucket = client.bucket(bucket_name) 
    blob = bucket.blob(file_name)
    try:
        return blob.download_as_bytes()
    except Exception as e:
        return None
    
def upload_file_to_bucket(bucket_name : str,file: UploadFile, new_filename: str):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(new_filename)    
    try:
        blob.upload_from_file(file.file, content_type="application/pdf")
        return {"status": "success", "message": f"PDF '{new_filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")
    
def get_file_name(
    language: Language,
    district : str,
    forecast_type : str,
):
    return district + "-" + forecast_type + "-" + language_code.get(language) + ".pdf"


@router.get("/")
def get_forecasts() :    
    forecasts = {
        "mw" : get_forecasts_from_buckets(mw_forecast_bucket), 
        "zm" : get_forecasts_from_buckets(zm__forecast_bucket)
        }
    return {"forecasts": forecasts}   



@router.get("/{country}/{file_name}")
def get_forecasts(*, country: country_name, file_name: str) :
    if country == "mw":
        bucket_name = mw_forecast_bucket
    elif country == "zm":
        bucket_name = zm__forecast_bucket
    else: #This should never be reached. due to how country is passed in
        raise HTTPException(status_code=404, detail=f"Country not found: {country}")
    
    content = get_file_from_bucket(bucket_name, file_name)
    if content == None:
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
    return StreamingResponse(BytesIO(content), 
                            media_type="application/pdf", 
                            headers={"Content-Disposition": f"attachment; filename={file_name}"})


@router.post("/")
def upload_forecast(
    country: country_name,
    language: Language,
    district : str,
    forecast_type : str,
    file: UploadFile = File(...)
) :
    if country == "mw":
        bucket_name = mw_forecast_bucket
    elif country == "zm":
        bucket_name = zm__forecast_bucket
    else: #This should never be reached. due to how country is passed in
        raise HTTPException(status_code=404, detail=f"Country not found: {country}")
    
    return upload_file_to_bucket(bucket_name,file,get_file_name(language,district,forecast_type))
    





   
