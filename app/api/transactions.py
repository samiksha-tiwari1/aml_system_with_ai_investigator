"""
transactions.py

Real Transaction Ingestion API with:
- DB integration
- Rule engine
- Graph update
- Alert generation
- Risk audit trail
- Admin transaction view with pagination & filters
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas import TransactionCreate, TransactionResponse
from app.db import get_db
from app.models import (
    Transaction,
    Account,
    AccountLink,
    Alert,
    RiskAudit,
)

from app.services.rule_engine import evaluate_rules
from app.services.graph_service import check_money_loop
from app.services.alert_service import (
    generate_alerts,
    risk_increase_from_severity,
)

router = APIRouter()


# -----------------------------------------------------
# POST /transactions  → Ingest transaction
# -----------------------------------------------------
@router.post("/transactions", response_model=TransactionResponse)
def ingest_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """
    Main entry point where transactions enter the AML system.
    This function simulates how banks process live transactions.
    """

    # STEP 1 — Ensure both accounts exist
    for acc_id in [payload.from_account, payload.to_account]:
        acc_id_str = str(acc_id)

        account = db.query(Account).filter(Account.id == acc_id_str).first()
        if not account:
            account = Account(id=acc_id_str, name=f"User-{acc_id_str[:4]}")
            db.add(account)

    db.commit()

    # STEP 2 — Save the transaction
    transaction = Transaction(
        from_account=str(payload.from_account),
        to_account=str(payload.to_account),
        amount=payload.amount,
        timestamp=datetime.utcnow(),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # STEP 3 — Update account relationship graph (adjacency list)
    link = db.query(AccountLink).filter(
        AccountLink.account_a == str(payload.from_account),
        AccountLink.account_b == str(payload.to_account),
    ).first()

    if link:
        link.link_strength += 1
    else:
        link = AccountLink(
            account_a=str(payload.from_account),
            account_b=str(payload.to_account),
        )
        db.add(link)

    db.commit()

    # STEP 4 — Collect past transactions for rule engine
    past_txns = db.query(Transaction).filter(
        Transaction.from_account == str(payload.from_account)
    ).all()

    txn_times = [t.timestamp for t in past_txns]
    triggered_rules = evaluate_rules(payload.amount, txn_times)

    # STEP 5 — Graph analysis for money loops
    links = db.query(AccountLink).all()
    link_pairs = [(l.account_a, l.account_b) for l in links]

    if check_money_loop(link_pairs):
        triggered_rules.append("Money Loop Detected")

    # STEP 6 — Generate alerts + update risk score + store audit trail
    alerts = generate_alerts(transaction.id, triggered_rules)

    for a in alerts:
        alert = Alert(
            transaction_id=a["transaction_id"],
            rule_triggered=a["rule_triggered"],
            severity=a["severity"],
            reason=a["reason"],
        )
        db.add(alert)

        # ---- Risk score update with audit history ----
        account = db.query(Account).filter(
            Account.id == str(payload.from_account)
        ).first()

        old_score = account.risk_score
        increase = risk_increase_from_severity(a["severity"])
        new_score = old_score + increase

        account.risk_score = new_score

        audit = RiskAudit(
            account_id=account.id,
            old_score=old_score,
            new_score=new_score,
            reason=a["reason"],
        )

        db.add(audit)

    db.commit()

    # STEP 7 — Return transaction response
    return TransactionResponse(
        id=transaction.id,
        from_account=transaction.from_account,
        to_account=transaction.to_account,
        amount=transaction.amount,
        timestamp=transaction.timestamp,
        status=transaction.status,
    )


# -----------------------------------------------------
# GET /transactions  → Admin view with pagination, filters, time range, sorting
# -----------------------------------------------------
@router.get("/transactions")
def list_transactions(
    db: Session = Depends(get_db),

    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Records per page"),

    # Filters
    account_id: str | None = Query(
        None,
        description="Show transactions where this account is sender or receiver",
    ),

    # Time range filters
    start_time: datetime | None = Query(
        None,
        description="Transactions after this time (ISO format)",
    ),
    end_time: datetime | None = Query(
        None,
        description="Transactions before this time (ISO format)",
    ),

    # Sorting
    sort: str = Query(
        "desc",
        description="Sort by time: asc (oldest) or desc (newest)",
    ),
):
    query = db.query(Transaction)

    # -----------------------------
    # Account filter
    # -----------------------------
    if account_id:
        query = query.filter(
            (Transaction.from_account == account_id) |
            (Transaction.to_account == account_id)
        )

    # -----------------------------
    # Time filters
    # -----------------------------
    if start_time:
        query = query.filter(Transaction.timestamp >= start_time)

    if end_time:
        query = query.filter(Transaction.timestamp <= end_time)

    # -----------------------------
    # Sorting
    # -----------------------------
    if sort == "asc":
        query = query.order_by(Transaction.timestamp.asc())
    else:
        query = query.order_by(Transaction.timestamp.desc())

    total = query.count()

    # -----------------------------
    # Pagination
    # -----------------------------
    transactions = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "data": transactions,
    }