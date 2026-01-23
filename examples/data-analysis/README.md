# Data Analysis MCP Server

A powerful MCP server that lets Claude analyze CSV and JSON datasets with filtering, aggregation, and multi-file joins.

## Features

- 📊 Analyze CSV and JSON data files
- 🔍 Automatic column type detection
- 📈 Statistical analysis (min, max, mean, median, standard deviation)
- 🔗 Multi-file joins for complex analysis
- 📊 Group-by aggregations (sum, avg, count, min, max)
- 🎯 Flexible filtering with multiple conditions
- 📁 Dataset discovery and exploration

## Installation

```bash
# Install UV (Python package manager)
# Mac/Linux:
brew install uv
# Or visit: https://github.com/astral-sh/uv

# Install dependencies with UV
uv sync

# Test the server
uv run server.py
```

## Configuration

Add to your Claude Desktop config:

**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-analysis": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/examples/data-analysis",
        "run",
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
    "data-analysis": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\absolute\\path\\to\\examples\\data-analysis",
        "run",
        "server.py"
      ]
    }
  }
}
```

## Sample Dataset

This server includes a realistic e-commerce dataset with:

- **customers.csv** - 1,000 customers across 5 regions
- **products.csv** - 100 products in 5 categories
- **transactions.csv** - 10,000 sales transactions
- **README.json** - Dataset metadata

Generate fresh sample data:

```bash
uv run generate_sales_data.py
```

## Example Prompts

### Getting Started

```plaintext
What data files are available?
```

```plaintext
Show me a summary of the sales/customers.csv file
```

```plaintext
Analyze the total_amount column in transactions.csv
```

### Basic Analysis

```plaintext
What are the most popular product categories?
```

```plaintext
Show me the distribution of customer segments
```

```plaintext
What's the price range for products in the Electronics category?
```

### Filtering Data

```plaintext
Show me all transactions over $500
```

```plaintext
Find customers in the West region who are in the Platinum segment
```

```plaintext
Filter products with ratings above 4.5
```

### Aggregation Analysis

```plaintext
What's the total revenue by product category?
```

```plaintext
Show me average order value by payment method
```

```plaintext
Count transactions by customer segment
```

### Advanced Multi-File Joins ⭐

This is where the server really shines - combining data from multiple files:

```plaintext
Join transactions with customers and show total revenue by region
```

```plaintext
Which customer segments generate the most revenue?
Analyze by joining transactions with customers.
```

```plaintext
Join transactions with products to find top-performing categories
```

```plaintext
Analyze average order value by customer region.
Join transactions with customers, group by region, and calculate average.
```

```plaintext
Which suppliers have the highest-rated products?
Join products data to analyze by supplier and rating.
```

## Use Cases

### 1. Sales Performance Analysis

Understand revenue drivers and sales patterns.

**Example Workflow**:

1. Get total revenue by region (join transactions + customers)
2. Identify top product categories
3. Analyze seasonal trends by month
4. Compare performance across customer segments

**Sample Prompt**:

```plaintext
I want to understand our sales performance:
1. What's total revenue by region?
2. Which product categories drive the most sales?
3. How does average order value differ by customer segment?
```

### 2. Customer Intelligence

Segment and analyze customer behavior.

**Example Workflow**:

1. Analyze customer distribution by region
2. Compare purchase patterns by segment
3. Identify high-value customer groups
4. Calculate lifetime value metrics

**Sample Prompt**:

```plaintext
Help me understand our customer base:
1. How are customers distributed across regions?
2. Which segments have the highest average order value?
3. What products do Platinum customers buy most?
```

### 3. Product Performance

Optimize inventory and pricing decisions.

**Example Workflow**:

1. Analyze sales by product category
2. Compare pricing across categories
3. Identify best-selling products
4. Evaluate supplier performance

**Sample Prompt**:

```plaintext
Analyze our product catalog:
1. Which categories generate the most revenue?
2. What's the average price by category?
3. Which products have the best ratings?
```

### 4. Business Intelligence Dashboard

Create comprehensive business reports.

**Example Workflow**:

1. Join transactions with customers for regional analysis
2. Join transactions with products for category analysis
3. Calculate key metrics (total revenue, average order, etc.)
4. Identify trends and outliers

**Sample Prompt**:

```plaintext
Create a business overview:
1. Total revenue and number of transactions
2. Revenue by region and customer segment
3. Top 5 product categories by sales
4. Average order value by region
```

## Detailed Walkthrough

### Scenario: "Which regions are our top performers?"

This scenario demonstrates the progression from basic exploration to advanced multi-file analysis.

#### Step 1: Discover Available Data

**Prompt**: "What data files are available?"

**Result**: You'll see:

- sales/customers.csv
- sales/products.csv  
- sales/transactions.csv
- sales/README.json

#### Step 2: Understand the Data Structure

**Prompt**: "Show me a summary of transactions.csv and customers.csv"

**Result**: You'll learn:

- Transactions has: transaction_id, customer_id, product_id, total_amount, etc.
- Customers has: customer_id, region, city, customer_segment, etc.
- Both files share the "customer_id" key

#### Step 3: Perform the Analysis

**Prompt**: "Join transactions with customers and show total revenue by region"

**Result**: You'll get revenue totals like:

- West: $523,421.50
- East: $487,392.30
- Central: $445,678.90
- And so on...

#### Step 4: Dig Deeper

**Prompt**: "Now show me average order value by region"

**Result**: Reveals which regions have higher-value transactions, not just more volume.

## Advanced Patterns

### Multi-Step Analysis

Break complex questions into steps:

```plaintext
First, show me the top 3 product categories by revenue.
Then, for each of those categories, show me which region buys them most.
```

### Comparative Analysis

Compare different segments or periods:

```plaintext
Compare average order value between:
- Gold vs Platinum customer segments
- West vs East regions
- Credit Card vs PayPal payment methods
```

### Filtering Before Aggregation

Narrow your analysis scope:

```plaintext
Filter transactions for orders over $300, 
then show me total revenue by customer segment
```

### Chained Joins

Use results from one analysis to inform the next:

```plaintext
1. Find the top product category by revenue
2. Then analyze that category's sales by customer region
3. Finally, show me the customer segments in the top region
```

## Understanding the Tools

### `list_data_files`

**Purpose**: Discover what data is available  
**When to use**: Start of any analysis session  
**Example**: "What data files can I analyze?"

### `get_data_summary`

**Purpose**: Understand file structure and column types  
**When to use**: Before analyzing or joining files  
**Example**: "Summarize the customers.csv file"

### `analyze_column`

**Purpose**: Deep dive into a specific column  
**When to use**: Understanding distributions, ranges, or unique values  
**Example**: "Analyze the total_amount column"

### `filter_data`

**Purpose**: Subset data based on conditions  
**When to use**: Narrowing focus before analysis  
**Example**: "Show transactions over $500"

### `aggregate_data`

**Purpose**: Summarize data from a single file  
**When to use**: Simple group-by calculations  
**Example**: "Total revenue by product category"

### `join_and_aggregate` ⭐

**Purpose**: Combine multiple files for complex analysis  
**When to use**: Questions that span multiple data sources  
**Example**: "Revenue by customer region" (needs transactions + customers)  
**Why special**: Most business questions require joining data!

## Tips for Best Results

### 1. Start with Exploration

✅ Always begin with `list_data_files` and `get_data_summary`  
❌ Don't jump straight to complex queries

Understanding your data structure first prevents errors and makes analysis more effective.

### 2. Check Column Types

✅ Use `analyze_column` to understand data types  
❌ Don't assume a column is numeric without checking

This prevents aggregation errors and reveals data quality issues.

### 3. Verify Join Keys

✅ Confirm join columns exist in both files  
✅ Check that values match (e.g., "CUST00001" vs "CUST1")  
❌ Don't assume column names mean they're compatible

Use `get_data_summary` on both files before joining.

### 4. Use Descriptive Requests

✅ "Join transactions with customers, group by region, sum total_amount"  
❌ "Analyze sales"

Specific requests get better results faster.

### 5. Filter Smart

✅ Filter before aggregating for performance  
✅ Use appropriate operators (>, <, ==, contains)  
❌ Don't filter on the wrong data type

Example: Use `>` for numbers, `contains` for text.

### 6. Iterate Your Analysis

Start simple, then build complexity:

```plaintext
Step 1: "What's total revenue?" 
Step 2: "Now break that down by region"
Step 3: "For the top region, show me revenue by customer segment"
```

## Troubleshooting

### "File not found"

**Cause**: Incorrect file path  
**Solution**:

- Use `list_data_files` to see available files
- Paths are relative to the datasets directory
- Example: `sales/customers.csv` not `/full/path/customers.csv`

### "Column not found"

**Cause**: Typo or column doesn't exist  
**Solution**:

- Use `get_data_summary` to see exact column names
- Column names are case-sensitive
- Check spelling carefully

### "Join returns no results"

**Cause**: Join keys don't match between files  
**Solution**:

- Verify join column exists in both files
- Use `analyze_column` on join keys to see sample values
- Check for formatting differences (spaces, case, prefixes)

### "Type conversion error"

**Cause**: Trying to do numeric operations on text columns  
**Solution**:

- Use `analyze_column` to check the data type
- Text columns can use `count`, but not `sum` or `avg`
- Numeric operations require numeric columns

### "Empty aggregation results"

**Cause**: Filtered all data out or wrong column  
**Solution**:

- Check your filter conditions aren't too restrictive
- Verify the aggregation column has data
- Use `filter_data` first to see what matches your conditions

## Sample Analysis Sessions

### Session 1: Quick Revenue Check

```plaintext
User: What data files are available?
Claude: [Shows files including transactions.csv]

User: What's our total revenue?
Claude: [Aggregates total_amount in transactions]

User: Break that down by month
Claude: [Groups by transaction_date month]

User: Show me the top 5 months
Claude: [Sorts and displays top 5]
```

### Session 2: Customer Segmentation

```plaintext
User: Summarize customers.csv
Claude: [Shows structure including customer_segment column]

User: How many customers in each segment?
Claude: [Counts by segment: Bronze, Silver, Gold, Platinum]

User: Which segment generates the most revenue?
Claude: [Joins transactions + customers, groups by segment]

User: What's the average order value for Platinum customers?
Claude: [Filters to Platinum, calculates average]
```

### Session 3: Regional Analysis

```plaintext
User: I want to understand regional performance
Claude: [Guides through joining transactions + customers]

User: Show me total revenue by region
Claude: [Displays West, East, Central, North, South totals]

User: Which region has the highest average order value?
Claude: [Calculates avg by region]

User: For the top region, what products sell best?
Claude: [Joins with products, filters to top region]
```

## Extending This Server

Ideas for enhancement:

### 1. Time-Series Analysis

Add date-range filtering and trend calculation:

- Week-over-week growth
- Moving averages
- Seasonal pattern detection

### 2. Advanced Statistics

Beyond basic stats:

- Percentiles (25th, 75th, 95th)
- Correlation analysis
- Outlier detection

### 3. Multi-File Joins

Join 3+ files in one operation:

- transactions + customers + products
- Complex hierarchical data

### 4. Result Export

Save analysis results:

- Create new CSV with results
- Generate summary reports
- Export to JSON

### 5. Data Validation

Add data quality checks:

- Missing value detection
- Duplicate identification
- Range validation

### 6. Visualization Hints

Suggest chart types:

- "This would work well as a bar chart"
- "Consider a time-series line graph"
- Prepare data in visualization-ready format

## Working with Your Own Data

### File Requirements

- **Format**: CSV or JSON
- **Location**: Place in `datasets/` directory
- **Structure**: Consistent column names, one header row (CSV)

### CSV Best Practices

✅ Include header row with column names  
✅ Use consistent data types per column  
✅ Quote text fields containing commas  
✅ Use ISO date format (YYYY-MM-DD)

### JSON Best Practices

✅ Use array of objects format  
✅ Consistent property names across objects  
✅ Avoid deeply nested structures  
✅ Keep numeric values as numbers, not strings

### Example Directory Structure

```plaintext
datasets/
  your-project/
    main-data.csv
    lookup-table.csv
    metadata.json
