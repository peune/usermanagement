from sqlalchemy import Boolean, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base
from typing import Any


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    family_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    workplace = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_approved = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())