# Database MCP Server

A powerful MCP server that lets Claude query SQL databases using natural language. Supports both SQLite (local, zero-setup) and PostgreSQL (cloud-hosted, production-ready).

## Features

- 🗄️ **Dual Database Support** - SQLite for instant setup, PostgreSQL for production
- 🔍 **Schema Discovery** - List tables, inspect columns, view constraints
- 📊 **SQL Query Execution** - Run SELECT queries with parameterized inputs
- 🔒 **Read-Only by Default** - Safe for production data analysis
- 📈 **Business Intelligence** - Pre-built views for common analyses
- 🎯 **Sample Data Preview** - Quickly explore table contents
- ⚡ **Connection Pooling** - Efficient PostgreSQL connections

## Installation

```bash
# Install UV (Python package manager)
# Mac/Linux:
brew install uv
# Or visit: https://github.com/astral-sh/uv

# Install dependencies with UV
uv sync

# For PostgreSQL support, install optional dependencies
uv sync --extra postgres

# Create the sample SQLite database
uv run examples/database/load_sample_data.py

# Test the server
uv run examples/database/server.py
```

## Configuration

### SQLite Setup (Default - Recommended for Learning)

Add to your Claude Desktop config:

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "database": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/examples/database",
        "run",
        "server.py"
      ],
      "env": {
        "DB_TYPE": "sqlite"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "database": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\absolute\\path\\to\\examples\\database",
        "run",
        "server.py"
      ],
      "env": {
        "DB_TYPE": "sqlite"
      }
    }
  }
}
```

### PostgreSQL Setup (Optional - For Production Patterns)

First, set up a free PostgreSQL database with [Neon](https://neon.tech) or [Supabase](https://supabase.com):

1. **Create database** - Sign up and create a new project
2. **Run schema** - Execute `schema.sql` in the SQL editor
3. **Load data** - Import CSV files from `datasets/sales/`
4. **Get connection string** - Copy from project settings

Then update your Claude Desktop config:

```json
{
  "mcpServers": {
    "database": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/examples/database",
        "run",
        "server.py"
      ],
      "env": {
        "DB_TYPE": "postgresql",
        "DATABASE_URL": "postgresql://user:password@host.region.provider.tech/dbname"
      }
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
| ---------- | --------- | ------------- |
| `DB_TYPE` | `sqlite` | Database type: `sqlite` or `postgresql` |
| `DATABASE_URL` | `../../datasets/sales.db` | Connection string (SQLite path or PostgreSQL URL) |
| `DB_READ_ONLY` | `true` | If `true`, only SELECT queries allowed |
| `DB_MAX_ROWS` | `1000` | Maximum rows returned per query |

## Sample Database

The SQLite database contains the same e-commerce dataset from the Data Analysis server:

- **customers** - 1,000 customers across 5 regions (North, South, East, West, Central)
- **products** - 100 products in 5 categories (Electronics, Clothing, Home, Books, Sports)
- **transactions** - 10,000 sales transactions with status tracking
- **Views** - Pre-built queries for revenue analysis and customer summaries

Generate the database:

```bash
# First ensure you have the CSV files
cd examples/data-analysis
uv run generate_sales_data.py

# Then create the SQLite database
cd ../database
uv run load_sample_data.py
```

## Example Prompts

### Getting Started

```plaintext
What tables are available in the database?
```

```plaintext
Describe the structure of the customers table
```

```plaintext
Show me 5 sample rows from the products table
```

### Basic Queries

```plaintext
What are the top 10 products by revenue?
```

```plaintext
How many customers do we have in each region?
```

```plaintext
Show me all transactions over $500
```

### Business Intelligence

```plaintext
What's our total revenue by product category?
```

```plaintext
Which customer segment has the highest average order value?
```

```plaintext
Show me monthly revenue trends
```

```plaintext
What percentage of transactions are completed vs cancelled?
```

### Advanced Analysis

```plaintext
For each region, show total revenue and number of customers
```

```plaintext
Find customers who have spent over $1000 total
```

```plaintext
Which products have the highest profit margins (price - cost)?
```

```plaintext
Show me the top 5 customers by total spend in each region
```

### Multi-Table Joins ⭐

```plaintext
Join transactions with customers and products to show:
- Product name
- Customer region
- Total revenue by region and category
```

```plaintext
Which suppliers provide the highest-rated products?
Join products data and calculate average rating by supplier.
```

```plaintext
Show customer lifetime value by segment.
Join customers with transactions, group by segment, and calculate total spend.
```

## Use Cases

### 1. Sales Performance Analysis

Understand revenue drivers and identify trends.

**Example Workflow**:

1. Query revenue by product category
2. Analyze regional performance differences
3. Compare customer segment behavior
4. Identify top-performing products

**Sample Prompt**:

```plaintext
Help me understand our sales performance:
1. What are our top 5 products by revenue?
2. Which region generates the most sales?
3. How does average order value vary by customer segment?
4. Show me products with high revenue but low profit margins.
```

### 2. Customer Segmentation

Analyze customer behavior and identify high-value segments.

**Example Workflow**:

1. Count customers by segment and region
2. Calculate average spend per segment
3. Identify high-value customer groups
4. Find patterns in purchase frequency

**Sample Prompt**:

```plaintext
I want to segment our customers:
1. How many customers are in each segment (Bronze, Silver, Gold, Platinum)?
2. What's the average lifetime value by segment?
3. Which regions have the most Platinum customers?
4. Find customers who haven't purchased in the last 90 days.
```

### 3. Product Performance

Evaluate product catalog and inventory.

**Example Workflow**:

1. Analyze sales by category
2. Identify slow-moving inventory
3. Calculate profit margins
4. Compare ratings across categories

**Sample Prompt**:

```plaintext
Analyze our product performance:
1. Which categories have the highest total revenue?
2. Find products with stock below 10 units
3. Show products with ratings below 3.0
4. Which suppliers have the best-performing products?
```

### 4. Financial Reporting

Generate business reports and metrics.

**Example Workflow**:

1. Calculate total revenue and transactions
2. Break down by time period (daily, monthly)
3. Analyze payment method distribution
4. Track cancelled vs completed orders

**Sample Prompt**:

```plaintext
Create a financial summary:
1. What's our total revenue from completed transactions?
2. Show revenue by month
3. What percentage of transactions use each payment method?
4. Calculate the cancellation rate
```

## Database Schema

### Tables

**customers**  

- `customer_id` (PRIMARY KEY) - Unique customer identifier
- `first_name`, `last_name` - Customer name
- `email` (UNIQUE) - Contact email
- `region` - North, South, East, West, Central
- `city` - Customer location
- `signup_date` - Account creation date
- `customer_segment` - Bronze, Silver, Gold, Platinum

**products**  

- `product_id` (PRIMARY KEY) - Unique product identifier
- `product_name` - Product display name
- `category` - Electronics, Clothing, Home, Books, Sports
- `price` - Retail price
- `cost` - Wholesale cost (for margin analysis)
- `stock_quantity` - Current inventory level
- `supplier` - Supplier name
- `rating` - Average customer rating (1-5)

**transactions**  

- `transaction_id` (PRIMARY KEY) - Unique transaction identifier
- `transaction_date` - Purchase date
- `customer_id` (FOREIGN KEY) - References customers
- `product_id` (FOREIGN KEY) - References products
- `quantity` - Number of items purchased
- `unit_price` - Price per item at time of purchase
- `total_amount` - Total transaction value
- `discount` - Discount percentage applied
- `payment_method` - Credit Card, PayPal, etc.
- `status` - Completed, Pending, or Cancelled

### Views

**revenue_by_product**  

- Pre-aggregated product performance metrics
- Includes total orders, units sold, revenue, average order value
- Only includes completed transactions

**customer_summary**  

- Pre-aggregated customer metrics
- Includes total orders, total spent, last order date
- Useful for customer lifetime value analysis

## How It Works

### Architecture

```plaintext
Claude Desktop
    ↓
MCP Protocol (stdio)
    ↓
Database MCP Server (Python)
    ↓
DatabaseConnection Class
    ├─ SQLite (built-in sqlite3)
    └─ PostgreSQL (asyncpg with connection pooling)
    ↓
Database (Local file or Cloud)
```

### Available Tools

1. **list_tables** - List all tables and views in the database
2. **describe_table** - Get schema information (columns, types, constraints)
3. **get_sample_data** - Preview data from any table
4. **execute_query** - Run SELECT queries with parameterized inputs
5. **execute_write** - INSERT/UPDATE/DELETE (only when read_only=false)

### Safety Features

- **Read-only mode by default** - Prevents accidental data modification
- **Parameterized queries** - Protects against SQL injection
- **Row limits** - Prevents memory issues with large result sets
- **Query validation** - Ensures only SELECT in read-only mode
- **Connection timeouts** - Prevents hanging queries

## Comparing SQLite vs PostgreSQL

### SQLite (Recommended for Learning)

**Pros:**

- ✅ Zero setup - just run `load_sample_data.py`
- ✅ No external dependencies
- ✅ Perfect for tutorials and local development
- ✅ File-based - easy to share and backup
- ✅ Built into Python

**Cons:**

- ❌ Not suitable for production web apps
- ❌ Limited concurrent writes
- ❌ No network access

**Best for:**

- Learning SQL and MCP
- Local prototyping
- Single-user applications
- Embedded databases

### PostgreSQL (Production-Ready)

**Pros:**

- ✅ Industry standard for production
- ✅ Excellent concurrency and performance
- ✅ Advanced features (JSON, full-text search, etc.)
- ✅ Cloud hosting available (Neon, Supabase)
- ✅ Strong ACID compliance

**Cons:**

- ❌ Requires setup (or cloud account)
- ❌ More complex configuration
- ❌ Additional dependency (asyncpg)

**Best for:**

- Production applications
- Team collaboration
- Web applications
- Large datasets

## SQL Query Tips

### Basic Patterns

```sql
-- Count rows
SELECT COUNT(*) FROM customers;

-- Filter data
SELECT * FROM products WHERE category = 'Electronics';

-- Sort results
SELECT * FROM transactions ORDER BY total_amount DESC LIMIT 10;

-- Aggregate data
SELECT category, AVG(price) as avg_price 
FROM products 
GROUP BY category;
```

### Joins

```sql
-- Inner join
SELECT 
    t.transaction_id,
    c.first_name,
    p.product_name,
    t.total_amount
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
JOIN products p ON t.product_id = p.product_id
WHERE t.status = 'Completed';

-- Left join (include all customers even without orders)
SELECT 
    c.customer_id,
    c.first_name,
    COUNT(t.transaction_id) as order_count
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id;
```

### Filtering

```sql
-- Multiple conditions
SELECT * FROM transactions 
WHERE status = 'Completed' 
AND total_amount > 100
AND transaction_date >= '2024-01-01';

-- IN clause
SELECT * FROM products 
WHERE category IN ('Electronics', 'Books');

-- LIKE pattern matching
SELECT * FROM customers 
WHERE email LIKE '%@gmail.com';
```

### Aggregations

```sql
-- Group by with multiple aggregates
SELECT 
    region,
    COUNT(*) as customer_count,
    COUNT(DISTINCT city) as city_count
FROM customers
GROUP BY region;

-- Having clause (filter after grouping)
SELECT 
    customer_id,
    SUM(total_amount) as total_spent
FROM transactions
WHERE status = 'Completed'
GROUP BY customer_id
HAVING SUM(total_amount) > 1000;
```

## Troubleshooting

### Database not found

**Error**: `no such table: customers` or `database not found`

**Solution**:

```bash
# Generate CSV data if needed
cd examples/data-analysis
uv run generate_sales_data.py

# Create SQLite database
cd ../database
uv run load_sample_data.py
```

### PostgreSQL connection failed

**Error**: `asyncpg not installed` or `connection refused`

**Solution**:

```bash
# Install asyncpg
uv pip install asyncpg

# Verify your connection string
# Format: postgresql://user:password@host:port/database
```

### Tool not appearing in Claude

**Solution**:

1. Check Claude Desktop logs (`~/Library/Logs/Claude/mcp*.log` on Mac)
2. Verify the absolute path in your config
3. Restart Claude Desktop completely (quit, not just close window)
4. Ensure `uv sync` completed successfully

### Queries timing out

**Solution**:

- Add LIMIT clause to large queries
- Check database indexes exist (`load_sample_data.py` creates them)
- Increase timeout in PostgreSQL: `command_timeout=60` in server.py

## Security Best Practices

### Read-Only Access (Default)

The server runs in read-only mode by default:

- ✅ Only SELECT queries allowed
- ❌ INSERT/UPDATE/DELETE blocked

To enable writes (use with caution):

```json
"env": {
  "DB_READ_ONLY": "false"
}
```

### Connection String Security

- ✅ Store credentials in environment variables
- ✅ Never commit connection strings to git
- ✅ Use read-only database accounts when possible
- ✅ Rotate credentials regularly

### Query Safety

- ✅ Always use parameterized queries
- ✅ Set reasonable row limits
- ✅ Implement query timeouts
- ✅ Validate user inputs

## Next Steps

After mastering this example:

1. **Try the Web API Server** - Learn to integrate external APIs
2. **Combine servers** - Use file-system, data-analysis, and database together
3. **Build custom views** - Create specialized queries for your domain
4. **Connect to your own databases** - Apply patterns to real projects
5. **Explore PostgreSQL features** - JSON columns, full-text search, etc.

## Learning Resources

### SQL

- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [SQL Best Practices](https://www.sisense.com/blog/8-ways-fine-tune-sql-queries-production-databases/)

### Cloud Databases

- [Neon PostgreSQL](https://neon.tech) - Serverless Postgres with free tier
- [Supabase](https://supabase.com) - Open source Firebase alternative

### Security

- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Database Security](https://www.imperva.com/learn/data-security/database-security/)

## Contributing

Found a bug or have a suggestion? Please open an issue or submit a PR!

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

This project is part of the MCP Agentic Starter Kit.

See [LICENSE.md](../../LICENSE.md) for details.
