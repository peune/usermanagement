from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base # >old code
from sqlalchemy.orm import sessionmaker
from typing import Any

from config import settings

SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)
# The str() call ensures proper type conversion
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/userdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base() # >old code
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass