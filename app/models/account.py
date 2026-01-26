"""
Account model
Stores account holder data and risk score.

DB-agnostic: works with SQLite now and PostgreSQL later.
"""

import uuid
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.db import Base


class Account(Base):
    __tablename__ = "accounts"

    # Use String UUID so it works across DBs
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Account holder name
    name = Column(String, nullable=False)

    # Risk score updated by AML engine
    risk_score = Column(Float, default=0)

    # Creation timestamp
    created_at = Column(DateTime, default=datetime.utcnow)