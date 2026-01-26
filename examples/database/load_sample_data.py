#!/usr/bin/env python3
"""
Load sample sales data from CSV files into SQLite database
Run this script to create the sample database for testing
"""

import csv
import sqlite3
from pathlib import Path


def create_database(db_path: Path, csv_dir: Path):
    """Create SQLite database from CSV files"""
    
    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating database: {db_path}")
    
    # Create customers table
    print("\n📊 Creating customers table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            region TEXT,
            city TEXT,
            signup_date DATE,
            customer_segment TEXT
        )
    """)
    
    # Load customers data
    customers_file = csv_dir / "customers.csv"
    if customers_file.exists():
        with open(customers_file, 'r') as f:
            reader = csv.DictReader(f)
            customers = list(reader)
            cursor.executemany(
                """
                INSERT OR REPLACE INTO customers 
                (customer_id, first_name, last_name, email, region, city, signup_date, customer_segment)
                VALUES (:customer_id, :first_name, :last_name, :email, :region, :city, :signup_date, :customer_segment)
                """,
                customers
            )
        print(f"   ✓ Loaded {len(customers)} customers")
    else:
        print(f"   ⚠️  Warning: {customers_file} not found")
    
    # Create products table
    print("\n📦 Creating products table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL,
            cost REAL,
            stock_quantity INTEGER,
            supplier TEXT,
            rating REAL
        )
    """)
    
    # Load products data
    products_file = csv_dir / "products.csv"
    if products_file.exists():
        with open(products_file, 'r') as f:
            reader = csv.DictReader(f)
            products = list(reader)
            cursor.executemany(
                """
                INSERT OR REPLACE INTO products
                (product_id, product_name, category, price, cost, stock_quantity, supplier, rating)
                VALUES (:product_id, :product_name, :category, :price, :cost, :stock_quantity, :supplier, :rating)
                """,
                products
            )
        print(f"   ✓ Loaded {len(products)} products")
    else:
        print(f"   ⚠️  Warning: {products_file} not found")
    
    # Create transactions table
    print("\n💳 Creating transactions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date DATE,
            customer_id TEXT,
            product_id TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            discount REAL,
            payment_method TEXT,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    # Load transactions data
    transactions_file = csv_dir / "transactions.csv"
    if transactions_file.exists():
        with open(transactions_file, 'r') as f:
            reader = csv.DictReader(f)
            transactions = list(reader)
            cursor.executemany(
                """
                INSERT OR REPLACE INTO transactions
                (transaction_id, transaction_date, customer_id, product_id, quantity, 
                 unit_price, total_amount, discount, payment_method, status)
                VALUES (:transaction_id, :transaction_date, :customer_id, :product_id, 
                        :quantity, :unit_price, :total_amount, :discount, :payment_method, :status)
                """,
                transactions
            )
        print(f"   ✓ Loaded {len(transactions)} transactions")
    else:
        print(f"   ⚠️  Warning: {transactions_file} not found")
    
    # Create indexes for better query performance
    print("\n🔍 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
    print("   ✓ Indexes created")
    
    # Create useful views
    print("\n👁️  Creating views...")
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS revenue_by_product AS
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            COUNT(t.transaction_id) as total_orders,
            SUM(t.quantity) as units_sold,
            SUM(t.total_amount) as total_revenue,
            AVG(t.total_amount) as avg_order_value
        FROM products p
        LEFT JOIN transactions t ON p.product_id = t.product_id
        WHERE t.status = 'Completed'
        GROUP BY p.product_id, p.product_name, p.category
    """)
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS customer_summary AS
        SELECT 
            c.customer_id,
            c.first_name,
            c.last_name,
            c.email,
            c.region,
            c.city,
            c.customer_segment,
            COUNT(t.transaction_id) as total_orders,
            SUM(CASE WHEN t.status = 'Completed' THEN t.total_amount ELSE 0 END) as total_spent,
            MAX(t.transaction_date) as last_order_date
        FROM customers c
        LEFT JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.customer_id
    """)
    print("   ✓ Views created")
    
    # Commit and close
    conn.commit()
    
    # Print summary statistics
    print("\n📈 Database Summary:")
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"   Customers: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"   Products: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    print(f"   Transactions: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT SUM(total_amount) FROM transactions WHERE status = 'Completed'")
    revenue = cursor.fetchone()[0]
    print(f"   Total Revenue: ${revenue:,.2f}" if revenue else "   Total Revenue: $0.00")
    
    conn.close()
    print(f"\n✅ Database created successfully at: {db_path}")


def main():
    """Main entry point"""
    # Determine paths
    script_dir = Path(__file__).parent
    db_path = script_dir / "sample_data" / "sales.db"
    csv_dir = script_dir.parent.parent / "datasets" / "sales"
    
    if not csv_dir.exists():
        print("❌ Error: Could not find datasets/sales directory")
        print("\nPlease ensure the sales dataset exists at:")
        print(f"  {csv_dir}")
        print("\nGenerate it by running:")
        print("  cd datasets/sales")
        print("  uv run ../../examples/data-analysis/generate_sales_data.py")
        return
    
    print(f"Using CSV files from: {csv_dir}")
    
    # Create datasets directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()
    
    # Create new database
    create_database(db_path, csv_dir)


if __name__ == "__main__":
    main()