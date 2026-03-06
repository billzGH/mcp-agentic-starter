#!/usr/bin/env python3
"""
Task Manager MCP Server
Demonstrates basic MCP server implementation with persistent JSON storage.
This is the completed example from Tutorial 2.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent

# Store tasks next to this file so the server works from any working directory
TASKS_FILE = Path(__file__).parent / "tasks.json"

server = Server("task-manager")


class TaskManager:
    """Simple task management with JSON file storage"""

    def __init__(self):
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> list:
        if TASKS_FILE.exists():
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def create_task(self, title: str, description: str = "") -> dict:
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.append(task)
        self._save_tasks()
        return task

    def list_tasks(self, show_completed: bool = True) -> list:
        if show_completed:
            return self.tasks
        return [t for t in self.tasks if not t["completed"]]

    def complete_task(self, task_id: int) -> dict:
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                return task
        raise ValueError(f"Task {task_id} not found")

    def delete_task(self, task_id: int) -> bool:
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) < initial_len:
            self._save_tasks()
            return True
        return False


task_manager = TaskManager()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="create_task",
            description="Create a new task with title and optional description",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {
                        "type": "string",
                        "description": "Optional task description",
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="list_tasks",
            description="List all tasks, or only incomplete tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_completed": {
                        "type": "boolean",
                        "description": "Include completed tasks (default: true)",
                    }
                },
            },
        ),
        Tool(
            name="complete_task",
            description="Mark a task as complete by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to complete",
                    }
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="delete_task",
            description="Delete a task by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete",
                    }
                },
                "required": ["task_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    try:
        if name == "create_task":
            task = task_manager.create_task(
                arguments["title"], arguments.get("description", "")
            )
            return [TextContent(type="text", text=f"Created task #{task['id']}: {task['title']}")]

        elif name == "list_tasks":
            show_completed = arguments.get("show_completed", True)
            tasks = task_manager.list_tasks(show_completed)

            if not tasks:
                message = "No tasks found."
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
            return [TextContent(type="text", text=f"Completed task #{task['id']}: {task['title']}")]

        elif name == "delete_task":
            success = task_manager.delete_task(arguments["task_id"])
            message = (
                f"Deleted task #{arguments['task_id']}"
                if success
                else f"Task #{arguments['task_id']} not found"
            )
            return [TextContent(type="text", text=message)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
