# worker/transaction_worker.py
import time
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.txn_queue import TransactionQueue
from app.api.transactions import ingest_transaction  # Ensure processing logic is in a reusable service

def process_transaction_queue():
    db: Session = SessionLocal()
    while True:
        # Fetch one pending transaction safely
        pending = (
            db.query(TransactionQueue)
            .filter(TransactionQueue.status == "pending")
            .order_by(TransactionQueue.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )

        if pending:
            try:
                pending.status = "processing"
                db.commit()

                # Process transaction using existing logic
                ingest_transaction(pending.txn_id, db=db)

                pending.status = "done"
            except Exception as e:
                pending.retries += 1
                pending.status = "failed" if pending.retries > 3 else "pending"
            finally:
                db.commit()
        else:
            time.sleep(1)  # No pending txn, wait

if __name__ == "__main__":
    process_transaction_queue()