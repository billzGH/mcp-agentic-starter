# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (uses UV)
uv sync

# Install optional dependency groups
uv sync --extra postgres   # PostgreSQL support (asyncpg)
uv sync --extra api        # Mock API server (fastapi, uvicorn)
uv sync --extra viz        # Visualization (matplotlib, seaborn)
uv sync --extra dev        # Dev tools (pytest, black, ruff)
uv sync --all-extras       # All of the above

# Run an MCP server directly (for testing or Claude Desktop integration)
uv run python examples/file-system/server.py
uv run python examples/data-analysis/server.py
uv run python examples/database/server.py
uv run python examples/web-api/server.py
uv run python examples/task-manager/server.py
uv run python examples/data-pipeline/server.py

# Run the mock API server (required before using the web-api MCP server)
uv run python examples/web-api/mock_api.py

# Generate sample sales data for the data-analysis server
uv run python examples/data-analysis/generate_sales_data.py

# Load sample data into the SQLite database
uv run python examples/database/load_sample_data.py

# Lint and format
uv run ruff check .
uv run black .

# Run tests (requires dev extras)
uv sync --extra dev
uv run pytest tests/ -v          # all 80 tests
uv run pytest tests/test_pipeline.py -v  # single file
```

## Architecture

This repo is a learning kit for building MCP (Model Context Protocol) servers — standalone Python scripts that expose tools to AI agents. It is **not** a traditional application; there is no main entrypoint, web server, or shared library. Each example under `examples/` is an independent, runnable server.

### MCP Server Pattern

All servers follow the same structure:

1. Create a `Server` instance: `server = Server("name")`
2. Register a tool list handler: `@server.list_tools()` returning `List[Tool]` with JSON schemas
3. Register a tool call handler: `@server.call_tool()` dispatching on tool name, returning `List[TextContent]`
4. Run via stdio transport in `main()`:
   ```python
   async with stdio_server() as (read_stream, write_stream):
       await server.run(read_stream, write_stream, server.create_initialization_options())
   ```

All tool calls return `List[TextContent]` and handle exceptions internally, returning error messages as text rather than raising.

### Example Servers

- **file-system/server.py** — Read/write/search files restricted to `~/Documents/claude-workspace`. Uses `is_safe_path()` to prevent path traversal.
- **data-analysis/server.py** — Loads CSV/JSON from `datasets/` and performs statistical analysis. Uses stdlib `statistics`, `csv`, `json` (no pandas dependency at runtime).
- **database/server.py** — Wraps SQLite (default) or PostgreSQL via `DatabaseConnection` class. Configured via env vars: `DB_TYPE`, `DATABASE_URL`, `DB_READ_ONLY` (default: `true`), `DB_MAX_ROWS` (default: `1000`). Defaults to `examples/database/sample_data/sales.db`. Write tools are only registered when `DB_READ_ONLY=false`.
- **web-api/server.py** — Calls a REST API via `APIClient` (httpx) with retry/backoff and in-process rate limiting. Configured via env vars: `API_BASE_URL` (default: `http://localhost:8000`), `API_KEY`, `REQUEST_TIMEOUT`, `MAX_RETRIES`. Requires the mock API server to be running.
- **task-manager/server.py** — Persistent task list backed by `tasks.json` in the server directory. `TASKS_FILE` uses `Path(__file__).parent` so it resolves correctly regardless of working directory.
- **data-pipeline/server.py** — Five-stage pipeline (INGESTION → VALIDATION → PROCESSING → ANALYSIS → REPORTING). State persisted as JSON between tool calls in `pipeline_state/`. Uses plain dicts (not dataclasses) to avoid Enum serialization issues.

### Supporting Files

- **examples/web-api/mock_api.py** — FastAPI server simulating an e-commerce + analytics API on port 8000. Required for testing the web-api MCP server.
- **examples/database/schema.sql** — SQL schema for the sample sales database.
- **datasets/** — Synthetic CSV/JSON data consumed by the data-analysis server.
- **tutorials/** — Markdown learning guides (not executable).
- **prompts/** — Prompt engineering examples for agentic tasks.

### Code Style

- Line length: 100 characters (black + ruff)
- Target: Python 3.10+
- Ruff rules: E, F, I, N, W

### Adding a New MCP Server

New servers belong in `examples/your-server/` and should include `server.py`, `README.md`, and optionally `test_prompts.md`. Follow the existing tool registration pattern and run via stdio transport.

## Contributing

### Pull Requests

Always use the template at `.github/pull_request_template.md` when opening PRs. Use feature branches (`feature/...`) for new functionality and `fix/...` for bug fixes — never commit directly to `main`.

### Claude Desktop Config

`claude_desktop_config.example.json` at the repo root shows how to wire up all servers. Copy it to the Claude Desktop config location and replace `/absolute/path/to` with the actual repo path.
