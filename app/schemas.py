# app/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


# -----------------------------
# Transaction Schemas
# -----------------------------
class TransactionCreate(BaseModel):
    from_account: str
    to_account: str
    amount: float


class TransactionResponse(BaseModel):
    id: str
    from_account: str
    to_account: str
    amount: float
    timestamp: datetime
    status: Optional[str] = "processed"

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Alert Schemas
# -----------------------------
class AlertCreate(BaseModel):
    transaction_id: str
    rule_triggered: str
    severity: str
    reason: str


class AlertResponse(BaseModel):
    id: str
    transaction_id: str
    rule_triggered: str
    severity: str
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Account Schemas
# -----------------------------
class AccountResponse(BaseModel):
    id: str
    name: str
    risk_score: float
    total_transactions: int
    linked_accounts: List[str]
    transactions: List[TransactionResponse]

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Risk Audit Schemas
# -----------------------------
class RiskAuditResponse(BaseModel):
    account_id: str
    old_score: float
    new_score: float
    reason: str
    time: datetime

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Pagination / Filter Schemas
# -----------------------------
class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10


class AlertFilterParams(PaginationParams):
    severity: Optional[str] = None
    transaction_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None