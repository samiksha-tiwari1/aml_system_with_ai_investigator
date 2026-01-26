"""
alert_service.py

Responsible for generating alerts from triggered AML rules,
determining severity, and calculating risk score increases.

This module is used by the transaction ingestion pipeline.
"""

# ----------------------------
# RULE SEVERITY MAPPING
# ----------------------------
# Map rule names to severity levels
RULE_SEVERITY = {
    "Large Transaction Amount": "HIGH",
    "Rapid Transactions": "MEDIUM",
    "Money Loop Detected": "HIGH",
    "Mule Account Detected": "HIGH",
    "OTP Scam Detected": "HIGH",
    "Smurfing Pattern": "MEDIUM",
    "False / Temp Account": "MEDIUM",
    # Add more rules here as needed
}


# ----------------------------
# RISK SCORE INCREASE MAPPING
# ----------------------------
# Determines how much to increase account risk based on alert severity
RISK_SCORE_INCREASE = {
    "LOW": 5,
    "MEDIUM": 15,
    "HIGH": 30,
}


# ----------------------------
# Determine severity of a rule
# ----------------------------
def determine_severity(rule_name: str) -> str:
    """
    Maps a rule name to a severity level.
    Defaults to "LOW" if rule name is unknown.

    Args:
        rule_name (str): Name of the triggered rule

    Returns:
        str: Severity level ("LOW", "MEDIUM", "HIGH")
    """
    return RULE_SEVERITY.get(rule_name, "LOW")


# ----------------------------
# Determine risk score increase from severity
# ----------------------------
def risk_increase_from_severity(severity: str) -> int:
    """
    Maps severity level to risk score increment.

    Args:
        severity (str): "LOW", "MEDIUM", "HIGH"

    Returns:
        int: Risk score increment
    """
    return RISK_SCORE_INCREASE.get(severity, 0)


# ----------------------------
# Generate alerts for a transaction
# ----------------------------
def generate_alerts(txn_id, triggered_rules):
    """
    Converts triggered rules into alert objects with severity and reason.

    Args:
        txn_id (str): Transaction ID
        triggered_rules (list): List of triggered rules
            Each element can be either:
            - a string (rule name)
            - a dict {"rule_triggered": str, "reason": str}

    Returns:
        List[dict]: List of alerts with:
            - transaction_id
            - rule_triggered
            - severity
            - reason
    """
    alerts = []

    for rule in triggered_rules:
        # Extract rule name and reason depending on type
        if isinstance(rule, dict):
            rule_name = rule.get("rule_triggered", "Unknown Rule")
            reason = rule.get("reason", "")
        else:
            rule_name = str(rule)
            reason = ""

        severity = determine_severity(rule_name)

        alerts.append({
            "transaction_id": txn_id,
            "rule_triggered": rule_name,
            "severity": severity,
            "reason": reason
        })

    return alerts