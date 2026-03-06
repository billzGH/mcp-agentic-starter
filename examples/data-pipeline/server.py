#!/usr/bin/env python3
"""
Data Pipeline MCP Server — Tutorial 4 Complete Example

Demonstrates a production-style multi-stage processing pipeline with:
  - State persistence across tool calls (checkpoint/resume)
  - Stage-by-stage execution Claude controls via continue_pipeline
  - Comprehensive error handling and logging
  - Real CSV data processing using the sales dataset

Stages:
  1. INGESTION  — load file, detect schema, count records
  2. VALIDATION — check data quality, flag issues, score the dataset
  3. PROCESSING — filter and clean records, extract date components
  4. ANALYSIS   — compute revenue, trends, and payment breakdowns
  5. REPORTING  — write a formatted markdown report to disk

Run directly to test: uv run examples/data-pipeline/server.py
See README.md for Claude Desktop configuration.
"""

import asyncio
import csv
import json
import logging
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("data-pipeline")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
STAGE_ORDER = ["ingestion", "validation", "processing", "analysis", "reporting", "complete"]

REQUIRED_COLUMNS = {"transaction_id", "transaction_date", "total_amount", "status", "payment_method"}
VALID_STATUSES = {"Completed", "Pending", "Cancelled"}

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


def make_state(session_id: str, input_file: str) -> dict:
    return {
        "session_id": session_id,
        "stage": "ingestion",
        "input_file": input_file,
        "records_processed": 0,
        "errors": [],
        "results": {},
    }


def next_stage(state: dict) -> None:
    idx = STAGE_ORDER.index(state["stage"])
    state["stage"] = STAGE_ORDER[idx + 1]


def record_error(state: dict, message: str) -> None:
    state["errors"].append({"stage": state["stage"], "error": message, "timestamp": datetime.now().isoformat()})
    logger.error(f"[{state['stage']}] {message}")


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def resolve_path(input_file: str) -> Path:
    """Resolve a path that may be absolute or relative to the repo root."""
    p = Path(input_file)
    return p if p.is_absolute() else REPO_ROOT / p


def load_csv(path: Path) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Stage implementations
# ---------------------------------------------------------------------------


async def _ingest(state: dict) -> dict:
    """Stage 1 — Load file, detect schema, count records."""
    path = resolve_path(state["input_file"])

    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            f"Generate it first: uv run datasets/sales/generate_sales_data.py"
        )

    rows = load_csv(path)
    if not rows:
        raise ValueError("Input file is empty.")

    columns = list(rows[0].keys())
    state["records_processed"] = len(rows)
    state["results"]["ingestion"] = {
        "total_records": len(rows),
        "columns": columns,
        "file_size_kb": round(path.stat().st_size / 1024, 1),
        "sample_record": rows[0],
    }

    logger.info(f"[ingestion] Loaded {len(rows):,} records, {len(columns)} columns from {path.name}")
    next_stage(state)
    return state


async def _validate(state: dict) -> dict:
    """Stage 2 — Check data quality: missing fields, invalid values, quality score."""
    path = resolve_path(state["input_file"])
    rows = load_csv(path)
    columns = set(rows[0].keys()) if rows else set()

    issues: List[str] = []
    error_count = 0

    # Check required columns
    missing_cols = REQUIRED_COLUMNS - columns
    if missing_cols:
        issues.append(f"Missing required columns: {sorted(missing_cols)}")
        error_count += len(missing_cols) * len(rows)  # every row is affected

    # Per-column null/empty counts
    null_counts: Dict[str, int] = defaultdict(int)
    invalid_amounts = 0
    invalid_statuses = 0

    for row in rows:
        for col in columns:
            if not row.get(col, "").strip():
                null_counts[col] += 1

        # Validate total_amount
        try:
            amount = float(row.get("total_amount", ""))
            if amount < 0:
                invalid_amounts += 1
                error_count += 1
        except (ValueError, TypeError):
            invalid_amounts += 1
            error_count += 1

        # Validate status
        status = row.get("status", "")
        if status not in VALID_STATUSES:
            invalid_statuses += 1
            error_count += 1

    if invalid_amounts:
        issues.append(f"{invalid_amounts} records with missing or negative total_amount")
    if invalid_statuses:
        issues.append(f"{invalid_statuses} records with unrecognised status values")

    # Columns with > 5% nulls are flagged
    high_null_cols = {col: count for col, count in null_counts.items() if count / len(rows) > 0.05}
    if high_null_cols:
        issues.append(f"High null rate (>5%) in: {list(high_null_cols.keys())}")

    quality_score = max(0.0, round(100.0 - (error_count / len(rows)) * 100, 1))

    state["results"]["validation"] = {
        "quality_score": quality_score,
        "total_records": len(rows),
        "null_counts": dict(null_counts),
        "invalid_amounts": invalid_amounts,
        "invalid_statuses": invalid_statuses,
        "issues": issues,
        "passed": len(issues) == 0,
    }

    logger.info(f"[validation] Quality score: {quality_score}/100 — {len(issues)} issue(s) found")
    next_stage(state)
    return state


