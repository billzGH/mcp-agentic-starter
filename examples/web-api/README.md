<!-- markdownlint-disable MD024 -->
# Web API MCP Server

A powerful MCP server that lets Claude interact with REST APIs for e-commerce and analytics. Features a built-in mock API for learning (no external accounts needed) and patterns for connecting to real services.

## Features

- 🌐 **REST API Integration** - Connect Claude to external web services
- 🔒 **Secure Authentication** - API key management and header handling
- 🔄 **Rate Limiting** - Automatic rate limit handling with exponential backoff
- 🔁 **Retry Logic** - Resilient error handling with configurable retries
- 📊 **E-commerce Tools** - Products, orders, and inventory management
- 📈 **Analytics Tools** - Traffic metrics and conversion data
- 🎯 **Mock API Included** - Local server for testing without external dependencies
- ⚡ **Async Operations** - Fast, non-blocking HTTP requests

## Installation

```bash
# Install UV (Python package manager)
# Mac/Linux:
brew install uv
# Or visit: https://github.com/astral-sh/uv

# Install dependencies with UV
uv sync

# For FastAPI support (mock API)
uv sync --extra api

# Test the mock API server
uv run examples/web-api/mock_api.py

# Test the MCP server
uv run examples/web-api/server.py
```

## Configuration

### With Mock API (Default - Recommended for Learning)

**Step 1:** Start the mock API server in a separate terminal:

```bash
uv run examples/web-api/mock_api.py
```

You should see:

```plaintext
🚀 Starting Mock API Server on http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
🔑 Valid API Keys: test_api_key, demo_key_12345
```

**Step 2:** Add to your Claude Desktop config:

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "web-api": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/examples/web-api",
        "server.py"
      ],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "API_KEY": "test_api_key"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "web-api": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\absolute\\path\\to\\examples\\web-api",
        "server.py"
      ],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "API_KEY": "test_api_key"
      }
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
| ---------- | --------- | ------------- |
| `API_BASE_URL` | `http://localhost:8000` | Base URL for the API |
| `API_KEY` | `test_api_key` | API key for authentication |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `MAX_RETRIES` | `3` | Maximum number of retry attempts |

### With Real APIs (Production)

To connect to real services like Shopify, Stripe, or custom APIs:

