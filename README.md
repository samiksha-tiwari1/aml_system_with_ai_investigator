
# Real-Time AML & Fraud Detection System + AI Investigator

A **production-grade backend system** built with Python and FastAPI that monitors financial transactions in real-time, detects suspicious activity, generates alerts, and provides AI-powered explanations for alerts. This project simulates how real banks and fintechs detect money laundering and fraud.

## 

![UI](image.png)

---

## Features

- **Transaction Ingestion API**
  - Accepts real-time transactions
  - Ensures accounts exist, saves transaction, updates account relationships

- **AML Rule Engine**
  - Large transaction detection
  - Rapid multiple transactions detection
  - Mule / OTP scams detection
  - Smurfing (splitting large transactions)
  - Circular money flow detection
  - False / temporary account detection

- **Graph Analysis**
  - Tracks linked accounts
  - Detects suspicious circular flows
  - Supports risk scoring

- **Alert Management**
  - Generates alerts with severity (LOW, MEDIUM, HIGH)
  - View alerts with filters, pagination, and sorting
  - Admin endpoints for single alert details

- **Account Risk Scoring & Audit Trail**
  - Updates account risk scores per alert
  - Full audit trail for compliance and monitoring

- **AI Investigator Module**
  - Endpoint for human-readable explanations of alerts
  - Mock mode ready for testing
  - Future GPT/LLM integration supported

---

## Tech Stack

**Backend**
- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite (development) / PostgreSQL (production-ready)
- Pydantic for schema validation

**Frontend / Interaction**
- Swagger UI (`/docs`) for API testing
- Optional LLM/AI module (mock mode included)

---

## How It Works

1. Transactions are received via `/transactions`.
2. Accounts are validated and saved; account relationships are updated.
3. AML rules are applied to detect suspicious activity.
4. Alerts are generated based on rules and severity.
5. Risk scoring is updated and recorded in audit logs.
6. Admin APIs allow filtering, pagination, and investigation of alerts.
7. AI Investigator generates human-readable explanations for alerts.

---

## Project Structure

aml_system/
│
├── app/
│   ├── api/
│   │   ├── transactions.py
│   │   ├── alerts.py
│   │   ├── accounts.py
│   │   └── ai.py
│   ├── models/
│   │   ├── transaction.py
│   │   ├── alert.py
│   │   ├── account.py
│   │   ├── account_link.py
│   │   ├── risk_audit.py
│   │   └── txn_queue.py
│   ├── schemas.py
│   ├── db.py
│   └── services/
│       ├── rule_engine.py
│       ├── graph_service.py
│       ├── alert_service.py
│       └── ai_services.py
│
├── worker/
│   └── transaction_worker.py
├── main.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md

---

## Running the Project

**Backend (FastAPI)**

```bash
cd aml_system
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
pip install -r requirements.txt
python -c "from app.db import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
uvicorn main:app --reload

	•	Swagger UI: http://127.0.0.1:8000/docs￼

Worker (Optional)

python -m worker.transaction_worker


⸻

API Examples

Create Transaction

POST /transactions
{
  "from_account": "acc_123",
  "to_account": "acc_456",
  "amount": 150000
}

List Alerts

GET /alerts?page=1&size=5&account_id=acc_123&severity=HIGH&start_time=2026-01-26T00:00:00&end_time=2026-01-26T23:59:59

Single Alert

GET /alerts/<alert_id>

AI Explanation

GET /ai/alert/<alert_id>?use_mock=True


⸻

Example Test Scenario
	1.	Create transaction: from_account="acc_1", to_account="acc_2", amount=150000
	2.	Trigger alert: Large Transaction Amount with HIGH severity
	3.	Fetch alert via /alerts and /alerts/<alert_id>
	4.	Fetch AI explanation via /ai/alert/<alert_id>

⸻

Future Enhancements
	•	Switch to PostgreSQL for production
	•	Integrate GPT/LLM for AI Investigator
	•	Async transaction processing (Celery / background worker)
	•	Dockerize backend with docker-compose
	•	Monitoring and structured logging

⸻

