from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router

from app.core.config import settings

from app.models import create_tables

create_tables()


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0",
                   docs_url="/")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(v1_router, prefix='/v1')

    return _app


app = get_application()