async def _process(state: dict) -> dict:
    """Stage 3 — Filter to completed records, parse numeric fields, extract date parts."""
    path = resolve_path(state["input_file"])
    rows = load_csv(path)

    completed = []
    skipped = 0

    for row in rows:
        if row.get("status") != "Completed":
            skipped += 1
            continue
        try:
            row["_amount"] = float(row["total_amount"])
            row["_quantity"] = int(row.get("quantity", 1) or 1)
            row["_discount"] = float(row.get("discount", 0) or 0)
        except (ValueError, TypeError):
            skipped += 1
            continue

        # Extract year-month for trend analysis
        date_str = row.get("transaction_date", "")
        row["_year_month"] = date_str[:7] if len(date_str) >= 7 else "unknown"
        completed.append(row)

    if not completed:
        raise ValueError("No completed transactions found after filtering.")

    dates = [r["transaction_date"] for r in completed if r.get("transaction_date")]
    state["records_processed"] = len(completed)
    state["results"]["processing"] = {
        "completed_records": len(completed),
        "skipped_records": skipped,
        "filter_applied": "status == 'Completed'",
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
        },
    }

    # Stash the processed rows for downstream stages (stored in results, not state root)
    # In a real system these would be written to a temp file; here we keep them in memory
    # across the in-process pipeline call. We serialize a compact summary instead.
    state["results"]["_processed_rows"] = [
        {k: v for k, v in r.items() if k.startswith("_") or k in
         ("transaction_id", "customer_id", "product_id", "payment_method", "transaction_date")}
        for r in completed
    ]

    logger.info(f"[processing] {len(completed):,} completed records retained, {skipped} skipped")
    next_stage(state)
    return state


