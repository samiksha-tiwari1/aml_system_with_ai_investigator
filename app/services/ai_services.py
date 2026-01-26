# app/services/ai_services.py
from typing import Dict
from datetime import datetime

MOCK_MODE = True  # Keep True for now, set False to enable real AI

def explain_alert(alert: Dict) -> str:
    """
    Generate a detailed, human-readable AI-style explanation for an AML alert.
    Works fully in MOCK_MODE for demo purposes.
    
    Example output:
    "Alert 'Rapid Transactions' triggered for txn 12345 (HIGH risk).
    Reason: Multiple transactions detected within 60 seconds.
    Related accounts: 456, 789.
    Recommendation: Investigate account activity for potential smurfing or mule behavior."
    """

    if MOCK_MODE:
        explanation_lines = [
            f"Alert '{alert['rule_triggered']}' triggered for transaction {alert['transaction_id']}.",
            f"Severity Level: {alert['severity']}",
            f"Reason: {alert.get('reason', 'No reason provided')}"
        ]

        # Add context based on rule type
        rule = alert['rule_triggered'].lower()
        if "rapid" in rule:
            explanation_lines.append(
                "Pattern detected: Multiple quick successive transactions. "
                "This may indicate smurfing or automated transfers."
            )
        elif "large" in rule:
            explanation_lines.append(
                "Pattern detected: High-value transaction exceeding normal threshold. "
                "Verify source of funds and legitimacy."
            )
        elif "money loop" in rule:
            explanation_lines.append(
                "Pattern detected: Circular money flow between linked accounts. "
                "Potential layering to obscure funds."
            )
        elif "mule" in rule or "otp" in rule:
            explanation_lines.append(
                "Pattern detected: Newly created account forwarding funds quickly. "
                "Potential mule/OTP scam behavior."
            )

        # Add generic recommendation
        explanation_lines.append(
            "Recommendation: Investigate account, review transaction history, "
            "and check linked accounts for suspicious activity."
        )

        return "\n".join(explanation_lines)

    # Placeholder for real AI integration (OpenAI GPT, etc.)
    # import openai
    # import os
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": f"Explain this AML alert: {alert}"}]
    # )
    # return response.choices[0].message.content