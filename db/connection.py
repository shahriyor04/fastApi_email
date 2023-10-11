# postgres database connection

from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:1@127.0.0.1:5432/test",
    isolation_level="SERIALIZABLE",
)

#  sqlite database bilan ishlash
# from sqlalchemy import create_engine
# engine = create_engine("sqlite:///database.db", echo=True)
