# Task Manager MCP Server

A simple MCP server for managing tasks with persistent JSON storage. This is the completed example built in [Tutorial 2: Your First MCP Server](../../tutorials/02-first-server.md).

## Features

- Create tasks with title and optional description
- List all tasks or filter to incomplete only
- Mark tasks as complete
- Delete tasks
- Persistent storage in `tasks.json` (survives server restarts)

## Installation

```bash
# From the repo root
uv sync

# Test the server runs
uv run examples/task-manager/server.py
```

## Configuration

Add to your Claude Desktop config:

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/examples/task-manager",
        "server.py"
      ]
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\absolute\\path\\to\\examples\\task-manager",
        "server.py"
      ]
    }
  }
}
```

After saving the config, restart Claude Desktop completely.

## Example Prompts

```plaintext
Create a task called "Review Q4 report"
```

```plaintext
Create three tasks: "Email team", "Review PR", and "Update docs"
```

```plaintext
List all my tasks
```

```plaintext
Show me only incomplete tasks
```

```plaintext
Complete task #1
```

```plaintext
Delete task #3
```

## How It Works

Tasks are stored in `tasks.json` in the same directory as `server.py`. The file is created automatically on first use and persists across server restarts.

Each task has:
- `id` — auto-incremented integer
- `title` — required task name
- `description` — optional details
- `completed` — boolean status
- `created_at` — ISO timestamp
- `completed_at` — ISO timestamp (set when completed)

## Available Tools

| Tool | Description |
|---|---|
| `create_task` | Create a task with title and optional description |
| `list_tasks` | List tasks; pass `show_completed: false` to filter |
| `complete_task` | Mark a task done by its ID |
| `delete_task` | Remove a task by its ID |

## Extending This Server

Good next steps after following Tutorial 2:

- **Add priorities** — `low`, `medium`, `high` field on each task
- **Add due dates** — store and surface overdue tasks
- **Add search** — filter tasks by keyword in title/description
- **Add tags** — categorize tasks for better organization

See [Tutorial 2](../../tutorials/02-first-server.md) for step-by-step guidance on each extension.
