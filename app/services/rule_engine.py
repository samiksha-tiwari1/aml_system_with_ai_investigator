"""
rule_engine.py

Advanced AML rules engine for real-time transaction monitoring.
- Detects high-risk patterns and assigns severity.
- Returns triggered rules for alerts and risk scoring.
"""

from datetime import datetime, timedelta
from collections import defaultdict

# -----------------------------
# CONFIG / THRESHOLDS
# -----------------------------
LARGE_TXN_THRESHOLD = 100000  # ₹100,000
RAPID_TXN_WINDOW_SEC = 60     # 60 seconds
SMURF_TXN_THRESHOLD = 5       # ≥ 5 small repeated txns
SMURF_TXN_AMOUNT = 10000      # Small txn < ₹10,000
NEW_ACCOUNT_AGE_HOURS = 24    # New account window for mule detection

# -----------------------------
# Helper Functions
# -----------------------------
def get_time_diff_seconds(times):
    """Return differences in seconds between consecutive transaction timestamps."""
    times = sorted(times)
    return [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]

def detect_rapid_transactions(txn_times):
    """Detect multiple transactions in short period."""
    diffs = get_time_diff_seconds(txn_times)
    return any(d < RAPID_TXN_WINDOW_SEC for d in diffs)

def detect_mule(account_created_at, txn_time, past_txns):
    """Detect mule/OTP scams: new account forwarding funds quickly."""
    account_age = (txn_time - account_created_at).total_seconds() / 3600
    if account_age <= NEW_ACCOUNT_AGE_HOURS and len(past_txns) <= 2:
        return True
    return False

def detect_smurfing(amount, past_txns):
    """Detect repeated small-value transactions between same accounts."""
    small_txns = [t for t in past_txns if t.amount <= SMURF_TXN_AMOUNT]
    return len(small_txns) >= SMURF_TXN_THRESHOLD

def detect_circular_flow(link_pairs, txn_pair):
    """
    Detect circular money flows (A -> B -> C -> A)
    - link_pairs: list of tuples (from_account, to_account)
    - txn_pair: current txn (from_account, to_account)
    """
    graph = defaultdict(set)
    for a, b in link_pairs:
        graph[a].add(b)

    start, end = txn_pair
    # Check if end can reach start in 2 steps (A->B->C->A)
    for intermediate in graph[end]:
        if start in graph.get(intermediate, []):
            return True
    return False

def detect_false_accounts(account_activity):
    """
    Detect accounts with minimal legitimate activity that forward money quickly.
    - account_activity: dict of account_id -> number of txns
    """
    return [acc for acc, count in account_activity.items() if count <= 1]

# -----------------------------
# Main Rule Evaluation Function
# -----------------------------
def evaluate_rules(amount, txn_times, account_created_at=None, past_txns=None, link_pairs=None, account_activity=None, txn_pair=None):
    """
    Evaluate AML rules for a transaction.
    
    Args:
        amount (float): transaction amount
        txn_times (list[datetime]): previous txn timestamps for from_account
        account_created_at (datetime): account creation time
        past_txns (list[Transaction]): previous transactions of account
        link_pairs (list[(from_account, to_account)]): all account links for graph analysis
        account_activity (dict): account_id -> total txn count
        txn_pair (tuple): current transaction (from_account, to_account)
    
    Returns:
        triggered_rules (list[dict]): list of dicts with rule, severity, reason
    """
    triggered_rules = []

    # 1️ Large Transaction Amount
    if amount >= LARGE_TXN_THRESHOLD:
        triggered_rules.append({
            "rule_triggered": "Large Transaction Amount",
            "severity": "HIGH",
            "reason": f"Transaction amount exceeds safe threshold (₹{LARGE_TXN_THRESHOLD})."
        })

    # 2️ Rapid Transactions
    if txn_times and detect_rapid_transactions(txn_times):
        triggered_rules.append({
            "rule_triggered": "Rapid Transactions",
            "severity": "MEDIUM",
            "reason": f"Multiple transactions detected from this account within {RAPID_TXN_WINDOW_SEC} seconds."
        })

    # 3️ Mule / OTP scam detection
    if account_created_at and past_txns is not None and detect_mule(account_created_at, txn_times[-1], past_txns):
        triggered_rules.append({
            "rule_triggered": "Mule / OTP Scam",
            "severity": "HIGH",
            "reason": "New account forwarding received funds quickly (potential mule or OTP scam)."
        })

    # 4️ Smurfing
    if past_txns is not None and detect_smurfing(amount, past_txns):
        triggered_rules.append({
            "rule_triggered": "Smurfing",
            "severity": "MEDIUM",
            "reason": f"Multiple small transactions detected between same accounts (≥ {SMURF_TXN_THRESHOLD})."
        })

    # 5️ Circular Money Flow
    if link_pairs is not None and txn_pair is not None and detect_circular_flow(link_pairs, txn_pair):
        triggered_rules.append({
            "rule_triggered": "Money Loop Detected",
            "severity": "HIGH",
            "reason": "Circular money flow detected between linked accounts."
        })

    # 6️ False / Temporary Accounts
    if account_activity is not None:
        false_accs = detect_false_accounts(account_activity)
        if false_accs:
            triggered_rules.append({
                "rule_triggered": "False / Temporary Accounts",
                "severity": "MEDIUM",
                "reason": f"Accounts with minimal activity detected: {false_accs}."
            })

    return triggered_rules