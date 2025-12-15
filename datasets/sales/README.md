# Sample Datasets

This directory contains sample datasets for learning and testing MCP servers.

## 📊 Available Datasets

### Sales Data (`sales/`)

Realistic e-commerce transaction data including:

- **customers.csv/json** - Customer demographics and segments
- **products.csv/json** - Product catalog with pricing and ratings
- **transactions.csv/json** - 10,000 purchase transactions

## 🔧 Generating Sample Data

The sample data files are **NOT** included in the repository by design. This allows you to:

- Practice generating data programmatically
- Customize the data to your needs
- Understand how the data is structured

### Generate Sales Data

```bash
cd examples/data-analysis
uv run generate_sales_data.py
```

This will create:

- 1,000 customers with realistic demographics
- 100 products across 5 categories
- 10,000 transactions over the past year
- Metadata file with dataset statistics

### Customize Generation

You can modify `generate_sales_data.py` to:

- Change the number of records
- Adjust date ranges
- Add new product categories
- Modify customer segments
- Change pricing ranges

Example:

```python
# Edit these at the top of generate_sales_data.py
NUM_CUSTOMERS = 5000      # More customers
NUM_PRODUCTS = 200        # More products
NUM_TRANSACTIONS = 50000  # More transactions
```

## 📁 Data Structure

### Customers

```csv
customer_id,first_name,last_name,email,region,city,signup_date,customer_segment
CUST00001,John,Smith,customer1@email.com,North,Seattle,2024-01-15,Gold
```

### Products

```csv
product_id,product_name,category,price,cost,stock_quantity,supplier,rating
PROD0001,Laptop,Electronics,899.99,539.99,45,Supplier 3,4.5
```

### Transactions

```csv
transaction_id,transaction_date,customer_id,product_id,quantity,unit_price,total_amount,discount,payment_method,status
TXN000001,2024-12-15,CUST00234,PROD0015,2,49.99,99.98,0.00,Credit Card,Completed
```

## 🎯 Using the Data

Once generated, you can use the data with the Data Analysis MCP server:

```plaintext
# In Claude Desktop
What data files are available?
Analyze transactions.csv - what's the total revenue?
Show me the top 5 products by sales
Which customers have the highest lifetime value?
```

## 🔄 Regenerating Data

To create fresh data:

```bash
cd examples/data-analysis
python generate_sales_data.py
```

The script will overwrite existing files. Your analysis work won't be affected since it uses the CSV/JSON files.

## 📝 Creating Your Own Datasets

Use the sales data generator as a template to create datasets for:

- Customer support tickets
- Blog posts and content
- Inventory management
- Time series data
- Survey responses

See [PROJECT-IDEAS.md](../projects/PROJECT-IDEAS.md) for suggestions.

## ⚙️ Data Quality

The generated data includes:

- ✅ Realistic distributions
- ✅ Seasonal patterns
- ✅ Some edge cases (outliers, missing values)
- ✅ Consistent relationships (customer → transactions)
- ✅ Proper data types

This makes it suitable for:

- Testing data validation
- Practicing data cleaning
- Learning analysis techniques
- Building dashboards

## 🚀 Next Steps

1. Generate the sample data
2. Explore it with the Data Analysis server
3. Try the example prompts in the tutorials
4. Create your own datasets for your projects

Happy analyzing! 📊
