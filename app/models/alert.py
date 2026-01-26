"""
Alert model
Stores alerts triggered by rule engine or graph analysis.
"""

import uuid
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, nullable=False)
    rule_triggered = Column(String)
    severity = Column(String)

    # NEW: human-readable reason for analysts
    reason = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)