#!/usr/bin/env python3
"""
Generate synthetic customer support ticket dataset.
Produces customer_support_tickets.csv and customer_support_tickets.json
in the same directory as this script.

Usage:
    uv run datasets/customer-support/generate_data.py
"""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

CATEGORIES = ["Billing", "Technical", "Shipping", "Account", "Product", "Refund"]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
PRIORITY_WEIGHTS = [0.35, 0.40, 0.18, 0.07]

STATUSES = ["Open", "In Progress", "Resolved", "Closed", "Escalated"]
STATUS_WEIGHTS = [0.20, 0.15, 0.40, 0.20, 0.05]

CHANNELS = ["Email", "Chat", "Phone", "Web Form"]
CHANNEL_WEIGHTS = [0.40, 0.30, 0.20, 0.10]

SENTIMENTS = ["Positive", "Neutral", "Negative", "Very Negative"]
SENTIMENT_WEIGHTS = [0.15, 0.35, 0.35, 0.15]

AGENTS = [
    "Agent_001", "Agent_002", "Agent_003", "Agent_004", "Agent_005",
    "Agent_006", "Agent_007", "Agent_008",
]

SUBJECT_TEMPLATES = {
    "Billing": [
        "Incorrect charge on my account",
        "Double billed for subscription",
        "Invoice missing from account",
        "Unexpected fee on statement",
        "Request for billing adjustment",
    ],
    "Technical": [
        "Cannot log in to my account",
        "App crashes on startup",
        "Feature not working as expected",
        "Error message when submitting form",
        "Slow performance issues",
    ],
    "Shipping": [
        "Order not received",
        "Package arrived damaged",
        "Wrong item delivered",
        "Tracking number not updating",
        "Delivery address needs correction",
    ],
    "Account": [
        "Unable to reset password",
        "Account locked after failed login",
        "Need to update payment method",
        "Request to close account",
        "Email address change not working",
    ],
    "Product": [
        "Product stopped working after update",
        "Missing feature from previous version",
        "Compatibility issue with my device",
        "Data loss after upgrade",
        "Requesting product documentation",
    ],
    "Refund": [
        "Request refund for duplicate order",
        "Item not as described, want refund",
        "Cancelled subscription but still charged",
        "Refund status inquiry",
        "Partial refund request",
    ],
}

RESOLUTION_NOTES = {
    "Billing": "Billing team reviewed the account and issued a credit.",
    "Technical": "Engineering identified the root cause and deployed a fix.",
    "Shipping": "Carrier was contacted and replacement shipment arranged.",
    "Account": "Account access restored and security review completed.",
    "Product": "Product team acknowledged the issue and added it to the backlog.",
    "Refund": "Refund processed and will appear within 3-5 business days.",
}


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_ticket(ticket_id: int, start_date: datetime, end_date: datetime) -> dict:
    category = random.choice(CATEGORIES)
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
    channel = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0]
    sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]
    subject = random.choice(SUBJECT_TEMPLATES[category])

    created_at = random_date(start_date, end_date)

    # Resolution time varies by priority
    resolution_hours = {
        "Critical": random.randint(1, 8),
        "High": random.randint(4, 24),
        "Medium": random.randint(8, 72),
        "Low": random.randint(24, 168),
    }[priority]

    resolved_at = None
    if status in ("Resolved", "Closed"):
        resolved_at = created_at + timedelta(hours=resolution_hours)

    customer_id = f"CUST{random.randint(1000, 9999)}"
    agent = random.choice(AGENTS) if status != "Open" else None
    satisfaction = None
    if status in ("Resolved", "Closed"):
        satisfaction = random.randint(1, 5)

    return {
        "ticket_id": f"TKT{ticket_id:05d}",
        "customer_id": customer_id,
        "category": category,
        "priority": priority,
        "status": status,
        "channel": channel,
        "subject": subject,
        "sentiment": sentiment,
        "assigned_agent": agent or "",
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else "",
        "resolution_hours": resolution_hours if resolved_at else "",
        "satisfaction_score": satisfaction or "",
        "resolution_note": RESOLUTION_NOTES[category] if resolved_at else "",
        "escalated": status == "Escalated",
        "first_response_hours": round(random.uniform(0.25, resolution_hours * 0.3), 2),
    }


def main(n: int = 1000):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    tickets = [generate_ticket(i + 1, start_date, end_date) for i in range(n)]

    # Sort by created_at for readability
    tickets.sort(key=lambda t: t["created_at"])

    # Write CSV
    csv_path = OUTPUT_DIR / "customer_support_tickets.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)
    print(f"Wrote {len(tickets)} rows to {csv_path}")

    # Write JSON
    json_path = OUTPUT_DIR / "customer_support_tickets.json"
    with open(json_path, "w") as f:
        json.dump(tickets, f, indent=2)
    print(f"Wrote {len(tickets)} records to {json_path}")


if __name__ == "__main__":
    main()