```

## Security & Privacy

- All data stays local on your machine
- No data is sent to external servers
- Files are read-only by default
- Sandboxed to the datasets directory

## Performance Considerations

- Large files (>100K rows) may be slow
- Joins are memory-intensive with large datasets
- Filter before aggregating when possible
- Consider sampling large datasets for exploration

## Related Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Tutorial 1: Building Your First MCP Server](../../tutorials/01-basic-mcp-server/)
- [File System Server](../file-system/) - Save analysis results
- [Effective Prompting Guide](../../docs/prompting-guide.md)

## Support

Having issues?

1. Check that paths are relative to datasets directory
2. Verify file format (CSV with headers, or JSON array)
3. Use `get_data_summary` to understand your data structure
4. Review MCP logs for detailed error messages

## Example Output Reference

### list_data_files Output

```plaintext
Found 4 data files:

📄 sales/customers.csv (156.3 KB)
📄 sales/products.csv (12.4 KB)
📄 sales/transactions.csv (892.1 KB)
📄 sales/README.json (0.5 KB)
```

### get_data_summary Output

```plaintext
📊 Summary of sales/customers.csv:

Records: 1000
Columns: customer_id, first_name, last_name, email, region, city, signup_date, customer_segment

Column Types:
  • customer_id: text
  • first_name: text
  • last_name: text
  • email: text
  • region: text
  • city: text
  • signup_date: text
  • customer_segment: text
```

### join_and_aggregate Output

```plaintext
🔗 Join and Aggregation Results:

Joined 10000 records
Grouped by: region
Function: sum of total_amount

West: 523421.50
East: 487392.30
Central: 445678.90
North: 412543.20
South: 398765.10
```

This shows you exactly what to expect when running these tools!
