from pydantic import BaseModel, Field
from app.definitions import country_code

class DocumentsGetParameters(BaseModel):
    country: country_code
    prefix: str = Field(
        default='',
        description='Specify folder path prefixes. Can be used to filter folders timestamped YYYYMMDD, E.g. "202405"',
    )
    max_results: int = Field(
        default=50,
        description='Max 1000',
        gt=0,
        lt=1000,
    )
    match_glob: str = Field(
        default='**[^/]' ,
        description='Use expression for advanced pattern matching. Specify "[^/]" to omit folders',
    ) 
    

# Subset of fields returned for GCS object. Designed to be consistent with:
# https://cloud.google.com/storage/docs/json_api/v1/objects#resource-representations
class DocumentMetadata(BaseModel):
    name: str
    contentType: str
    size: int
    timeCreated: str
    updated:str
    
    