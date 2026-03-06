# Tutorial 5: Testing MCP Servers

**Time**: 60 minutes
**Difficulty**: Intermediate
**Prerequisites**: Tutorials 1-4

## What You'll Learn

- Why testing MCP servers requires a different approach than typical Python testing
- How to load non-package server modules in pytest
- Writing sync and async tests for server business logic
- Using fixtures for isolation and reusability
- Mocking external dependencies (HTTP, file system, databases)
- What to test — and what not to

---

## The Testing Challenge

MCP servers are standalone scripts, not installable packages. You can't do:

```python
from examples.data_analysis.server import DataAnalyzer  # ❌ won't work
```

The `examples/` directories have no `__init__.py`, so Python doesn't treat them as packages. You need a different strategy.

### The Solution: `importlib`

Python's `importlib` lets you load any `.py` file by path and register it as a named module:

```python
import importlib.util
import sys
from pathlib import Path

def load_example_module(example_dir: str, alias: str):
    """Load examples/<example_dir>/server.py as a uniquely named module."""
    path = Path(__file__).parent.parent / "examples" / example_dir / "server.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod
```

The `alias` must be unique per server to avoid `sys.modules` collisions when loading multiple servers in the same test run.

---

## Setting Up the Test Environment

### 1. Add test dependencies

In `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    ...
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

`asyncio_mode = "auto"` means async test functions run automatically without needing `@pytest.mark.asyncio` decorators.

Install with:

```bash
uv sync --extra dev
```

### 2. Create `tests/conftest.py`

`conftest.py` is pytest's shared fixture file. Put module-loading fixtures here so every test file can use them:

```python
# tests/conftest.py
import importlib.util
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent

def load_example_module(example_dir: str, alias: str):
    path = REPO_ROOT / "examples" / example_dir / "server.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod

@pytest.fixture(scope="session")
def data_analysis_mod():
    return load_example_module("data-analysis", "data_analysis_server")

@pytest.fixture(scope="session")
def task_manager_mod():
    return load_example_module("task-manager", "task_manager_server")
```

`scope="session"` loads each module once for the entire test run — server modules are expensive to load and have no per-test state at load time.

---

## Writing Your First Test

Once you have a module fixture, testing is standard pytest:

```python
# tests/test_data_analyzer.py

