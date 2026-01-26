"""
AccountLink model
Acts as adjacency list for graph relationships between accounts.

This version is DB-agnostic:
Works with SQLite now and PostgreSQL later.
"""

import uuid
from sqlalchemy import Column, Integer, String
from app.db import Base


class AccountLink(Base):
    __tablename__ = "account_links"

    # Use String for IDs so it works across SQLite and Postgres
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Account identifiers
    account_a = Column(String, nullable=False)
    account_b = Column(String, nullable=False)

    # Number of transactions between these accounts
    link_strength = Column(Integer, default=1)