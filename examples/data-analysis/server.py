#!/usr/bin/env python3
"""
Data Analysis MCP Server
Allows Claude to analyze CSV/JSON data files
"""

import json
import csv
import asyncio
from pathlib import Path
from typing import Any, Dict, List
import statistics
from collections import Counter, defaultdict

from mcp.server import Server
from mcp.types import Tool, TextContent

# Initialize server
server = Server("data-analysis")

class DataAnalyzer:
    """Analyze CSV and JSON data files"""
    
    def __init__(self, data_dir: str = "../../datasets"):
        self.data_dir = Path(data_dir)
    
    def list_files(self) -> List[Dict[str, Any]]:
        """List available data files"""
        files = []
        for ext in ['*.csv', '*.json']:
            for file in self.data_dir.rglob(ext):
                files.append({
                    "path": str(file.relative_to(self.data_dir)),
                    "name": file.name,
                    "size": file.stat().st_size,
                    "type": file.suffix
                })
        return files
    
    def load_csv(self, filepath: str) -> List[Dict]:
        """Load CSV file"""
        full_path = self.data_dir / filepath
        with open(full_path, 'r') as f:
            return list(csv.DictReader(f))
    
    def load_json(self, filepath: str) -> Any:
        """Load JSON file"""
        full_path = self.data_dir / filepath
        with open(full_path, 'r') as f:
            return json.load(f)
    
    def get_summary(self, filepath: str) -> Dict:
        """Get summary statistics for a file"""
        if filepath.endswith('.csv'):
            data = self.load_csv(filepath)
        else:
            data = self.load_json(filepath)
        
        if not data:
            return {"error": "No data found"}
        
        # Basic stats
        summary = {
            "num_records": len(data),
            "columns": list(data[0].keys()) if isinstance(data[0], dict) else [],
            "sample_record": data[0] if data else None
        }
        
        # Column type analysis
        if summary["columns"]:
            column_types = {}
            for col in summary["columns"]:
                values = [row[col] for row in data if col in row]
                column_types[col] = self._infer_type(values)
            summary["column_types"] = column_types
        
        return summary
    
    def _infer_type(self, values: List) -> str:
        """Infer the type of a column"""
        non_empty = [v for v in values if v and str(v).strip()]
        if not non_empty:
            return "empty"
        
        sample = non_empty[0]
        try:
            float(sample)
            return "numeric"
        except (ValueError, TypeError):
            return "text"
    
    def analyze_column(self, filepath: str, column: str) -> Dict:
        """Analyze a specific column"""
        if filepath.endswith('.csv'):
            data = self.load_csv(filepath)
        else:
            data = self.load_json(filepath)
        
        values = [row[column] for row in data if column in row]
        
        # Try numeric analysis
        try:
            numeric_values = [float(v) for v in values if v and str(v).strip()]
            return {
                "column": column,
                "type": "numeric",
                "count": len(numeric_values),
                "min": min(numeric_values),
                "max": max(numeric_values),
                "mean": statistics.mean(numeric_values),
                "median": statistics.median(numeric_values),
                "stdev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
            }
        except (ValueError, TypeError):
            # Text analysis
            text_values = [str(v) for v in values if v]
            counter = Counter(text_values)
            return {
                "column": column,
                "type": "text",
                "count": len(text_values),
                "unique_values": len(counter),
                "most_common": counter.most_common(10),
                "sample_values": list(set(text_values))[:10]
            }
    
    def filter_data(self, filepath: str, conditions: List[Dict]) -> List[Dict]:
        """Filter data based on conditions"""
        if filepath.endswith('.csv'):
            data = self.load_csv(filepath)
        else:
            data = self.load_json(filepath)
        
        filtered = data
        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            if operator == '==':
                filtered = [row for row in filtered if str(row.get(column)) == str(value)]
            elif operator == '>':
                filtered = [row for row in filtered if float(row.get(column, 0)) > float(value)]
            elif operator == '<':
                filtered = [row for row in filtered if float(row.get(column, 0)) < float(value)]
            elif operator == 'contains':
                filtered = [row for row in filtered if value.lower() in str(row.get(column, '')).lower()]
        
        return filtered
    
    def aggregate(self, filepath: str, group_by: str, agg_column: str, agg_func: str) -> Dict:
        """Aggregate data by a column"""
        if filepath.endswith('.csv'):
            data = self.load_csv(filepath)
        else:
            data = self.load_json(filepath)
        
        groups = defaultdict(list)
        for row in data:
            key = row.get(group_by, 'Unknown')
            value = row.get(agg_column)
            if value:
                try:
                    groups[key].append(float(value))
                except (ValueError, TypeError):
                    pass
        
        results = {}
        for key, values in groups.items():
            if agg_func == 'sum':
                results[key] = sum(values)
            elif agg_func == 'avg':
                results[key] = statistics.mean(values)
            elif agg_func == 'count':
                results[key] = len(values)
            elif agg_func == 'min':
                results[key] = min(values)
            elif agg_func == 'max':
                results[key] = max(values)
        
        return {
            "grouped_by": group_by,
            "aggregated": agg_column,
            "function": agg_func,
            "results": dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        }

