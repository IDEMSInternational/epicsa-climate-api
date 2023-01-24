from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def get_session() -> Session:
    """
    Api dependency to provide database session to a request
    """

    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
