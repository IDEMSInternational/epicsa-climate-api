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
        description='Maximum number of results to return. If more than 1000 results required use multiple queries',
        gt=0,
        # Limit results as greater would involve paginating the queries
        le=1000,
    )
    match_glob: str = Field(
        default='**[^/]' ,
        description='Use expression for advanced pattern matching. To return only files and not folders end with "[^/]"',
    ) 
    

# Subset of fields returned for GCS object. Designed to be consistent with:
# https://cloud.google.com/storage/docs/json_api/v1/objects#resource-representations
class DocumentMetadata(BaseModel):
    name: str
    contentType: str
    size: int
    timeCreated: str
    updated:str
    
    