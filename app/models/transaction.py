"""
Transaction model
Stores all money transfers between accounts.

DB-agnostic: works with SQLite now and PostgreSQL later.
"""

import uuid
from sqlalchemy import Column, Float, ForeignKey, String, DateTime
from datetime import datetime
from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    # Use String UUID so it works across DBs
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Sender and receiver account IDs
    from_account = Column(String, ForeignKey("accounts.id"), nullable=False)
    to_account = Column(String, ForeignKey("accounts.id"), nullable=False)

    # Transaction amount
    amount = Column(Float, nullable=False)

    # Timestamp of transaction
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Processing status
    status = Column(String, default="processed")