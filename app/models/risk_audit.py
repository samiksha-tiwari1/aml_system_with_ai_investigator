"""
RiskAudit model

Stores history of risk score changes for an account.
"""

import uuid
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.db import Base


class RiskAudit(Base):
    __tablename__ = "risk_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, nullable=False)
    old_score = Column(Float)
    new_score = Column(Float)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)