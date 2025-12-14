# Tutorial 2: Your First MCP Server

**Time**: 45 minutes  
**Difficulty**: Beginner  
**Prerequisites**: Tutorial 1

## What We're Building

A simple **Task Manager MCP Server** that lets Claude:

- Create tasks
- List all tasks
- Mark tasks as complete
- Delete tasks

This demonstrates all core MCP concepts in a practical way.

## Setup

### Step 1: Create Project Structure

```bash
cd examples/task-manager
mkdir task-manager-mcp
cd task-manager-mcp
```

### Step 2: Initialize Python Project

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mcp
```

### Step 3: Create Main Server File

Create `server.py`:

```python
#!/usr/bin/env python3
"""
Simple Task Manager MCP Server
Demonstrates basic MCP server implementation
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# Storage file
TASKS_FILE = Path("tasks.json")

class TaskManager:
    """Simple task management with JSON storage"""
    
    def __init__(self):
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> list:
        """Load tasks from JSON file"""
        if TASKS_FILE.exists():
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_tasks(self):
        """Save tasks to JSON file"""
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def create_task(self, title: str, description: str = "") -> dict:
        """Create a new task"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def list_tasks(self, show_completed: bool = True) -> list:
        """List all tasks"""
        if show_completed:
            return self.tasks
        return [t for t in self.tasks if not t["completed"]]
    
    def complete_task(self, task_id: int) -> dict:
        """Mark a task as complete"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                return task
        raise ValueError(f"Task {task_id} not found")
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) < initial_len:
            self._save_tasks()
            return True
        return False

# Initialize server and task manager
server = Server("task-manager")
task_manager = TaskManager()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Define available tools"""
    return [
        Tool(
            name="create_task",
            description="Create a new task with title and optional description",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional)"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks or only incomplete tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_completed": {
                        "type": "boolean",
                        "description": "Include completed tasks (default: true)"
                    }
                }
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as complete by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to complete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "create_task":
            task = task_manager.create_task(
                arguments["title"],
                arguments.get("description", "")
            )
            return [TextContent(
                type="text",
                text=f"Created task #{task['id']}: {task['title']}"
            )]
        
        elif name == "list_tasks":
            show_completed = arguments.get("show_completed", True)
            tasks = task_manager.list_tasks(show_completed)
            
            if not tasks:
                message = "No tasks found"
            else:
                message = f"Found {len(tasks)} task(s):\n\n"
                for task in tasks:
                    status = "✓" if task["completed"] else "○"
                    message += f"{status} #{task['id']}: {task['title']}\n"
                    if task["description"]:
                        message += f"   {task['description']}\n"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "complete_task":
            task = task_manager.complete_task(arguments["task_id"])
            return [TextContent(
                type="text",
                text=f"Completed task #{task['id']}: {task['title']}"
            )]
        
        elif name == "delete_task":
            success = task_manager.delete_task(arguments["task_id"])
            if success:
                message = f"Deleted task #{arguments['task_id']}"
            else:
                message = f"Task #{arguments['task_id']} not found"
            return [TextContent(type="text", text=message)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Understanding the Code

### 1. **Storage Layer** (`TaskManager` class)

Handles all data operations - create, read, update, delete tasks. Uses simple JSON file storage.

### 2. **Tool Definitions** (`list_tools()`)

Tells Claude what functions are available and what parameters they accept. This is like an API specification.

### 3. **Tool Execution** (`call_tool()`)

Handles the actual work when Claude calls a tool. Validates inputs and returns results.

### 4. **Server Setup**

Connects everything and handles communication with Claude.

## Configuration

Create `claude_desktop_config.json` in Claude Desktop's config directory:

**Mac/Linux**: `~/Library/Application Support/Claude/`  
**Windows**: `%APPDATA%\Claude\`

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["/path/to/your/task-manager-mcp/server.py"]
    }
  }
}
```

## Testing Your Server

### Step 1: Restart Claude Desktop

After adding the configuration, restart Claude Desktop completely.

### Step 2: Verify Connection

In Claude, type:

```plaintext
Do you have access to task management tools?
```

Claude should confirm it can see the tools.

### Step 3: Test Basic Operations

Try these prompts:

```plaintext
Create a task called "Buy groceries" with description "Milk, eggs, bread"
```

```plaintext
List all my tasks
```

```plaintext
Complete task #1
```

```plaintext
Create three tasks: "Email team", "Review PR", and "Update docs"
```

```plaintext
Show me only incomplete tasks
```

## Debugging

### Server Not Appearing?

1. Check the config file path is correct
2. Verify Python path in config
3. Look at Claude Desktop logs:
   - Mac: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### Tool Calls Failing?

1. Check the server's JSON output format
2. Verify your Python environment is activated
3. Add print statements for debugging:

```python
import sys
print(f"Tool called: {name}", file=sys.stderr)
print(f"Arguments: {arguments}", file=sys.stderr)
```

## Extending Your Server

Try these enhancements:

### Add Priority Levels

```python
def create_task(self, title: str, priority: str = "medium"):
    task = {
        # ... existing fields ...
        "priority": priority  # low, medium, high
    }
```

### Add Due Dates

```python
from datetime import datetime, timedelta

def create_task(self, title: str, due_date: str = None):
    task = {
        # ... existing fields ...
        "due_date": due_date
    }
```

### Add Search

```python
def search_tasks(self, query: str) -> list:
    return [t for t in self.tasks 
            if query.lower() in t["title"].lower() 
            or query.lower() in t.get("description", "").lower()]
```

## Common Patterns

### Pattern 1: Validation

Always validate inputs before processing:

```python
if not title or len(title) < 3:
    raise ValueError("Title must be at least 3 characters")
```

### Pattern 2: Error Handling

Return helpful error messages:

```python
try:
    task = task_manager.complete_task(task_id)
except ValueError as e:
    return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### Pattern 3: Rich Responses

Format output for readability:

```python
message = "📋 Your Tasks:\n\n"
for task in tasks:
    status = "✅" if task["completed"] else "⭕"
    message += f"{status} {task['title']}\n"
```

## Exercise: Build Your Own

Now try building an MCP server for:

### Option 1: Simple Notes

- Create note with title and content
- List all notes
- Search notes by keyword
- Delete notes

### Option 2: Weather Logger

- Log weather observations
- List recent observations
- Get statistics (average temp, etc.)

### Option 3: Habit Tracker

- Log habit completion
- View streak
- Get completion percentage

## What's Next?

In **Tutorial 3**, you'll learn agentic patterns - how to design prompts and workflows that let Claude use tools effectively to accomplish complex tasks.

Continue to [Tutorial 3: Agentic Patterns](03-agentic-patterns.md) →

## Key Takeaways

- ✅ MCP servers are just Python/Node.js programs
- ✅ Tools are functions with clear descriptions
- ✅ JSON schemas define input parameters
- ✅ Servers communicate via stdio
- ✅ Start simple, then extend

## Troubleshooting Checklist

- [ ] Config file in correct location
- [ ] Python path is absolute
- [ ] Server file is executable
- [ ] Claude Desktop fully restarted
- [ ] No syntax errors in server.py
- [ ] Dependencies installed in venv
