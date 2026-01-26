# create_tables.py
from app.db import engine, Base
from app.models import (
    Account,
    Transaction,
    Alert,
    AccountLink,
    RiskAudit,
    TransactionQueue  # <- include async queue
)

print("Creating all tables in the database...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully.")