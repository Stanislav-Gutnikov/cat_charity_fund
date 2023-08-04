from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime
from datetime import datetime
from app.core.db import Base


class UniversalClass(Base):
    __abstract__ = True

    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.utcnow)
    close_date = Column(DateTime)


class CharityProject(UniversalClass):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
