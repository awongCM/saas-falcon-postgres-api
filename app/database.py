from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import POSTGRESQL_DB

from models import (Base)

conn_url = '{engine}://{username}:{password}@{host}:5432/{db}'.format(
    **POSTGRESQL_DB)


engine = create_engine(conn_url, pool_size=100, echo=False)

Base.metadata.create_all(bind=engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
