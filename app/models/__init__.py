# TODO - temp import setup
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class TestTable(Base):
    __tablename__ = 'TestTable'
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    val = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
