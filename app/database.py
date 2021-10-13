from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from settings import POSTGRESQL_DB

conn_url = '{engine}://{username}:{password}@{host}:5432/{db}'.format(
    **POSTGRESQL_DB)


engine = create_engine(conn_url, pool_size=100, echo=False)

session_factory = sessionmaker(bind=engine)

Session = scoped_session(session_factory)
