from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base, engine

from app.api.v1.endpoints.station.model import Base as Station_Base

Station_Base.metadata.create_all(bind=engine)


def create_tables():
    Station_Base.metadata.create_all(bind=engine)


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")
