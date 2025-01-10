from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from json import dumps
from google.cloud import storage
from google.api_core.page_iterator import HTTPIterator
import os
from .schema import DocumentsGetParameters, DocumentMetadata

client = storage.Client.from_service_account_json('service-account.json')


bucket_name = "epicsa-documents"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()


@router.get("/{country}")
def get_documents(
    params:Annotated[DocumentsGetParameters, Query()]
) -> list[DocumentMetadata] :
    try:
        # Retrieve list of availble blobs. Adapted from:
        # https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.bucket.Bucket#google_cloud_storage_bucket_Bucket_list_blobs
        # NOTE - this is not currently paginated so will only return max 1000 items
        blobs_iterator:HTTPIterator = client.list_blobs(
            bucket_name,
            prefix=f"{params.country}/{params.prefix}",
            max_results=params.max_results,
            match_glob=params.match_glob)

        entries = []
        blob: storage.Blob
        for blob in blobs_iterator:
            # gcs returns blobs as class. Extract fields used in response and append to return entries
            entry = DocumentMetadata(
                name= blob.name,
                contentType= blob.content_type,
                size= blob.size,
                timeCreated= blob.time_created.isoformat(),
                updated= blob.updated.isoformat()
            )
            entries.append(entry)           
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
