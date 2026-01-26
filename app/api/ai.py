# app/api/ai.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Alert
from app.services.ai_services import explain_alert

router = APIRouter(tags=["AI Investigator"])

@router.get("/ai/alert/{alert_id}")
def get_ai_alert_explanation(alert_id: str, db: Session = Depends(get_db)):
    """
    Fetch a human-readable AI explanation for a given alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    explanation = explain_alert({
        "transaction_id": alert.transaction_id,
        "rule_triggered": alert.rule_triggered,
        "severity": alert.severity,
        "reason": getattr(alert, "reason", "No reason provided"),
    })

    return {"alert_id": alert.id, "explanation": explanation}