```json
{
  "mcpServers": {
    "web-api": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/examples/web-api",
        "server.py"
      ],
      "env": {
        "API_BASE_URL": "https://your-api.example.com",
        "API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

## Mock API Features

The included mock API simulates realistic e-commerce and analytics endpoints:

### E-commerce Endpoints

- `GET /api/products` - List products with filters (category, price, stock)
- `GET /api/products/{id}` - Get specific product details
- `GET /api/inventory/{id}` - Check inventory levels
- `GET /api/orders` - List orders with filters (status, customer)
- `GET /api/orders/{id}` - Get specific order details

### Analytics Endpoints

- `POST /api/analytics/report` - Get analytics reports (page views, traffic sources)

### Features

- ✅ Rate limiting (100 requests/minute)
- ✅ API key authentication
- ✅ Pagination support
- ✅ Realistic sample data (45 products, 100 orders)
- ✅ Interactive API documentation at `/docs`

## Example Prompts

### Getting Started

```plaintext
What products are available in the Electronics category?
```

```plaintext
Check the inventory for product PROD0001
```

```plaintext
Show me all pending orders
```

### E-commerce Operations

```plaintext
List all products under $100
```

```plaintext
Which products are out of stock?
```

```plaintext
Show me orders with status "shipped"
```

```plaintext
Find products in the Clothing category that are in stock
```

### Inventory Management

```plaintext
Check inventory levels for all products in the Electronics category
```

```plaintext
Which products have low stock warnings?
```

```plaintext
Show me products with more than 50 units in stock
```

### Order Management

```plaintext
Find all delivered orders from the last 30 days
```

```plaintext
Show me order ORD00001 details
```

```plaintext
How many orders are currently in "processing" status?
```

### Analytics & Reporting

```plaintext
Get page views for the last 30 days
```

```plaintext
Show me traffic sources breakdown
```

```plaintext
What's our top traffic source?
```

```plaintext
Compare page views between this week and last week
```

### Cross-Tool Analysis ⭐

Combine with other MCP servers for powerful workflows:

```plaintext
Get all Electronics products from the API and save the results to a file
(Uses web-api + file-system servers)
```

```plaintext
Fetch order data from the API and analyze revenue trends by status
(Uses web-api + data-analysis servers)
```

```plaintext
Load products from the API into the database for persistent storage
(Uses web-api + database servers)
```

## Use Cases

### 1. E-commerce Operations

Monitor and manage online store operations.

**Example Workflow**:

1. Check inventory levels across product catalog
2. Identify low-stock items
3. Review pending orders
4. Track order fulfillment status

**Sample Prompt**:

```plaintext
Help me with inventory management:
1. Which products have less than 10 units in stock?
2. Show me all pending orders
3. What's the total value of orders in "processing" status?
```

### 2. Analytics & Insights

Track website performance and visitor behavior.

**Example Workflow**:

1. Pull page view metrics
2. Analyze traffic sources
3. Identify trends over time
4. Calculate conversion rates

**Sample Prompt**:

```plaintext
Give me an analytics summary:
1. What are our top 3 traffic sources?
2. Show page views for the last 7 days
3. What's the average bounce rate?
```

### 3. Order Fulfillment

Track and manage order pipeline.

**Example Workflow**:

1. List orders by status
2. Identify delayed shipments
3. Review cancelled orders
4. Monitor order volume

**Sample Prompt**:

```plaintext
Help me review our orders:
1. How many orders are currently "pending"?
2. Show me all "shipped" orders from this week
3. What percentage of orders are "delivered" vs "cancelled"?
```

### 4. Product Catalog Management

Maintain and analyze product inventory.

**Example Workflow**:

1. List products by category
2. Filter by price range
3. Check stock availability
4. Identify popular items

**Sample Prompt**:

```plaintext
Analyze our product catalog:
1. How many products do we have in each category?
2. What's the average price by category?
3. Which categories have the most out-of-stock items?
```

## API Best Practices

### Rate Limiting

The server includes automatic rate limiting:

- Default: 10 requests per 60 seconds
- Handles API `429` responses with retry-after
- Exponential backoff for failed requests

### Error Handling

Robust error recovery:

- Automatic retry with exponential backoff
- Timeout handling (default 30 seconds)
- Clear error messages with troubleshooting tips
- Graceful degradation on API failures

### Authentication

Secure API key management:

- API keys stored in environment variables
- Never hardcoded in source code
- Bearer token authentication pattern
- Support for custom header formats

### Pagination

Efficient data retrieval:

- Supports offset-based pagination
- Configurable page size (default: 20, max: 100)
- "has_more" indicator for additional pages
- Automatic handling of large result sets

## Architecture

```plaintext
Claude Desktop
    ↓
MCP Protocol (stdio)
    ↓
Web API MCP Server (Python)
    ↓
HTTP Client (httpx)
    ├─ Rate Limiter
    ├─ Retry Logic
    └─ Auth Headers
    ↓
API Endpoint (Local or Remote)
    ├─ Mock API (FastAPI) - For learning
    └─ Real APIs (Shopify, Stripe, etc.) - For production
```

## Available Tools

### E-commerce Tools

1. **list_products** - List products with filters (category, price, stock status)
2. **get_product** - Get detailed information for a specific product
3. **check_inventory** - Check stock levels and availability
4. **list_orders** - List orders with filters (status, customer ID)
5. **get_order** - Get detailed information for a specific order

### Analytics Tools

1. **get_analytics_report** - Get analytics metrics (page views, traffic sources)

## Connecting to Real APIs

### Pattern 1: Shopify-Style API

If your API follows REST patterns similar to Shopify:

```json
{
  "env": {
    "API_BASE_URL": "https://your-store.myshopify.com/admin/api/2024-01",
    "API_KEY": "your_shopify_access_token"
  }
}
```

You may need to adjust the endpoint paths in `server.py` to match Shopify's API structure.

### Pattern 2: Custom REST API

For custom APIs with different endpoints:

1. Update the tool endpoint paths in `server.py`
2. Adjust request/response parsing for your API format
3. Update authentication headers if needed
4. Configure rate limiting based on your API limits

### Pattern 3: Third-Party Services

Examples of compatible services:

- **Stripe**: Payment and subscription data
- **Twilio**: Communication logs
- **SendGrid**: Email analytics
- **GitHub**: Repository data
- **Slack**: Channel messages

## Troubleshooting

### Mock API won't start

**Error**: `Address already in use` or `Port 8000 is already allocated`

**Solution**:

```bash
# Find and kill process on port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn mock_api:app --port 8001
```

### Connection refused

**Error**: `Connection refused` or `Cannot connect to API`

**Solution**:

1. Verify mock API is running: `curl http://localhost:8000/health`
2. Check `API_BASE_URL` in Claude config matches mock API
3. Ensure no firewall blocking localhost connections

