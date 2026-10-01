from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from fastapi.openapi.utils import get_openapi

from app.api.v1.router import v1_router
from app.api.v1.endpoints.select_query.router import close_connection_pool
from app.core.config import Settings
from app.schemas.database import DATABASE_TABLE_MODELS


@lru_cache()
def get_settings():
    return Settings()


def get_application():
    settings = get_settings()
    _app = FastAPI(title="E-PICSA Climate API", version="1.7.2", docs_url="/")
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(GZipMiddleware)
    _app.include_router(v1_router, prefix="/v1")
    _app.add_event_handler("shutdown", close_connection_pool)

    def custom_openapi():
        if _app.openapi_schema:
            return _app.openapi_schema
        openapi_schema = get_openapi(
            title=_app.title,
            version=_app.version,
            description=_app.description,
            routes=_app.routes,
        )
        components = openapi_schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        for model in DATABASE_TABLE_MODELS.values():
            if model.__name__ not in schemas:
                schemas[model.__name__] = model.schema(
                    ref_template="#/components/schemas/{model}"
                )
        _app.openapi_schema = openapi_schema
        return _app.openapi_schema

    _app.openapi = custom_openapi

    return _app


app = get_application()
