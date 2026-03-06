"""Tests for examples/data-pipeline/server.py."""

import csv
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Sample CSV data matching the pipeline's expected schema
# ---------------------------------------------------------------------------

PIPELINE_ROWS = [
    {
        "transaction_id": "T001", "transaction_date": "2025-01-15",
        "total_amount": "100.00", "status": "Completed",
        "payment_method": "Credit Card", "customer_id": "C001",
        "product_id": "P001", "quantity": "2", "discount": "0",
    },
    {
        "transaction_id": "T002", "transaction_date": "2025-01-20",
        "total_amount": "200.00", "status": "Completed",
        "payment_method": "PayPal", "customer_id": "C002",
        "product_id": "P002", "quantity": "1", "discount": "5",
    },
    {
        "transaction_id": "T003", "transaction_date": "2025-02-10",
        "total_amount": "150.00", "status": "Pending",
        "payment_method": "Credit Card", "customer_id": "C003",
        "product_id": "P001", "quantity": "1", "discount": "0",
    },
    {
        "transaction_id": "T004", "transaction_date": "2025-02-15",
        "total_amount": "300.00", "status": "Completed",
        "payment_method": "Credit Card", "customer_id": "C001",
        "product_id": "P003", "quantity": "3", "discount": "10",
    },
    {
        "transaction_id": "T005", "transaction_date": "2025-03-01",
        "total_amount": "75.00", "status": "Cancelled",
        "payment_method": "Bank Transfer", "customer_id": "C004",
        "product_id": "P001", "quantity": "1", "discount": "0",
    },
]


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Write PIPELINE_ROWS to a temp CSV and return its absolute path."""
    csv_path = tmp_path / "transactions.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PIPELINE_ROWS[0].keys())
        writer.writeheader()
        writer.writerows(PIPELINE_ROWS)
    return csv_path


# ---------------------------------------------------------------------------
# make_state
# ---------------------------------------------------------------------------


def test_make_state_initial_values(pipeline_mod):
    state = pipeline_mod.make_state("test-session", "datasets/sales/transactions.csv")
    assert state["session_id"] == "test-session"
    assert state["input_file"] == "datasets/sales/transactions.csv"
    assert state["stage"] == "ingestion"
    assert state["records_processed"] == 0
    assert state["errors"] == []
    assert state["results"] == {}


# ---------------------------------------------------------------------------
# next_stage
# ---------------------------------------------------------------------------


def test_next_stage_advances_from_ingestion(pipeline_mod):
    state = pipeline_mod.make_state("s", "f")
    pipeline_mod.next_stage(state)
    assert state["stage"] == "validation"


def test_next_stage_full_progression(pipeline_mod):
    state = pipeline_mod.make_state("s", "f")
    expected = ["validation", "processing", "analysis", "reporting", "complete"]
    for expected_stage in expected:
        pipeline_mod.next_stage(state)
        assert state["stage"] == expected_stage


# ---------------------------------------------------------------------------
# record_error
# ---------------------------------------------------------------------------


def test_record_error_appends_to_list(pipeline_mod):
    state = pipeline_mod.make_state("s", "f")
    pipeline_mod.record_error(state, "something went wrong")
    assert len(state["errors"]) == 1
    assert state["errors"][0]["stage"] == "ingestion"
    assert state["errors"][0]["error"] == "something went wrong"
    assert "timestamp" in state["errors"][0]


def test_record_error_multiple(pipeline_mod):
    state = pipeline_mod.make_state("s", "f")
    pipeline_mod.record_error(state, "err1")
    pipeline_mod.record_error(state, "err2")
    assert len(state["errors"]) == 2


# ---------------------------------------------------------------------------
# resolve_path
# ---------------------------------------------------------------------------


def test_resolve_path_absolute_passes_through(pipeline_mod):
    p = Path("/tmp/some/file.csv")
    assert pipeline_mod.resolve_path(str(p)) == p


def test_resolve_path_relative_joins_repo_root(pipeline_mod):
    result = pipeline_mod.resolve_path("datasets/sales/transactions.csv")
    assert result == pipeline_mod.REPO_ROOT / "datasets/sales/transactions.csv"


# ---------------------------------------------------------------------------
# _ingest
# ---------------------------------------------------------------------------


async def test_ingest_loads_correct_record_count(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)

    ingestion = state["results"]["ingestion"]
    assert ingestion["total_records"] == 5
    assert state["records_processed"] == 5
    assert state["stage"] == "validation"


async def test_ingest_detects_columns(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)

    columns = state["results"]["ingestion"]["columns"]
    assert "transaction_id" in columns
    assert "total_amount" in columns
    assert "status" in columns


async def test_ingest_file_not_found_raises(pipeline_mod):
    state = pipeline_mod.make_state("s", "/nonexistent/path/file.csv")
    with pytest.raises(FileNotFoundError):
        await pipeline_mod._ingest(state)


async def test_ingest_empty_file_raises(pipeline_mod, tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("")
    state = pipeline_mod.make_state("s", str(empty_csv))
    with pytest.raises(ValueError, match="empty"):
        await pipeline_mod._ingest(state)


# ---------------------------------------------------------------------------
# _validate
# ---------------------------------------------------------------------------


async def test_validate_clean_data_high_quality_score(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)

    validation = state["results"]["validation"]
    assert validation["quality_score"] > 90
    assert validation["total_records"] == 5
    assert state["stage"] == "processing"


async def test_validate_flags_invalid_amount(pipeline_mod, tmp_path):
    rows = [r.copy() for r in PIPELINE_ROWS]
    rows[0]["total_amount"] = "not-a-number"

    csv_path = tmp_path / "bad_amount.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    state = pipeline_mod.make_state("s", str(csv_path))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)

    assert state["results"]["validation"]["invalid_amounts"] >= 1


async def test_validate_missing_required_column(pipeline_mod, tmp_path):
    # Drop the 'status' column
    rows = [{k: v for k, v in r.items() if k != "status"} for r in PIPELINE_ROWS]

    csv_path = tmp_path / "no_status.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    state = pipeline_mod.make_state("s", str(csv_path))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)

    issues = state["results"]["validation"]["issues"]
    assert any("status" in issue for issue in issues)


# ---------------------------------------------------------------------------
# _process
# ---------------------------------------------------------------------------


async def test_process_keeps_only_completed(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    state = await pipeline_mod._process(state)

    processing = state["results"]["processing"]
    # 3 Completed rows in PIPELINE_ROWS
    assert processing["completed_records"] == 3
    assert processing["skipped_records"] == 2
    assert state["stage"] == "analysis"


async def test_process_extracts_year_month(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    state = await pipeline_mod._process(state)

    processed_rows = state["results"]["_processed_rows"]
    year_months = {r["_year_month"] for r in processed_rows}
    assert "2025-01" in year_months
    assert "2025-02" in year_months


async def test_process_no_completed_raises(pipeline_mod, tmp_path):
    rows = [r.copy() for r in PIPELINE_ROWS]
    for r in rows:
        r["status"] = "Pending"

    csv_path = tmp_path / "all_pending.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    state = pipeline_mod.make_state("s", str(csv_path))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    with pytest.raises(ValueError, match="No completed transactions"):
        await pipeline_mod._process(state)


# ---------------------------------------------------------------------------
# _analyze
# ---------------------------------------------------------------------------


async def test_analyze_computes_total_revenue(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    state = await pipeline_mod._process(state)
    state = await pipeline_mod._analyze(state)

    analysis = state["results"]["analysis"]
    # Completed rows: 100 + 200 + 300 = 600
    assert analysis["total_revenue"] == pytest.approx(600.0, rel=1e-3)
    assert analysis["total_transactions"] == 3


async def test_analyze_payment_method_breakdown(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    state = await pipeline_mod._process(state)
    state = await pipeline_mod._analyze(state)

    by_payment = state["results"]["analysis"]["revenue_by_payment_method"]
    # Credit Card: T001 (100) + T004 (300) = 400; PayPal: T002 (200)
    assert by_payment["Credit Card"] == pytest.approx(400.0, rel=1e-3)
    assert by_payment["PayPal"] == pytest.approx(200.0, rel=1e-3)


async def test_analyze_monthly_trend_keys(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("s", str(sample_csv))
    state = await pipeline_mod._ingest(state)
    state = await pipeline_mod._validate(state)
    state = await pipeline_mod._process(state)
    state = await pipeline_mod._analyze(state)

    monthly = state["results"]["analysis"]["monthly_revenue_trend"]
    assert "2025-01" in monthly
    assert "2025-02" in monthly


# ---------------------------------------------------------------------------
# DataPipeline.save_state / load_state
# ---------------------------------------------------------------------------


def test_save_and_load_state_roundtrip(pipeline_mod, tmp_path):
    dp = pipeline_mod.DataPipeline.__new__(pipeline_mod.DataPipeline)
    dp.state_dir = tmp_path

    state = pipeline_mod.make_state("roundtrip-test", "datasets/sales/transactions.csv")
    state["stage"] = "analysis"
    state["records_processed"] = 42

    dp.save_state(state)
    loaded = dp.load_state("roundtrip-test")

    assert loaded["session_id"] == "roundtrip-test"
    assert loaded["stage"] == "analysis"
    assert loaded["records_processed"] == 42


def test_load_state_missing_session_raises(pipeline_mod, tmp_path):
    dp = pipeline_mod.DataPipeline.__new__(pipeline_mod.DataPipeline)
    dp.state_dir = tmp_path

    with pytest.raises(ValueError, match="No pipeline session found"):
        dp.load_state("ghost-session")