async def _analyze(state: dict) -> dict:
    """Stage 4 — Compute revenue, trends, top products, payment breakdown."""
    # Reload from source to avoid carrying large data in state across tool calls
    path = resolve_path(state["input_file"])
    rows = load_csv(path)

    completed = []
    for row in rows:
        if row.get("status") != "Completed":
            continue
        try:
            row["_amount"] = float(row["total_amount"])
            row["_discount"] = float(row.get("discount", 0) or 0)
            row["_quantity"] = int(row.get("quantity", 1) or 1)
            row["_year_month"] = row.get("transaction_date", "")[:7]
        except (ValueError, TypeError):
            continue
        completed.append(row)

    if not completed:
        raise ValueError("No completed transactions available for analysis.")

    amounts = [r["_amount"] for r in completed]
    total_revenue = sum(amounts)
    avg_order_value = statistics.mean(amounts)

    # Revenue by payment method
    by_payment: Dict[str, float] = defaultdict(float)
    for r in completed:
        by_payment[r.get("payment_method", "Unknown")] += r["_amount"]

    # Monthly revenue trend
    by_month: Dict[str, float] = defaultdict(float)
    for r in completed:
        by_month[r["_year_month"]] += r["_amount"]
    monthly_trend = {k: round(v, 2) for k, v in sorted(by_month.items())}

    # Top 10 products by revenue
    by_product: Dict[str, float] = defaultdict(float)
    for r in completed:
        pid = r.get("product_id", "unknown")
        by_product[pid] += r["_amount"]
    top_products = sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:10]

    # Discount analysis
    discounts = [r["_discount"] for r in completed]
    avg_discount = statistics.mean(discounts) if discounts else 0.0
    discounted_orders = sum(1 for d in discounts if d > 0)

    state["results"]["analysis"] = {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": len(completed),
        "average_order_value": round(avg_order_value, 2),
        "revenue_by_payment_method": {k: round(v, 2) for k, v in sorted(by_payment.items(), key=lambda x: x[1], reverse=True)},
        "monthly_revenue_trend": monthly_trend,
        "top_10_products_by_revenue": [{"product_id": pid, "revenue": round(rev, 2)} for pid, rev in top_products],
        "discount_analysis": {
            "average_discount_pct": round(avg_discount, 2),
            "orders_with_discount": discounted_orders,
            "discount_rate": round(discounted_orders / len(completed) * 100, 1),
        },
    }

    # Clean up the temporary processed rows from state to keep it lightweight
    state["results"].pop("_processed_rows", None)

    logger.info(f"[analysis] Total revenue: ${total_revenue:,.2f} across {len(completed):,} transactions")
    next_stage(state)
    return state


async def _report(state: dict) -> dict:
    """Stage 5 — Write a formatted markdown report and record its path in state."""
    ingestion = state["results"].get("ingestion", {})
    validation = state["results"].get("validation", {})
    processing = state["results"].get("processing", {})
    analysis = state["results"].get("analysis", {})

    lines = [
        f"# Data Pipeline Report",
        f"",
        f"**Session**: `{state['session_id']}`  ",
        f"**Input file**: `{state['input_file']}`  ",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"---",
        f"",
        f"## 1. Ingestion",
        f"",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total records | {ingestion.get('total_records', 'N/A'):,} |",
        f"| Columns | {len(ingestion.get('columns', []))} |",
        f"| File size | {ingestion.get('file_size_kb', 'N/A')} KB |",
        f"",
        f"**Columns detected**: {', '.join(ingestion.get('columns', []))}",
        f"",
        f"---",
        f"",
        f"## 2. Validation",
        f"",
        f"**Quality score: {validation.get('quality_score', 'N/A')}/100**",
        f"",
    ]

    issues = validation.get("issues", [])
    if issues:
        lines.append("**Issues found:**")
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("No data quality issues found.")

    lines += [
        f"",
        f"| Check | Result |",
        f"|---|---|",
        f"| Invalid amounts | {validation.get('invalid_amounts', 0)} |",
        f"| Invalid statuses | {validation.get('invalid_statuses', 0)} |",
        f"",
        f"---",
        f"",
        f"## 3. Processing",
        f"",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Completed transactions | {processing.get('completed_records', 'N/A'):,} |",
        f"| Skipped records | {processing.get('skipped_records', 'N/A'):,} |",
        f"| Date range | {processing.get('date_range', {}).get('earliest', 'N/A')} → {processing.get('date_range', {}).get('latest', 'N/A')} |",
        f"",
        f"---",
        f"",
        f"## 4. Analysis",
        f"",
        f"### Revenue Summary",
        f"",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total revenue | ${analysis.get('total_revenue', 0):,.2f} |",
        f"| Total transactions | {analysis.get('total_transactions', 0):,} |",
        f"| Average order value | ${analysis.get('average_order_value', 0):,.2f} |",
        f"",
        f"### Revenue by Payment Method",
        f"",
        f"| Payment Method | Revenue |",
        f"|---|---|",
    ]

    for method, rev in analysis.get("revenue_by_payment_method", {}).items():
        lines.append(f"| {method} | ${rev:,.2f} |")

    lines += [
        f"",
        f"### Top 10 Products by Revenue",
        f"",
        f"| Rank | Product ID | Revenue |",
        f"|---|---|---|",
    ]
    for i, entry in enumerate(analysis.get("top_10_products_by_revenue", []), 1):
        lines.append(f"| {i} | {entry['product_id']} | ${entry['revenue']:,.2f} |")

    lines += [
        f"",
        f"### Monthly Revenue Trend",
        f"",
        f"| Month | Revenue |",
        f"|---|---|",
    ]
    for month, rev in analysis.get("monthly_revenue_trend", {}).items():
        lines.append(f"| {month} | ${rev:,.2f} |")

    discount = analysis.get("discount_analysis", {})
    lines += [
        f"",
        f"### Discount Analysis",
        f"",
        f"- Average discount: **{discount.get('average_discount_pct', 0):.1f}%**",
        f"- Orders with discount: **{discount.get('orders_with_discount', 0):,}** ({discount.get('discount_rate', 0):.1f}% of total)",
        f"",
        f"---",
        f"",
        f"## Pipeline Errors",
        f"",
    ]

    if state["errors"]:
        for err in state["errors"]:
            lines.append(f"- **[{err['stage']}]** {err['error']} _(at {err['timestamp']})_")
    else:
        lines.append("No errors recorded.")

    report_text = "\n".join(lines)

    # Save report to pipeline_state/
    state_dir = Path(__file__).parent / "pipeline_state"
    state_dir.mkdir(exist_ok=True)
    report_path = state_dir / f"{state['session_id']}_report.md"
    report_path.write_text(report_text, encoding="utf-8")

    state["results"]["report"] = {
        "report_path": str(report_path),
        "report_text": report_text,
    }

    logger.info(f"[reporting] Report saved to {report_path}")
    next_stage(state)
    return state


