from functools import lru_cache
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

try:
    import psycopg
except ImportError:
    psycopg = None

try:
    from psycopg_pool import PoolTimeout
except ImportError:
    PoolTimeout = None

from app.api.v1.router import v1_router
from app.api.v2.router import v2_router
from app.core.database import close_connection_pool
from app.core.config import Settings
from app.schemas.database import DATABASE_TABLE_MODELS


TAGS_METADATA = [
    {
        "name": "v2: Climate",
        "description": "PostgreSQL-backed high-performance climate statistics and probabilities.",
    },
    {
        "name": "v2: Metadata",
        "description": "Station metadata and statistical definitions from analytical database.",
    },
    {
        "name": "v2: Database",
        "description": "Parameterized SQL queries against the analytical PostgreSQL database.",
    },
    {
        "name": "v2: Documents",
        "description": "PDF and HTML documents streamed from Google Cloud Storage.",
    },
    {
        "name": "v2: Testing",
        "description": "System health and status checks for v2.",
    },
    {
        "name": "v1 (Legacy): Climate",
        "description": "Legacy climate statistics calculated using R epicsawrap and Cloud Storage.",
    },
    {
        "name": "v1 (Legacy): Metadata",
        "description": "Legacy station metadata.",
    },
    {
        "name": "v1 (Legacy): Database",
        "description": "Legacy database select query endpoint.",
    },
    {
        "name": "v1 (Legacy): Documents",
        "description": "PDF and HTML documents streamed from Google Cloud Storage.",
    },
    {
        "name": "v1 (Legacy): Testing",
        "description": "Legacy status health check.",
    },
]

API_DESCRIPTION = """
### E-PICSA Climate API Documentation

* **v2 Endpoints**: High-performance endpoints querying PostgreSQL directly. [View v2 Docs Only](/v2/docs)
* **v1 Endpoints (Legacy)**: Legacy endpoints using R (`epicsawrap`) and Cloud Storage. [View v1 Docs Only](/v1/docs)
"""


@lru_cache()
def get_settings():
    return Settings()


def _inject_database_models(openapi_schema: dict):
    components = openapi_schema.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    for model in DATABASE_TABLE_MODELS.values():
        if model.__name__ not in schemas:
            schemas[model.__name__] = model.schema(
                ref_template="#/components/schemas/{model}"
            )


def _clean_version_tags(schema: dict, prefix: str):
    for path, methods in schema.get("paths", {}).items():
        for method, op in methods.items():
            if isinstance(op, dict) and "tags" in op:
                op["tags"] = [
                    t.replace(prefix, "") if t.startswith(prefix) else t
                    for t in op["tags"]
                ]


def get_application():
    settings = get_settings()
    _app = FastAPI(
        title="E-PICSA Climate API",
        version="2.0.1",
        description=API_DESCRIPTION,
        docs_url="/",
        openapi_tags=TAGS_METADATA,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "list",
        },
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(GZipMiddleware)
    _app.include_router(v1_router, prefix="/v1")
    _app.include_router(v2_router, prefix="/v2")
    _app.add_event_handler("shutdown", close_connection_pool)

    if PoolTimeout is not None:
        @_app.exception_handler(PoolTimeout)
        async def pool_timeout_handler(request: Request, exc: PoolTimeout):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                headers={"Retry-After": "2"},
                content={
                    "error": {
                        "code": "DATABASE_BUSY",
                        "message": "Database connection pool is busy due to high concurrency. Please retry shortly.",
                        "retryable": True,
                    }
                },
            )

    if psycopg is not None:
        @_app.exception_handler(psycopg.Error)
        async def psycopg_error_handler(request: Request, exc: psycopg.Error):
            err_str = str(exc).lower()
            is_timeout = "statement timeout" in err_str or "canceling statement due to statement timeout" in err_str
            status_code = status.HTTP_504_GATEWAY_TIMEOUT if is_timeout else status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": {
                        "code": "QUERY_TIMEOUT" if is_timeout else "DATABASE_ERROR",
                        "message": "Database query timed out." if is_timeout else "Database query failed.",
                        "retryable": is_timeout,
                    }
                },
            )

    logger = logging.getLogger("app.main")

    @_app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return await http_exception_handler(request, exc)
        logger.exception("Unhandled server error processing %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred processing your request.",
                }
            },
        )

    @_app.get("/v2/docs", include_in_schema=False)
    def v2_docs():
        return get_swagger_ui_html(
            openapi_url="/v2/openapi.json",
            title="E-PICSA Climate API (v2) - Swagger UI",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,
                "docExpansion": "list",
            },
        )

    @_app.get("/v1/docs", include_in_schema=False)
    def v1_docs():
        return get_swagger_ui_html(
            openapi_url="/v1/openapi.json",
            title="E-PICSA Climate API (v1 Legacy) - Swagger UI",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,
                "docExpansion": "list",
            },
        )

    @_app.get("/v2/openapi.json", include_in_schema=False)
    def openapi_v2():
        routes_v2 = [r for r in _app.routes if getattr(r, "path", "").startswith("/v2")]
        v2_tags = [
            {"name": t["name"].replace("v2: ", ""), "description": t["description"]}
            for t in TAGS_METADATA
            if t["name"].startswith("v2:")
        ]
        schema = get_openapi(
            title="E-PICSA Climate API (v2)",
            version="2.0.1",
            description="PostgreSQL-backed high-performance climate statistics and metadata endpoints.",
            routes=routes_v2,
            tags=v2_tags,
        )
        _clean_version_tags(schema, prefix="v2: ")
        _inject_database_models(schema)
        return schema

    @_app.get("/v1/openapi.json", include_in_schema=False)
    def openapi_v1():
        routes_v1 = [r for r in _app.routes if getattr(r, "path", "").startswith("/v1")]
        v1_tags = [
            {"name": t["name"].replace("v1 (Legacy): ", ""), "description": t["description"]}
            for t in TAGS_METADATA
            if t["name"].startswith("v1 (Legacy):")
        ]
        schema = get_openapi(
            title="E-PICSA Climate API (v1 - Legacy)",
            version="1.8.0",
            description="Legacy cloud-storage and R computation endpoints.",
            routes=routes_v1,
            tags=v1_tags,
        )
        _clean_version_tags(schema, prefix="v1 (Legacy): ")
        _inject_database_models(schema)
        return schema

    def custom_openapi():
        if _app.openapi_schema:
            return _app.openapi_schema
        openapi_schema = get_openapi(
            title=_app.title,
            version=_app.version,
            description=_app.description,
            routes=_app.routes,
            tags=TAGS_METADATA,
        )
        _inject_database_models(openapi_schema)
        _app.openapi_schema = openapi_schema
        return _app.openapi_schema

    _app.openapi = custom_openapi

    return _app


app = get_application()
