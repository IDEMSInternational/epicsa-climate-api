
from typing import Union

from pydantic import AnyHttpUrl, BaseSettings,  validator


class Settings(BaseSettings):
    EPICSA_DATA_AUTH_TOKEN: str = ''
    # Allow cross-origin requests from development applications running on port 4200 (e-picsa angular apps)
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:4200"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"
