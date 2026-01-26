"""
accounts.py

Admin API to inspect an account deeply:
- Risk score
- Transactions
- Linked accounts (graph view)
- Risk history audit trail
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Account, Transaction, AccountLink, RiskAudit

router = APIRouter()


# -----------------------------------------------------
# GET /accounts/{account_id}
# Full account inspection
# -----------------------------------------------------
@router.get("/accounts/{account_id}")
def get_account_details(account_id: str, db: Session = Depends(get_db)):

    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # All transactions of this account
    transactions = db.query(Transaction).filter(
        (Transaction.from_account == account_id) |
        (Transaction.to_account == account_id)
    ).all()

    # Linked accounts from graph
    links = db.query(AccountLink).filter(
        (AccountLink.account_a == account_id) |
        (AccountLink.account_b == account_id)
    ).all()

    linked_accounts = set()
    for l in links:
        if l.account_a != account_id:
            linked_accounts.add(l.account_a)
        if l.account_b != account_id:
            linked_accounts.add(l.account_b)

    return {
        "account_id": account.id,
        "name": account.name,
        "risk_score": account.risk_score,
        "total_transactions": len(transactions),
        "linked_accounts": list(linked_accounts),
        "transactions": [
            {
                "id": t.id,
                "from": t.from_account,
                "to": t.to_account,
                "amount": t.amount,
                "time": t.timestamp,
            }
            for t in transactions
        ],
    }


# -----------------------------------------------------
# GET /accounts/{account_id}/risk-history
# Shows why risk score changed over time
# -----------------------------------------------------
@router.get("/accounts/{account_id}/risk-history")
def get_risk_history(account_id: str, db: Session = Depends(get_db)):
    audits = db.query(RiskAudit).filter(
        RiskAudit.account_id == account_id
    ).order_by(RiskAudit.timestamp.desc()).all()

    return [
        {
            "old_score": a.old_score,
            "new_score": a.new_score,
            "reason": a.reason,
            "time": a.timestamp,
        }
        for a in audits
    ]