### Authentication errors

**Error**: `401 Unauthorized` or `Invalid API key`

**Solution**:

1. Verify `API_KEY` in config matches mock API keys
2. Valid keys: `test_api_key` or `demo_key_12345`
3. Check Authorization header format: `Bearer YOUR_API_KEY`

### Rate limit errors

**Error**: `429 Too Many Requests`

**Solution**:

- Mock API limit: 100 requests/minute
- Server automatically retries after rate limit
- Wait 60 seconds for counter to reset
- Consider increasing limit in `mock_api.py` for testing

### Claude can't see the tools

**Solution**:

1. Check Claude Desktop logs
2. Verify absolute path in config
3. Ensure mock API is running
4. Restart Claude Desktop completely

## Security Best Practices

### API Key Management

- ✅ **Never commit API keys** to git
- ✅ Store keys in environment variables or config
- ✅ Use different keys for dev/staging/production
- ✅ Rotate keys regularly
- ✅ Use read-only keys when possible

### Request Security

- ✅ Always use HTTPS for production APIs
- ✅ Validate SSL certificates
- ✅ Set reasonable timeouts
- ✅ Implement rate limiting
- ✅ Log API errors (but not sensitive data)

### Data Privacy

- ✅ Don't log full API responses (may contain PII)
- ✅ Redact sensitive fields in logs
- ✅ Use secure credential storage
- ✅ Follow API provider's data usage policies

## Extending the Server

### Adding New Tools

To add custom API endpoints:

1. **Define the tool** in `list_tools()`:

```python
Tool(
    name="my_custom_tool",
    description="Description of what it does",
    inputSchema={...},
)
```

1. **Implement the handler** in `call_tool()`:

```python
elif name == "my_custom_tool":
    result = await api_client.get("/your/endpoint")
    # Process and format response
    return [TextContent(type="text", text=formatted_result)]
```

### Customizing Rate Limits

Adjust in the `RateLimiter` class:

```python
self.rate_limiter = RateLimiter(
    max_calls=50,  # Increase limit
    period=60,      # Time window in seconds
)
```

### Adding Response Caching

For frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_products():
    return await api_client.get("/api/products")
```

## Next Steps

After mastering this example:

1. **Connect to real APIs** - Try Shopify, Stripe, or your custom API
2. **Combine servers** - Use with database and file-system servers
3. **Build workflows** - Create multi-step API orchestrations
4. **Add custom tools** - Extend for your specific use cases
5. **Implement webhooks** - Add inbound event handling

## Learning Resources

### HTTP & APIs

- [HTTP Methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [REST API Tutorial](https://restfulapi.net/)
- [httpx Documentation](https://www.python-httpx.org/)

### Authentication

- [API Authentication](https://swagger.io/docs/specification/authentication/)
- [OAuth 2.0](https://oauth.net/2/)
- [API Keys Best Practices](https://cloud.google.com/docs/authentication/api-keys)

### Rate Limiting

- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [HTTP 429 Status Code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)

### FastAPI (Mock API)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Building APIs with FastAPI](https://fastapi.tiangolo.com/tutorial/)

## Contributing

Found a bug or have a suggestion? Please open an issue or submit a PR!

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

This project is part of the MCP Agentic Starter Kit.

See [LICENSE.md](../../LICENSE.md) for details.
