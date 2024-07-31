from fastapi import APIRouter, HTTPException
from google.cloud import storage
import os
from app.definitions import country_code

client = storage.Client.from_service_account_json('service-account.json')


bucket_name = "epicsa-documents"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/service-account.json"

router = APIRouter()


@router.get("/{country}")
def get_documents(
    country: country_code,
    prefix='',
    delimiter: str | None = None,
    max_results: int | None = None,
    match_glob: str | None = None
):
    try:
        blobs = client.list_blobs(
            bucket_name,
            prefix=country + '/' + prefix,
            delimiter=delimiter,
            max_results=max_results,
            match_glob=match_glob)

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
            # Exclude directories
            for blob in blobs if not blob.name.endswith('/')
        ]
        response = {
            "files": files_info
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
