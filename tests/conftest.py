"""
Shared fixtures and module-loading helpers for the test suite.

Each MCP server lives in examples/<name>/server.py and is not a proper package,
so we load them via importlib with unique module names to avoid conflicts.
"""

import csv
import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


def load_example_module(example_dir: str, alias: str):
    """Load examples/<example_dir>/server.py as a uniquely named module."""
    path = REPO_ROOT / "examples" / example_dir / "server.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Module fixtures (session-scoped — loaded once per test run)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def data_analysis_mod():
    return load_example_module("data-analysis", "data_analysis_server")


@pytest.fixture(scope="session")
def task_manager_mod():
    return load_example_module("task-manager", "task_manager_server")


@pytest.fixture(scope="session")
def database_mod():
    return load_example_module("database", "database_server")


@pytest.fixture(scope="session")
def web_api_mod():
    return load_example_module("web-api", "web_api_server")


@pytest.fixture(scope="session")
def pipeline_mod():
    return load_example_module("data-pipeline", "data_pipeline_server")


# ---------------------------------------------------------------------------
# Data fixtures
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    {"name": "Alice", "region": "North", "amount": "100.0", "status": "completed"},
    {"name": "Bob", "region": "South", "amount": "200.0", "status": "pending"},
    {"name": "Carol", "region": "North", "amount": "150.0", "status": "completed"},
    {"name": "Dave", "region": "East", "amount": "50.0", "status": "pending"},
    {"name": "Eve", "region": "South", "amount": "300.0", "status": "completed"},
]


@pytest.fixture()
def sample_data_dir(tmp_path: Path) -> Path:
    """Create a temp directory with sample CSV and JSON files."""
    csv_file = tmp_path / "sales.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_ROWS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_ROWS)

    import json

    json_file = tmp_path / "sales.json"
    json_file.write_text(json.dumps(SAMPLE_ROWS, indent=2))

    return tmp_path


@pytest.fixture()
def sqlite_db_path(tmp_path: Path) -> Path:
    """Create a minimal SQLite database with a products table."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            stock INTEGER
        )
        """
    )
    conn.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [
            (1, "Widget", 9.99, 100),
            (2, "Gadget", 29.99, 0),
            (3, "Doohickey", 4.99, 50),
        ],
    )
    conn.commit()
    conn.close()
    return db_path
