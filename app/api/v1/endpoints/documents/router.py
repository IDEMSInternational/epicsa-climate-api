from fastapi import APIRouter, HTTPException
from google.cloud import storage
from .schema import  documentParamaters
import os

client = storage.Client.from_service_account_json('service-account.json')


bucket_name = "zambia_pdf_forecasts"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()

@router.post("/")
def get_documents(params: documentParamaters):
    try:
        if params.maxResults > 0:
            blobs = client.list_blobs(
                bucket_name, 
                prefix=params.prefix, 
                delimiter=params.delimiter,
                max_results=params.maxResults)
        else:
            blobs = client.list_blobs(
                bucket_name, 
                prefix=params.prefix, 
                delimiter=params.delimiter)


        files_info = [
            {
                "name": blob.name,
                "selfLink": blob.self_link,      
                "mediaLink": blob.media_link,
                "contentType": blob.content_type,
                "size": blob.size,
                "time_created": blob.time_created.isoformat(),
                "updated": blob.updated.isoformat()
            }
            for blob in blobs if not blob.name.endswith('/')  # Exclude directories
        ]
        response = {
            "files": files_info
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





   