# ---------------------------------------------------------------------------
# DataPipeline orchestrator
# ---------------------------------------------------------------------------


class DataPipeline:
    """Orchestrates pipeline stages with JSON state persistence."""

    def __init__(self):
        self.state_dir = Path(__file__).parent / "pipeline_state"
        self.state_dir.mkdir(exist_ok=True)

    def save_state(self, state: dict) -> None:
        state_file = self.state_dir / f"{state['session_id']}.json"
        # Exclude large report text from persisted state
        slim = {k: v for k, v in state.items() if k != "results"}
        slim_results = {k: v for k, v in state.get("results", {}).items() if k != "report"}
        if "report" in state.get("results", {}):
            slim_results["report"] = {"report_path": state["results"]["report"].get("report_path")}
        slim["results"] = slim_results
        state_file.write_text(json.dumps(slim, indent=2), encoding="utf-8")
        logger.info(f"State saved → {state_file.name}")

    def load_state(self, session_id: str) -> dict:
        state_file = self.state_dir / f"{session_id}.json"
        if not state_file.exists():
            raise ValueError(f"No pipeline session found: '{session_id}'. Start one with start_pipeline first.")
        return json.loads(state_file.read_text(encoding="utf-8"))

    async def run_stage(self, state: dict) -> dict:
        stage = state["stage"]
        logger.info(f"Running stage: {stage}")
        stage_fn = {
            "ingestion": _ingest,
            "validation": _validate,
            "processing": _process,
            "analysis": _analyze,
            "reporting": _report,
        }.get(stage)

        if stage_fn is None:
            raise ValueError(f"Unknown or already-complete stage: '{stage}'")

        try:
            return await stage_fn(state)
        except Exception as e:
            record_error(state, str(e))
            raise


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

