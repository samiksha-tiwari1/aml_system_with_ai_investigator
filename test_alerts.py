# test_alerts.py
import uuid
from datetime import datetime
from app.db import SessionLocal, engine, Base
from app.models import Account, Transaction, Alert
from app.services.rule_engine import evaluate_rules
from app.services.alert_service import generate_alerts

# ---------------------------------------
# Step 0: Ensure tables exist
# ---------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------
# Step 1: Create a dummy transaction
# ---------------------------------------
db = SessionLocal()

# Create dummy accounts (use str UUIDs for DB compatibility)
from_account_id = str(uuid.uuid4())
to_account_id = str(uuid.uuid4())

account_from = Account(id=from_account_id, name="Alice")
account_to = Account(id=to_account_id, name="Bob")

db.add_all([account_from, account_to])
db.commit()

# Create a transaction that should trigger a "Large Transaction Amount" rule
transaction = Transaction(
    from_account=from_account_id,
    to_account=to_account_id,
    amount=200000,  # High amount to trigger alert
    timestamp=datetime.utcnow(),
    status="processed"
)
db.add(transaction)
db.commit()
db.refresh(transaction)

# ---------------------------------------
# Step 2: Trigger alerts using rule engine
# ---------------------------------------
triggered_rules = evaluate_rules(transaction.amount, [])

alerts = generate_alerts(transaction.id, triggered_rules)

for a in alerts:
    alert = Alert(
        transaction_id=str(a["transaction_id"]),
        rule_triggered=a["rule_triggered"],
        severity=a["severity"],
        reason=a["reason"]
    )
    db.add(alert)

db.commit()

# ---------------------------------------
# Step 3: Fetch alerts to verify
# ---------------------------------------
print("\n--- ALERTS IN DATABASE ---")
all_alerts = db.query(Alert).all()
for a in all_alerts:
    print(
        a.id,
        a.transaction_id,
        a.rule_triggered,
        a.severity,
        a.reason,
        a.created_at
    )

db.close()