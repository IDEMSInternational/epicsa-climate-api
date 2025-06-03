from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from google.cloud import storage
from google.api_core.page_iterator import HTTPIterator
from io import BytesIO
import os
from .schema import DocumentsGetParameters, DocumentMetadata
from app.definitions import country_code

client = storage.Client.from_service_account_json('service-account.json')


bucket_name = "epicsa-documents"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter() 

@router.get("/{country}", response_model=list[DocumentMetadata])
def get_documents(
    country: country_code,
    params:DocumentsGetParameters = Depends()
) -> list[DocumentMetadata] :
    try:
        # Retrieve list of availble blobs. Adapted from:
        # https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.bucket.Bucket#google_cloud_storage_bucket_Bucket_list_blobs
        # NOTE - this is not currently paginated so will only return max 1000 items
        blobs_iterator:HTTPIterator = client.list_blobs(
            bucket_name,
            prefix=f"{country}/{params.prefix}",
            max_results=params.max_results,
            match_glob=params.match_glob)

        entries = []
        blob: storage.Blob
        for blob in blobs_iterator:
            # gcs returns blobs as class. Extract fields used in response and append to return entries
            entry = DocumentMetadata(
                name= blob.name.replace(f"{country}/","",1),
                contentType= blob.content_type,
                size= blob.size,
                timeCreated= blob.time_created.isoformat(),
                updated= blob.updated.isoformat(),
                metadata=blob.metadata
            )
            entries.append(entry)           
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_file_from_bucket(filename:str):
    bucket = client.bucket(bucket_name) 
    blob = bucket.blob(filename)
    try:
        return blob.download_as_bytes()
    except Exception as e:
        return None     
    
# NOTE - as filenames include nested `/` paths use a catch-all for all child routes
@router.get("/{country}/{filepath:path}")
def download_document(
    country: country_code,
    filepath: str
) -> list[DocumentMetadata] :
    """
    Download a specific document
    """
    content = get_file_from_bucket(f"{country}/{filepath}")
    if content == None:
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    if filepath.lower().endswith('.html'):
        return StreamingResponse(BytesIO(content), 
                            media_type="application/html", 
                            headers={"Content-Disposition": f"attachment; filepath={filepath}"})
    else: # assume pdf if not html
        return StreamingResponse(BytesIO(content), 
                            media_type="application/pdf", 
                            headers={"Content-Disposition": f"attachment; filepath={filepath}"})
