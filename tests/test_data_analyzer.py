"""Tests for examples/data-analysis/server.py — DataAnalyzer class."""

import pytest


# ---------------------------------------------------------------------------
# list_files
# ---------------------------------------------------------------------------


def test_list_files_finds_csv_and_json(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    files = analyzer.list_files()
    extensions = {f["type"] for f in files}
    assert ".csv" in extensions
    assert ".json" in extensions


def test_list_files_empty_dir(data_analysis_mod, tmp_path):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(tmp_path))
    assert analyzer.list_files() == []


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------


def test_get_summary_record_count(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    summary = analyzer.get_summary("sales.csv")
    assert summary["num_records"] == 5


def test_get_summary_columns(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    summary = analyzer.get_summary("sales.csv")
    assert set(summary["columns"]) == {"name", "region", "amount", "status"}


def test_get_summary_column_types(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    summary = analyzer.get_summary("sales.csv")
    assert summary["column_types"]["amount"] == "numeric"
    assert summary["column_types"]["name"] == "text"


# ---------------------------------------------------------------------------
# analyze_column
# ---------------------------------------------------------------------------


def test_analyze_column_numeric(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.analyze_column("sales.csv", "amount")
    assert result["type"] == "numeric"
    assert result["min"] == pytest.approx(50.0)
    assert result["max"] == pytest.approx(300.0)
    assert result["mean"] == pytest.approx(160.0)
    assert result["count"] == 5


def test_analyze_column_text(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.analyze_column("sales.csv", "region")
    assert result["type"] == "text"
    assert result["unique_values"] == 3  # North, South, East
    assert result["count"] == 5


def test_analyze_column_most_common(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.analyze_column("sales.csv", "region")
    top_value, top_count = result["most_common"][0]
    # North and South both appear twice; either can be top
    assert top_count == 2


# ---------------------------------------------------------------------------
# filter_data
# ---------------------------------------------------------------------------


def test_filter_equals(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    rows = analyzer.filter_data("sales.csv", [{"column": "status", "operator": "==", "value": "completed"}])
    assert len(rows) == 3
    assert all(r["status"] == "completed" for r in rows)


def test_filter_greater_than(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    rows = analyzer.filter_data("sales.csv", [{"column": "amount", "operator": ">", "value": "100"}])
    assert len(rows) == 3  # 200, 150, 300


def test_filter_contains(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    rows = analyzer.filter_data("sales.csv", [{"column": "region", "operator": "contains", "value": "outh"}])
    assert len(rows) == 2
    assert all("South" in r["region"] for r in rows)


def test_filter_chained(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    rows = analyzer.filter_data(
        "sales.csv",
        [
            {"column": "status", "operator": "==", "value": "completed"},
            {"column": "amount", "operator": ">", "value": "100"},
        ],
    )
    # completed rows: Alice(100), Carol(150), Eve(300) — amount > 100 keeps Carol and Eve
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------


def test_aggregate_sum(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.aggregate("sales.csv", "status", "amount", "sum")
    assert result["results"]["completed"] == pytest.approx(550.0)  # 100+150+300
    assert result["results"]["pending"] == pytest.approx(250.0)  # 200+50


def test_aggregate_avg(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.aggregate("sales.csv", "region", "amount", "avg")
    assert result["results"]["North"] == pytest.approx(125.0)  # (100+150)/2
    assert result["results"]["South"] == pytest.approx(250.0)  # (200+300)/2


def test_aggregate_count(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.aggregate("sales.csv", "status", "amount", "count")
    assert result["results"]["completed"] == 3
    assert result["results"]["pending"] == 2


def test_aggregate_metadata(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    result = analyzer.aggregate("sales.csv", "status", "amount", "sum")
    assert result["grouped_by"] == "status"
    assert result["aggregated"] == "amount"
    assert result["function"] == "sum"
