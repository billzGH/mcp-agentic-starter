#!/usr/bin/env python3
"""
Database MCP Server
Provides Claude with SQL database access (SQLite and PostgreSQL)
"""

import os
import json
import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, Union
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.types import Tool, TextContent

# Optional PostgreSQL support
try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    if TYPE_CHECKING:
        import asyncpg  # type: ignore
    else:
        asyncpg = None  # type: ignore
    POSTGRES_AVAILABLE = False

# Initialize server
server = Server("database")


class DatabaseConnection:
    """Manages database connections for both SQLite and PostgreSQL"""
    
    def __init__(
        self,
        db_type: str = "sqlite",
        connection_string: Optional[str] = None,
        read_only: bool = True,
        max_rows: int = 1000
    ):
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.read_only = read_only
        self.max_rows = max_rows
        self.pool: Optional[Any] = None  # For PostgreSQL connection pool
        
        # Default to SQLite if no connection string provided
        if not connection_string:
            self.db_type = "sqlite"
            # Use sample database in the examples/database directory
            db_path = Path(__file__).parent / "sample_data" / "sales.db"
            self.connection_string = str(db_path)
    
    async def connect(self):
        """Initialize database connection"""
        if self.db_type == "postgresql":
            if not POSTGRES_AVAILABLE or asyncpg is None:
                raise ImportError(
                    "PostgreSQL support requires asyncpg. Install with: uv pip install asyncpg"
                )
            # Create connection pool for PostgreSQL
            self.pool = await asyncpg.create_pool(  # type: ignore
                self.connection_string,
                min_size=1,
                max_size=10,
                command_timeout=30
            )
        # SQLite doesn't need async connection setup
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection (context manager)"""
        if self.db_type == "sqlite":
            assert self.connection_string is not None, "SQLite connection string must be set"
            conn = sqlite3.connect(self.connection_string)
            conn.row_factory = sqlite3.Row  # Return rows as dicts
            try:
                yield conn
            finally:
                conn.close()
        else:  # PostgreSQL
            assert self.pool is not None, "PostgreSQL pool must be initialized"
            async with self.pool.acquire() as conn:  # type: ignore
                yield conn
    
    async def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        # Validate query is SELECT (read-only check)
        query_upper = query.strip().upper()
        if self.read_only and not query_upper.startswith("SELECT"):
            raise ValueError(
                "Only SELECT queries are allowed in read-only mode. "
                "Set read_only=False to enable write operations."
            )
        
        async with self.get_connection() as conn:
            if self.db_type == "sqlite":
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchmany(self.max_rows)
                return [dict(zip(columns, row)) for row in rows]
            
            else:  # PostgreSQL
                if params:
                    rows = await conn.fetch(query, *params)  # type: ignore
                else:
                    rows = await conn.fetch(query)  # type: ignore
                
                # Limit rows
                rows = rows[:self.max_rows]
                return [dict(row) for row in rows]
    
    async def execute_write(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> Dict[str, Any]:
        """Execute an INSERT/UPDATE/DELETE query"""
        if self.read_only:
            raise ValueError(
                "Write operations are disabled in read-only mode. "
                "Set read_only=False to enable write operations."
            )
        
        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT"):
            raise ValueError("Use execute_query for SELECT statements")
        
        async with self.get_connection() as conn:
            if self.db_type == "sqlite":
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                
                return {
                    "rows_affected": cursor.rowcount,
                    "last_row_id": cursor.lastrowid
                }
            
            else:  # PostgreSQL
                if params:
                    result = await conn.execute(query, *params)  # type: ignore
                else:
                    result = await conn.execute(query)  # type: ignore
                
                # Parse result string like "INSERT 0 1" or "UPDATE 3"
                rows_affected = 0
                if result:
                    parts = result.split()
                    if len(parts) >= 2:
                        rows_affected = int(parts[-1])
                
                return {
                    "rows_affected": rows_affected,
                    "result": result
                }
    
    async def list_tables(self) -> List[Dict[str, Any]]:
        """List all tables in the database"""
        if self.db_type == "sqlite":
            query = """
                SELECT name, type 
                FROM sqlite_master 
                WHERE type IN ('table', 'view') 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
        else:  # PostgreSQL
            query = """
                SELECT 
                    table_name as name,
                    table_type as type
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
        
        return await self.execute_query(query)
    
    async def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table"""
        if self.db_type == "sqlite":
            query = f"PRAGMA table_info({table_name})"
            columns = await self.execute_query(query)
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = await self.execute_query(count_query)
            
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": not col["notnull"],
                        "primary_key": bool(col["pk"])
                    }
                    for col in columns
                ],
                "row_count": count_result[0]["count"]
            }
        
        else:  # PostgreSQL
            query = """
                SELECT 
                    column_name as name,
                    data_type as type,
                    is_nullable = 'YES' as nullable,
                    column_default as default_value
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """
            columns = await self.execute_query(query, (table_name,))
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = await self.execute_query(count_query)
            
            # Get primary key info
            pk_query = """
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_name = $1
                AND constraint_name LIKE '%_pkey'
            """
            pk_result = await self.execute_query(pk_query, (table_name,))
            pk_columns = {row["column_name"] for row in pk_result}  # type: ignore
            
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": col["nullable"],
                        "primary_key": col["name"] in pk_columns
                    }
                    for col in columns
                ],
                "row_count": count_result[0]["count"]
            }
    
    async def get_sample_data(
        self,
        table_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get sample rows from a table"""
        limit = min(limit, self.max_rows)
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return await self.execute_query(query)


# Initialize database connection from environment variables
db_type = os.getenv("DB_TYPE", "sqlite")
connection_string = os.getenv("DATABASE_URL") or os.getenv("DATABASE_CONNECTION_STRING")
read_only = os.getenv("DB_READ_ONLY", "true").lower() == "true"
max_rows = int(os.getenv("DB_MAX_ROWS", "1000"))

db = DatabaseConnection(
    db_type=db_type,
    connection_string=connection_string,
    read_only=read_only,
    max_rows=max_rows
)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """Define available database tools"""
    tools = [
        Tool(
            name="list_tables",
            description="List all tables and views in the database",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="describe_table",
            description="Get schema information for a specific table (columns, types, constraints)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="get_sample_data",
            description="Get sample rows from a table to understand its contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of rows to return (default: 5, max: 100)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="execute_query",
            description="Execute a SQL SELECT query and return results. Use parameterized queries for safety.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional parameters for parameterized queries (prevents SQL injection)",
                        "items": {"type": ["string", "number", "null"]},
                        "default": []
                    }
                },
                "required": ["query"]
            }
        )
    ]
    
    # Only expose write operations if not in read-only mode
    if not db.read_only:
        tools.append(
            Tool(
                name="execute_write",
                description="Execute an INSERT, UPDATE, or DELETE query. Only available when read_only=False.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL INSERT/UPDATE/DELETE query to execute"
                        },
                        "params": {
                            "type": "array",
                            "description": "Optional parameters for parameterized queries",
                            "items": {"type": ["string", "number", "null"]},
                            "default": []
                        }
                    },
                    "required": ["query"]
                }
            )
        )
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "list_tables":
            tables = await db.list_tables()
            
            message = f"📊 Database Tables ({db.db_type}):\n\n"
            for table in tables:
                message += f"  • {table['name']} ({table.get('type', 'table')})\n"
            
            if not tables:
                message += "  No tables found.\n"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "describe_table":
            table_info = await db.describe_table(arguments["table_name"])
            
            message = f"📋 Table: {table_info['table_name']}\n"
            message += f"Rows: {table_info['row_count']:,}\n\n"
            message += "Columns:\n"
            
            for col in table_info["columns"]:
                pk_marker = " 🔑" if col.get("primary_key") else ""
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                message += f"  • {col['name']} ({col['type']}) {nullable}{pk_marker}\n"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "get_sample_data":
            table_name = arguments["table_name"]
            limit = arguments.get("limit", 5)
            
            rows = await db.get_sample_data(table_name, limit)
            
            message = f"📄 Sample data from {table_name} ({len(rows)} rows):\n\n"
            
            if rows:
                message += json.dumps(rows, indent=2, default=str)
            else:
                message += "No data found."
            
            return [TextContent(type="text", text=message)]
        
        elif name == "execute_query":
            query = arguments["query"]
            params = tuple(arguments.get("params", []))
            
            rows = await db.execute_query(query, params if params else None)
            
            message = f"✅ Query executed successfully\n"
            message += f"Rows returned: {len(rows)}\n\n"
            
            if rows:
                # Show results as JSON
                message += json.dumps(rows, indent=2, default=str)
                
                if len(rows) == db.max_rows:
                    message += f"\n\n⚠️ Results limited to {db.max_rows} rows"
            else:
                message += "No results returned."
            
            return [TextContent(type="text", text=message)]
        
        elif name == "execute_write":
            if db.read_only:
                return [TextContent(
                    type="text",
                    text="❌ Write operations are disabled in read-only mode"
                )]
            
            query = arguments["query"]
            params = tuple(arguments.get("params", []))
            
            result = await db.execute_write(query, params if params else None)
            
            message = f"✅ Write operation completed\n"
            message += f"Rows affected: {result['rows_affected']}\n"
            
            if "last_row_id" in result and result["last_row_id"]:
                message += f"Last inserted ID: {result['last_row_id']}\n"
            
            return [TextContent(type="text", text=message)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n\n"
        error_msg += "Make sure:\n"
        error_msg += "  • Table/column names are correct\n"
        error_msg += "  • Query syntax is valid\n"
        error_msg += "  • Database connection is working\n"
        
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server
    
    # Initialize database connection
    await db.connect()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())