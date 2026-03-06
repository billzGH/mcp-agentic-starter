# Data Pipeline MCP Server

A production-style multi-stage data processing pipeline — the complete working example for [Tutorial 4: Advanced Workflows](../../tutorials/04-advanced-workflows.md).

## What It Demonstrates

- **State persistence** — each stage saves a checkpoint; Claude can resume across multiple tool calls
- **Stage-by-stage execution** — Claude controls when each stage runs via `continue_pipeline`
- **Real data processing** — ingestion, validation, cleaning, analysis, and formatted reporting on the sales dataset
- **Error recording** — failures are logged into state, not silently swallowed

## Pipeline Stages

```
INGESTION → VALIDATION → PROCESSING → ANALYSIS → REPORTING → COMPLETE
```

| Stage | What it does |
|---|---|
| **Ingestion** | Loads the CSV, detects schema, counts records |
| **Validation** | Checks required columns, flags nulls/invalid values, scores data quality |
| **Processing** | Filters to `Completed` transactions, parses numerics, extracts date parts |
| **Analysis** | Computes total revenue, average order value, payment method breakdown, monthly trend, top products |
| **Reporting** | Writes a formatted markdown report to `pipeline_state/<session_id>_report.md` |

## Prerequisites

Generate the sales dataset first if you haven't already:

```bash
uv run examples/data-analysis/generate_sales_data.py
```

## Installation

```bash
uv sync
```

## Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "data-pipeline": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-agentic-starter/examples/data-pipeline",
        "server.py"
      ]
    }
  }
}
```

## Example Session

```plaintext
Start a pipeline called "sales-2024" on datasets/sales/transactions.csv
```

```plaintext
Continue the sales-2024 pipeline
```

```plaintext
Continue the sales-2024 pipeline
```

_(repeat until complete — each call advances one stage and returns a summary)_

```plaintext
What's the status of the sales-2024 pipeline?
```

## Available Tools

| Tool | Description |
|---|---|
| `start_pipeline` | Begin a new session — runs INGESTION immediately |
| `continue_pipeline` | Advance to the next stage and return a summary |
| `get_pipeline_status` | Show current stage, progress, and any errors |

## State Files

Pipeline state is saved to `examples/data-pipeline/pipeline_state/`:

- `<session_id>.json` — checkpoint file (lightweight, no raw data rows)
- `<session_id>_report.md` — final markdown report (written after REPORTING stage)

These are gitignored. Delete them to reset a session.

## Extending This Example

Good next steps after studying this server:

- **Join data** — extend `_analysis` to load `customers.csv` and break down revenue by region
- **Add a ENRICHMENT stage** — look up product names from `products.csv` before analysis
- **Parallel analysis** — analyze each product category independently then aggregate
- **Retry logic** — catch transient file errors in `_ingest` and retry with backoff
