from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1.router import v1_router
from app.core.config import Settings


@lru_cache()
def get_settings():
    return Settings()


def get_application():
    settings = get_settings()
    _app = FastAPI(title="E-PICSA Climate API", version="1.6.0", docs_url="/")
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(GZipMiddleware)
    _app.include_router(v1_router, prefix="/v1")

    return _app


app = get_application()
