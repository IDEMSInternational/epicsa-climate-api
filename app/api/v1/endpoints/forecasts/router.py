from io import BytesIO
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from google.cloud import storage
from typing import get_args, List
from app.definitions import country_code
from app.utils.model import with_fallback
from .schema import Forecast
import os
import re
from datetime import datetime

client = storage.Client.from_service_account_json('service-account.json')

country_folders = {
    "zm": "zambia",
    "mw": "malawi"
}

folder_descriptions = {
    "forecasts": "Evening weather forecast",
    "reports": "Lunchtime weather report"
}

file_descriptions = {
    "bulletin_morning": "Morning Weather",
    "bulletin_evening": "Evening Weather",
    "forecast": "Forecast for tonight and tomorrow"
}

attachment_folder = "attachments/"
html_folder = "html/"

forecast_bucket = "zambia_pdf_forecasts"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()


def get_file_from_bucket(file_name:str):
    bucket = client.bucket(forecast_bucket) 
    blob = bucket.blob(file_name)
    try:
        return blob.download_as_bytes()
    except Exception as e:
        return None
  
def extract_date_from_path(file_path):
    match = re.search(r'(\d{4}_\d{2}_\d{2})', file_path)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y_%m_%d')
    else:
        return None

def get_file_description_from_name(file_path):
    file_name_with_extension = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name_with_extension)
    return file_descriptions.get(file_name, None)

def list_folders(prefix):
    blobs = client.list_blobs(forecast_bucket, prefix=prefix)
    directories = set()
    for blob in blobs:
        name_without_prefix = blob.name.removeprefix(prefix)
        if not name_without_prefix :
            continue
        parts = name_without_prefix.split('/')
        for i in range(1, len(parts)):
            directories.add('/'.join(parts[:i]))
    return directories
    
def get_latest_files_in_folder(prefix):
    blobs = client.list_blobs(forecast_bucket, prefix=prefix)
    files_with_dates = []
    date_pattern = re.compile(r'(\d{4}_\d{2}_\d{2})')
    for blob in blobs:
        match = date_pattern.search(blob.name)
        if match:
            date_str = match.group(1)
            date_obj = datetime.strptime(date_str, '%Y_%m_%d')
            files_with_dates.append((blob.name, date_obj))
    
    if not files_with_dates:
        return None

    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    most_recent_date = files_with_dates[0][1]
    most_recent_files = [file for file, date in files_with_dates if date == most_recent_date]    
    return most_recent_files
    
def get_latest_attachments_from_bucket(country: country_code):
    pdfFiles: List[Forecast] = []
    files = get_latest_files_in_folder(attachment_folder + getFolderForCountry(country))

    if files == None:
        return pdfFiles
    for file in files:
        forecast=Forecast(
            country_code= country,
            date= extract_date_from_path(file),
            filename=file,
            type=get_file_description_from_name(file),
            format="pdf"              
        )
        pdfFiles.append(forecast)

    return pdfFiles
    

def get_latest_html_from_bucket(country: country_code):
    htmlFiles: List[Forecast] = []
    folders = list_folders(html_folder+ getFolderForCountry(country) )
    for directory in sorted(folders):
        files = get_latest_files_in_folder(html_folder + getFolderForCountry(country) + directory)
        for file in files:
            forecast=Forecast(
            country_code= country,
            date= extract_date_from_path(file),
            filename=file,
            type=folder_descriptions.get(directory, directory),
            format="html"              
        )
        htmlFiles.append(forecast)
    return htmlFiles


def getFolderForCountry(country_code):
    return country_folders[country_code] + "/"

@router.get("/{country_code}",response_model=List[Forecast])
def list_forecasts(*,country_code:country_code) :
    """
    Get latest forecasts for country
    """
    attachmentFiles = get_latest_attachments_from_bucket(country_code)
    htmlFiles = get_latest_html_from_bucket(country_code)
    return attachmentFiles + htmlFiles



@router.get("/{file_name:path}")
def get_forecast(*, file_name: str) :
    """
    Get forecast file
    """
    content = get_file_from_bucket(file_name)
    if content == None:
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
    if file_name.lower().endswith('.html'):
        return StreamingResponse(BytesIO(content), 
                            media_type="application/html", 
                            headers={"Content-Disposition": f"attachment; filename={file_name}"})
    else: # assume pdf if not html
        return StreamingResponse(BytesIO(content), 
                            media_type="application/pdf", 
                            headers={"Content-Disposition": f"attachment; filename={file_name}"})

    
   




   
