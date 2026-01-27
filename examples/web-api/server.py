#!/usr/bin/env python3
"""
Web API MCP Server
Provides Claude with access to REST APIs (e-commerce and analytics)
"""

import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Initialize server
server = Server("web-api")

# Configuration from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "test_api_key")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


class RateLimiter:
    """Simple rate limiter to prevent overwhelming APIs"""
    
    def __init__(self, max_calls: int = 10, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls: List[datetime] = []
    
    async def acquire(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Remove calls outside the time window
        self.calls = [
            call_time for call_time in self.calls
            if (now - call_time).total_seconds() < self.period
        ]
        
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = self.calls[0]
            wait_time = self.period - (now - oldest_call).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                # Retry after waiting
                return await self.acquire()
        
        self.calls.append(now)


class APIClient:
    """HTTP client for making API requests with retry logic"""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        self.rate_limiter = RateLimiter(max_calls=10, period=60)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an API request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                # Make request
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                    json=json_data,
                )
                
                # Handle rate limiting from API
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    continue
                
                # Raise for other HTTP errors
                response.raise_for_status()
                
                return response.json()
            
            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Network error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return await self.request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request"""
        return await self.request("POST", endpoint, json_data=json_data)


# Initialize API client
api_client = APIClient(
    base_url=API_BASE_URL,
    api_key=API_KEY,
    timeout=REQUEST_TIMEOUT,
    max_retries=MAX_RETRIES,
)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """Define available API tools"""
    return [
        Tool(
            name="list_products",
            description="List products from the e-commerce API with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (Electronics, Clothing, Home, Books, Sports)",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter",
                    },
                    "in_stock": {
                        "type": "boolean",
                        "description": "Filter for in-stock items only",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of products to return (default: 20, max: 100)",
                        "default": 20,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_product",
            description="Get details for a specific product by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID (e.g., PROD0001)",
                    },
                },
                "required": ["product_id"],
            },
        ),
        Tool(
            name="check_inventory",
            description="Check inventory levels for a specific product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID to check inventory for",
                    },
                },
                "required": ["product_id"],
            },
        ),
        Tool(
            name="list_orders",
            description="List orders with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status (pending, processing, shipped, delivered, cancelled)",
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Filter by customer ID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of orders to return (default: 20, max: 100)",
                        "default": 20,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_order",
            description="Get details for a specific order by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID (e.g., ORD00001)",
                    },
                },
                "required": ["order_id"],
            },
        ),
        Tool(
            name="get_analytics_report",
            description="Get analytics report for specified metric and date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to report on (page_views or traffic_sources)",
                        "enum": ["page_views", "traffic_sources"],
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for report (YYYY-MM-DD format)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for report (YYYY-MM-DD format)",
                    },
                },
                "required": ["metric"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "list_products":
            params = {}
            if "category" in arguments:
                params["category"] = arguments["category"]
            if "min_price" in arguments:
                params["min_price"] = arguments["min_price"]
            if "max_price" in arguments:
                params["max_price"] = arguments["max_price"]
            if "in_stock" in arguments:
                params["in_stock"] = arguments["in_stock"]
            if "limit" in arguments:
                params["limit"] = arguments["limit"]
            
            result = await api_client.get("/api/products", params=params)
            
            products = result.get("data", [])
            pagination = result.get("pagination", {})
            
            message = f"📦 Found {pagination.get('total', 0)} products"
            if params:
                message += f" (filtered)"
            message += f"\nShowing {len(products)} results:\n\n"
            message += json.dumps(products, indent=2)
            
            if pagination.get("has_more"):
                message += f"\n\n⚠️ More results available (showing {len(products)} of {pagination['total']})"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "get_product":
            product_id = arguments["product_id"]
            result = await api_client.get(f"/api/products/{product_id}")
            
            product = result.get("data", {})
            message = f"📦 Product Details:\n\n{json.dumps(product, indent=2)}"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "check_inventory":
            product_id = arguments["product_id"]
            result = await api_client.get(f"/api/inventory/{product_id}")
            
            inventory = result.get("data", {})
            stock = inventory.get("stock", 0)
            
            message = f"📊 Inventory Status for {inventory.get('product_name')}:\n\n"
            message += f"  • Stock Level: {stock} units\n"
            message += f"  • Available: {'✅ Yes' if inventory.get('available') else '❌ No'}\n"
            
            if inventory.get("low_stock_warning"):
                message += f"  • ⚠️ LOW STOCK WARNING\n"
            
            message += f"  • Last Updated: {inventory.get('last_updated')}\n"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "list_orders":
            params = {}
            if "status" in arguments:
                params["status"] = arguments["status"]
            if "customer_id" in arguments:
                params["customer_id"] = arguments["customer_id"]
            if "limit" in arguments:
                params["limit"] = arguments["limit"]
            
            result = await api_client.get("/api/orders", params=params)
            
            orders = result.get("data", [])
            pagination = result.get("pagination", {})
            
            message = f"🛒 Found {pagination.get('total', 0)} orders"
            if params:
                message += f" (filtered)"
            message += f"\nShowing {len(orders)} results:\n\n"
            message += json.dumps(orders, indent=2)
            
            if pagination.get("has_more"):
                message += f"\n\n⚠️ More results available (showing {len(orders)} of {pagination['total']})"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "get_order":
            order_id = arguments["order_id"]
            result = await api_client.get(f"/api/orders/{order_id}")
            
            order = result.get("data", {})
            message = f"🛒 Order Details:\n\n{json.dumps(order, indent=2)}"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "get_analytics_report":
            metric = arguments["metric"]
            params = {"metric": metric}
            
            if "start_date" in arguments:
                params["start_date"] = arguments["start_date"]
            if "end_date" in arguments:
                params["end_date"] = arguments["end_date"]
            
            result = await api_client.post("/api/analytics/report", json_data=params)
            
            data = result.get("data", [])
            summary = result.get("summary", {})
            
            message = f"📈 Analytics Report: {metric}\n\n"
            message += "Summary:\n"
            message += json.dumps(summary, indent=2)
            message += "\n\nDetailed Data:\n"
            message += json.dumps(data[:10], indent=2)  # Show first 10 entries
            
            if len(data) > 10:
                message += f"\n\n... and {len(data) - 10} more entries"
            
            return [TextContent(type="text", text=message)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_msg = f"❌ API Error: {str(e)}\n\n"
        error_msg += "Common issues:\n"
        error_msg += "  • Mock API server not running (run: uv run mock_api.py)\n"
        error_msg += "  • Invalid API key in configuration\n"
        error_msg += "  • Network connectivity issues\n"
        error_msg += "  • API rate limit exceeded\n"
        
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    finally:
        await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())