server = Server("data-pipeline")
pipeline = DataPipeline()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="start_pipeline",
            description=(
                "Start a new data pipeline session. Runs the INGESTION stage immediately. "
                "Use continue_pipeline to advance through VALIDATION → PROCESSING → ANALYSIS → REPORTING."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Path to CSV file (relative to repo root or absolute). "
                                       "Default: datasets/sales/transactions.csv",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Unique name for this pipeline run (e.g. 'sales-q4-2024').",
                    },
                },
                "required": ["input_file", "session_id"],
            },
        ),
        Tool(
            name="continue_pipeline",
            description="Execute the next stage of an existing pipeline session and return a summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID returned by start_pipeline.",
                    }
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="get_pipeline_status",
            description="Get the current status and accumulated results for a pipeline session.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to check.",
                    }
                },
                "required": ["session_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    try:
        if name == "start_pipeline":
            session_id = arguments["session_id"]
            input_file = arguments.get("input_file", "datasets/sales/transactions.csv")

            state = make_state(session_id, input_file)
            state = await pipeline.run_stage(state)
            pipeline.save_state(state)

            ingestion = state["results"].get("ingestion", {})
            msg = (
                f"Pipeline started — session: {session_id}\n\n"
                f"Stage completed: INGESTION\n"
                f"  Records loaded: {ingestion.get('total_records', 0):,}\n"
                f"  Columns: {len(ingestion.get('columns', []))}\n"
                f"  File size: {ingestion.get('file_size_kb')} KB\n\n"
                f"Next stage: VALIDATION\n"
                f"Run continue_pipeline to proceed."
            )
            return [TextContent(type="text", text=msg)]

        elif name == "continue_pipeline":
            session_id = arguments["session_id"]
            state = pipeline.load_state(session_id)

            if state["stage"] == "complete":
                return [TextContent(type="text", text=f"Pipeline '{session_id}' is already complete.")]

            state = await pipeline.run_stage(state)
            pipeline.save_state(state)

            completed_stage = STAGE_ORDER[STAGE_ORDER.index(state["stage"]) - 1].upper()
            next = state["stage"].upper()

            if state["stage"] == "complete":
                report = state["results"].get("report", {})
                msg = (
                    f"Pipeline complete!\n\n"
                    f"Stage completed: REPORTING\n"
                    f"Report saved to: {report.get('report_path')}\n\n"
                    + report.get("report_text", "")
                )
            else:
                # Build a brief stage summary
                stage_key = completed_stage.lower()
                stage_data = state["results"].get(stage_key, {})
                summary_lines = [f"Stage completed: {completed_stage}"]

                if stage_key == "validation":
                    summary_lines += [
                        f"  Quality score: {stage_data.get('quality_score')}/100",
                        f"  Issues: {len(stage_data.get('issues', []))}",
                    ]
                    for issue in stage_data.get("issues", []):
                        summary_lines.append(f"    • {issue}")
                elif stage_key == "processing":
                    summary_lines += [
                        f"  Completed records: {stage_data.get('completed_records', 0):,}",
                        f"  Skipped: {stage_data.get('skipped_records', 0):,}",
                        f"  Date range: {stage_data.get('date_range', {}).get('earliest')} → {stage_data.get('date_range', {}).get('latest')}",
                    ]
                elif stage_key == "analysis":
                    summary_lines += [
                        f"  Total revenue: ${stage_data.get('total_revenue', 0):,.2f}",
                        f"  Transactions: {stage_data.get('total_transactions', 0):,}",
                        f"  Avg order value: ${stage_data.get('average_order_value', 0):,.2f}",
                    ]

                summary_lines += [f"", f"Next stage: {next}", f"Run continue_pipeline to proceed."]
                msg = "\n".join(summary_lines)

            return [TextContent(type="text", text=msg)]

        elif name == "get_pipeline_status":
            session_id = arguments["session_id"]
            state = pipeline.load_state(session_id)

            lines = [
                f"Pipeline Status — {session_id}",
                f"",
                f"Current stage : {state['stage'].upper()}",
                f"Records processed: {state['records_processed']:,}",
                f"Errors recorded: {len(state['errors'])}",
                f"",
                f"Stages completed:",
            ]
            current_idx = STAGE_ORDER.index(state["stage"])
            for stage in STAGE_ORDER[:current_idx]:
                lines.append(f"  ✓ {stage.upper()}")
            lines.append(f"  → {state['stage'].upper()} (current)")
            for stage in STAGE_ORDER[current_idx + 1:]:
                lines.append(f"    {stage.upper()}")

            if state["errors"]:
                lines += ["", "Errors:"]
                for err in state["errors"]:
                    lines.append(f"  [{err['stage']}] {err['error']}")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool '{name}' failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