analyzer = DataAnalyzer()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Define available tools"""
    return [
        Tool(
            name="list_data_files",
            description="List all available data files (CSV and JSON)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_data_summary",
            description="Get summary statistics and column info for a data file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to data file (e.g., 'sales/customers.csv')"}
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="analyze_column",
            description="Analyze a specific column (get stats, distributions, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to data file"},
                    "column": {"type": "string", "description": "Column name to analyze"}
                },
                "required": ["filepath", "column"]
            }
        ),
        Tool(
            name="filter_data",
            description="Filter data based on conditions",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to data file"},
                    "conditions": {
                        "type": "array",
                        "description": "List of filter conditions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "operator": {"type": "string", "enum": ["==", ">", "<", "contains"]},
                                "value": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["filepath", "conditions"]
            }
        ),
        Tool(
            name="aggregate_data",
            description="Group and aggregate data (sum, avg, count, min, max)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to data file"},
                    "group_by": {"type": "string", "description": "Column to group by"},
                    "agg_column": {"type": "string", "description": "Column to aggregate"},
                    "agg_func": {"type": "string", "enum": ["sum", "avg", "count", "min", "max"]}
                },
                "required": ["filepath", "group_by", "agg_column", "agg_func"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "list_data_files":
            files = analyzer.list_files()
            message = f"Found {len(files)} data files:\n\n"
            for file in files:
                size_kb = file['size'] / 1024
                message += f"📄 {file['path']} ({size_kb:.1f} KB)\n"
            return [TextContent(type="text", text=message)]
        
        elif name == "get_data_summary":
            summary = analyzer.get_summary(arguments["filepath"])
            message = f"📊 Summary of {arguments['filepath']}:\n\n"
            message += f"Records: {summary['num_records']}\n"
            message += f"Columns: {', '.join(summary['columns'])}\n\n"
            if 'column_types' in summary:
                message += "Column Types:\n"
                for col, typ in summary['column_types'].items():
                    message += f"  • {col}: {typ}\n"
            return [TextContent(type="text", text=message)]
        
        elif name == "analyze_column":
            result = analyzer.analyze_column(arguments["filepath"], arguments["column"])
            message = f"📈 Analysis of '{result['column']}':\n\n"
            message += f"Type: {result['type']}\n"
            message += f"Count: {result['count']}\n\n"
            
            if result['type'] == 'numeric':
                message += f"Min: {result['min']:.2f}\n"
                message += f"Max: {result['max']:.2f}\n"
                message += f"Mean: {result['mean']:.2f}\n"
                message += f"Median: {result['median']:.2f}\n"
                message += f"Std Dev: {result['stdev']:.2f}\n"
            else:
                message += f"Unique Values: {result['unique_values']}\n\n"
                message += "Most Common:\n"
                for value, count in result['most_common'][:5]:
                    message += f"  • {value}: {count}\n"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "filter_data":
            filtered = analyzer.filter_data(arguments["filepath"], arguments["conditions"])
            message = f"🔍 Filtered {len(filtered)} records\n\n"
            if filtered:
                message += "Sample results:\n"
                for row in filtered[:5]:
                    message += f"{json.dumps(row, indent=2)}\n\n"
            return [TextContent(type="text", text=message)]
        
        elif name == "aggregate_data":
            result = analyzer.aggregate(
                arguments["filepath"],
                arguments["group_by"],
                arguments["agg_column"],
                arguments["agg_func"]
            )
            message = f"📊 Aggregation Results:\n\n"
            message += f"Grouped by: {result['grouped_by']}\n"
            message += f"Function: {result['function']} of {result['aggregated']}\n\n"
            for key, value in list(result['results'].items())[:10]:
                message += f"{key}: {value:.2f}\n"
            return [TextContent(type="text", text=message)]
        
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