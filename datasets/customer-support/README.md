# Customer Support Tickets Dataset

Synthetic dataset of 1,000 customer support tickets spanning a full calendar year (2024). Designed for practicing NLP analysis, prioritization workflows, and agentic triage tasks with the data-analysis MCP server.

## Generating the Data

```bash
uv run datasets/customer-support/generate_data.py
```

This creates two files in the same directory:

- `customer_support_tickets.csv` — pipe-ready flat format
- `customer_support_tickets.json` — nested format for JSON-aware tools

## Schema

| Column | Type | Description |
|---|---|---|
| `ticket_id` | string | Unique ID (e.g. `TKT00001`) |
| `customer_id` | string | Customer reference (e.g. `CUST4821`) |
| `category` | string | Billing, Technical, Shipping, Account, Product, Refund |
| `priority` | string | Low, Medium, High, Critical |
| `status` | string | Open, In Progress, Resolved, Closed, Escalated |
| `channel` | string | Email, Chat, Phone, Web Form |
| `subject` | string | Short description of the issue |
| `sentiment` | string | Positive, Neutral, Negative, Very Negative |
| `assigned_agent` | string | Agent ID (empty if unassigned) |
| `created_at` | datetime | Ticket creation timestamp |
| `resolved_at` | datetime | Resolution timestamp (empty if unresolved) |
| `resolution_hours` | integer | Hours from creation to resolution |
| `satisfaction_score` | integer | Customer rating 1–5 (empty if unresolved) |
| `resolution_note` | string | Summary of how the ticket was resolved |
| `escalated` | boolean | Whether the ticket was escalated |
| `first_response_hours` | float | Hours until first agent response |

## Distribution

| Field | Values |
|---|---|
| Categories | Billing, Technical, Shipping, Account, Product, Refund (equal weight) |
| Priority | ~35% Low, ~40% Medium, ~18% High, ~7% Critical |
| Status | ~20% Open, ~15% In Progress, ~40% Resolved, ~20% Closed, ~5% Escalated |
| Channel | ~40% Email, ~30% Chat, ~20% Phone, ~10% Web Form |
| Sentiment | ~15% Positive, ~35% Neutral, ~35% Negative, ~15% Very Negative |

## Example Prompts

Use these with the data-analysis MCP server after generating the data:

```plaintext
What are the most common ticket categories?
```

```plaintext
What is the average resolution time by priority level?
```

```plaintext
Which categories have the most escalated tickets?
```

```plaintext
Show me tickets with Very Negative sentiment that are still Open or In Progress
```

```plaintext
What is the average customer satisfaction score by category?
```

```plaintext
Which agents handle the most Critical priority tickets?
```

```plaintext
Analyze trends: are ticket volumes higher in certain months?
```

## Sample Queries (Database Server)

If you load this data into the database server:

```sql
-- Average resolution time by priority
SELECT priority, AVG(resolution_hours) as avg_hours
FROM tickets
WHERE resolved_at != ''
GROUP BY priority
ORDER BY avg_hours;

-- Escalation rate by category
SELECT category,
       COUNT(*) as total,
       SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END) as escalated,
       ROUND(100.0 * SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as escalation_pct
FROM tickets
GROUP BY category;

-- Agent performance by satisfaction score
SELECT assigned_agent, AVG(satisfaction_score) as avg_satisfaction, COUNT(*) as tickets_handled
FROM tickets
WHERE satisfaction_score != ''
GROUP BY assigned_agent
ORDER BY avg_satisfaction DESC;
```
