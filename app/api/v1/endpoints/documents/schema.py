from pydantic import BaseModel


class documentParamaters(BaseModel):
    prefix: str = ""
    delimiter: str = ""
    maxResults: int = 0