def test_list_files_returns_csv_and_json(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    files = analyzer.list_files()
    extensions = {f["type"] for f in files}
    assert ".csv" in extensions
    assert ".json" in extensions

def test_get_summary_record_count(data_analysis_mod, sample_data_dir):
    analyzer = data_analysis_mod.DataAnalyzer(data_dir=str(sample_data_dir))
    summary = analyzer.get_summary("sales.csv")
    assert summary["num_records"] == 5
```

Notice: you're testing `DataAnalyzer` directly — not going through the MCP tool handler. This is intentional. See [What to Test](#what-to-test).

---

## Testing Async Functions

MCP stage functions are often `async`. With `asyncio_mode = "auto"`, just declare your test `async`:

```python
# tests/test_pipeline.py

async def test_ingest_loads_correct_record_count(pipeline_mod, sample_csv):
    state = pipeline_mod.make_state("test-session", str(sample_csv))
    state = await pipeline_mod._ingest(state)

    assert state["results"]["ingestion"]["total_records"] == 5
    assert state["stage"] == "validation"  # stage advanced automatically
```

No `asyncio.run()`, no `@pytest.mark.asyncio` — pytest handles the event loop.

---

## Fixtures and Isolation

### Use `tmp_path` for file-based tests

pytest's built-in `tmp_path` fixture gives each test a unique temporary directory that's cleaned up automatically:

```python
@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Write sample rows to a temp CSV."""
    csv_path = tmp_path / "transactions.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ROWS[0].keys())
        writer.writeheader()
        writer.writerows(ROWS)
    return csv_path
```

### Use `monkeypatch` to redirect file paths

When a server uses a hardcoded path (like `TASKS_FILE`), patch it per-test:

```python
def test_create_task_persists_to_json(task_manager_mod, tmp_path, monkeypatch):
    monkeypatch.setattr(task_manager_mod, "TASKS_FILE", tmp_path / "tasks.json")
    manager = task_manager_mod.TaskManager()
    manager.create_task("Write tests", "high")
    assert (tmp_path / "tasks.json").exists()
```

### Scope your fixtures appropriately

| Scope | When to use |
|-------|-------------|
| `session` | Expensive setup shared across all tests (module loading, DB connection) |
| `function` (default) | Anything that mutates state — files, in-memory stores, DB rows |

---

## Mocking External Dependencies

### HTTP calls

Use `unittest.mock.AsyncMock` to replace the httpx client — no real network calls needed:

```python
from unittest.mock import AsyncMock, MagicMock
import httpx

@pytest.fixture()
def api_client(web_api_mod):
    client = web_api_mod.APIClient(
        base_url="http://test.local",
        api_key="test-key",
        max_retries=1,  # fail fast in tests, no sleep
    )
    # High rate limit so tests never block
    client.rate_limiter = web_api_mod.RateLimiter(max_calls=1000, period=60)
    return client

def mock_response(data: dict):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp

async def test_get_returns_parsed_json(api_client):
    api_client.client.request = AsyncMock(
        return_value=mock_response({"data": [{"id": "PROD001"}]})
    )
    result = await api_client.get("/api/products")
    assert result["data"][0]["id"] == "PROD001"
```

### Skipping sleeps in retry tests

Retry logic uses `asyncio.sleep` for backoff. Mock it so tests don't actually wait:

```python
async def test_retries_three_times(api_client, monkeypatch):
    api_client.max_retries = 3
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    api_client.client.request = AsyncMock(return_value=mock_error_response(503))
    with pytest.raises(Exception):
        await api_client.get("/api/flaky")

    assert api_client.client.request.call_count == 3
```

### Database

Use a real SQLite in-memory or `tmp_path` database — no mocking needed:

```python
@pytest.fixture()
def sqlite_db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    conn.executemany("INSERT INTO products VALUES (?, ?, ?)", [(1, "Widget", 9.99)])
    conn.commit()
    conn.close()
    return db_path
```

---

## What to Test

### Test business logic directly

Focus on the classes and functions that do the actual work:

```
✅ DataAnalyzer.aggregate()
✅ TaskManager.create_task()
✅ DataPipeline._validate()
✅ APIClient.request()
✅ RateLimiter.acquire()
```

### Skip the MCP tool handlers

The `@server.call_tool()` handlers are thin wrappers — they parse arguments, call business logic, and format the result as `TextContent`. Testing them requires mocking the MCP framework itself, which adds complexity for little gain.

```
❌ Testing that call_tool("aggregate_data", {...}) returns TextContent
✅ Testing that DataAnalyzer.aggregate(...) returns the right dict
```

If the business logic is correct and the handler just calls it, the handler is correct.

### Test edge cases, not just the happy path

```python
# Happy path
async def test_ingest_loads_records(pipeline_mod, sample_csv): ...

# Edge cases
async def test_ingest_file_not_found_raises(pipeline_mod): ...
async def test_ingest_empty_file_raises(pipeline_mod, tmp_path): ...
async def test_process_no_completed_raises(pipeline_mod, tmp_path): ...
```

---

## Running the Suite

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest tests/ -v

# Run a single file
uv run pytest tests/test_pipeline.py -v

# Run a single test
uv run pytest tests/test_pipeline.py::test_ingest_loads_correct_record_count -v

# Stop on first failure
uv run pytest tests/ -x
```

The full suite for this project runs in under 2 seconds:

```
tests/test_api_client.py      13 passed
tests/test_data_analyzer.py   16 passed
tests/test_database.py        13 passed
tests/test_pipeline.py        22 passed
tests/test_rate_limiter.py     4 passed
tests/test_task_manager.py    12 passed
================================ 80 passed in 1.8s
```

---

## Key Takeaways

**`importlib` unlocks standalone scripts** — no need to restructure your project into packages just to test it.

**Test business logic, not the MCP layer** — keep tests focused on the functions that do the real work.

**`tmp_path` + `monkeypatch` = clean isolation** — never let tests share mutable state or write to real directories.

**`asyncio_mode = "auto"` removes boilerplate** — async tests just work without decorators.

**Mock at the boundary** — replace HTTP clients and external APIs, but use real SQLite databases and real file I/O wherever practical.

---

## What's Next: Phase 2

This tutorial series has covered the fundamentals of building MCP servers. The natural next step is **multi-agent systems** — architectures where multiple MCP servers collaborate, pass context between each other, and are orchestrated by an agent that can reason across tools from different domains.

That work lives in a separate repository. The patterns you've learned here — tool schemas, state management, async handlers, testing — carry directly into that world.
