"""
alerts.py

Admin API for alerts management.
- View alerts
- Filter by account, severity, time
- Pagination support
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models import Alert, Transaction, Account

router = APIRouter()


# -----------------------------------------------------
# GET /alerts  → View all alerts with filters & pagination
# -----------------------------------------------------
@router.get("/alerts")
def list_alerts(
    db: Session = Depends(get_db),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW/MEDIUM/HIGH"),
    start_time: Optional[datetime] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time filter (ISO format)"),
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(Alert)

    # Filter by account_id if provided
    if account_id:
        txn_ids = (
            select(Transaction.id)
            .where(
                (Transaction.from_account == account_id) |
                (Transaction.to_account == account_id)
            )
        )
        query = query.filter(Alert.transaction_id.in_(txn_ids))

    # Filter by severity
    if severity:
        query = query.filter(Alert.severity == severity.upper())

    # Filter by time range
    if start_time:
        query = query.filter(Alert.created_at >= start_time)
    if end_time:
        query = query.filter(Alert.created_at <= end_time)

    # Pagination
    alerts = (
        query.order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": a.id,
            "transaction_id": a.transaction_id,
            "rule_triggered": a.rule_triggered,
            "severity": a.severity,
            "reason": getattr(a, "reason", ""),
            "created_at": a.created_at,
        }
        for a in alerts
    ]


# -----------------------------------------------------
# GET /alerts/{alert_id}  → View single alert details
# -----------------------------------------------------
@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "id": alert.id,
        "transaction_id": alert.transaction_id,
        "rule_triggered": alert.rule_triggered,
        "severity": alert.severity,
        "reason": getattr(alert, "reason", ""),
        "created_at": alert.created_at,
    }