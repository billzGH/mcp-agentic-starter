#!/usr/bin/env python3
"""
Simple File System MCP Server
Allows Claude to read, write, and search files in a designated directory
"""

import asyncio
import os
from pathlib import Path
from typing import Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure safe working directory
WORK_DIR = Path.home() / "Documents" / "claude-workspace"
WORK_DIR.mkdir(parents=True, exist_ok=True)

server = Server("filesystem")

def is_safe_path(path: str) -> bool:
    """Check if path is within allowed directory"""
    try:
        resolved = (WORK_DIR / path).resolve()
        return resolved.is_relative_to(WORK_DIR)
    except (ValueError, RuntimeError):
        return False

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Define available tools"""
    return [
        Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file (relative to workspace)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file (creates if doesn't exist)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file (relative to workspace)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_files",
            description="List files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (relative to workspace, default: root)",
                        "default": "."
                    }
                }
            }
        ),
        Tool(
            name="search_files",
            description="Search for files by name or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (filename or content)"
                    },
                    "search_content": {
                        "type": "boolean",
                        "description": "Search file contents (default: false)",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file (relative to workspace)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_workspace_info",
            description="Get information about the workspace directory",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "read_file":
            path = arguments["path"]
            if not is_safe_path(path):
                return [TextContent(type="text", text="Error: Path outside workspace")]
            
            file_path = WORK_DIR / path
            if not file_path.exists():
                return [TextContent(type="text", text=f"Error: File not found: {path}")]
            
            content = file_path.read_text()
            return [TextContent(type="text", text=content)]
        
        elif name == "write_file":
            path = arguments["path"]
            content = arguments["content"]
            
            if not is_safe_path(path):
                return [TextContent(type="text", text="Error: Path outside workspace")]
            
            file_path = WORK_DIR / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
            return [TextContent(type="text", text=f"✓ Wrote to {path}")]
        
        elif name == "list_files":
            path = arguments.get("path", ".")
            if not is_safe_path(path):
                return [TextContent(type="text", text="Error: Path outside workspace")]
            
            dir_path = WORK_DIR / path
            if not dir_path.exists():
                return [TextContent(type="text", text=f"Error: Directory not found: {path}")]
            
            files = []
            dirs = []
            for item in sorted(dir_path.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    files.append(f"  📄 {item.name} ({size} bytes)")
                else:
                    dirs.append(f"  📁 {item.name}/")
            
            result = f"Contents of {path}:\n\n"
            if dirs:
                result += "\n".join(dirs) + "\n"
            if files:
                result += "\n".join(files)
            if not dirs and not files:
                result += "(empty directory)"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "search_files":
            query = arguments["query"].lower()
            search_content = arguments.get("search_content", False)
            
            matches = []
            for file_path in WORK_DIR.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Search filename
                if query in file_path.name.lower():
                    rel_path = file_path.relative_to(WORK_DIR)
                    matches.append(f"📄 {rel_path} (filename match)")
                    continue
                
                # Search content if requested
                if search_content:
                    try:
                        content = file_path.read_text()
                        if query in content.lower():
                            rel_path = file_path.relative_to(WORK_DIR)
                            matches.append(f"📄 {rel_path} (content match)")
                    except (UnicodeDecodeError, PermissionError):
                        pass
            
            if matches:
                result = f"Found {len(matches)} matches for '{query}':\n\n"
                result += "\n".join(matches[:20])
                if len(matches) > 20:
                    result += f"\n\n(showing first 20 of {len(matches)} matches)"
            else:
                result = f"No matches found for '{query}'"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "delete_file":
            path = arguments["path"]
            if not is_safe_path(path):
                return [TextContent(type="text", text="Error: Path outside workspace")]
            
            file_path = WORK_DIR / path
            if not file_path.exists():
                return [TextContent(type="text", text=f"Error: File not found: {path}")]
            
            file_path.unlink()
            return [TextContent(type="text", text=f"✓ Deleted {path}")]
        
        elif name == "get_workspace_info":
            total_files = sum(1 for _ in WORK_DIR.rglob("*") if _.is_file())
            total_dirs = sum(1 for _ in WORK_DIR.rglob("*") if _.is_dir())
            
            info = f"""
📁 Workspace Information:

Location: {WORK_DIR}
Files: {total_files}
Directories: {total_dirs}

You can:
• Read and write files
• List directory contents
• Search for files
• Delete files

All paths are relative to the workspace root.
"""
            return [TextContent(type="text", text=info)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())