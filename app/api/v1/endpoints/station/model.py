from sqlalchemy import Column,  Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
