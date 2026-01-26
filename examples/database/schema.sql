-- Drop tables if they exist
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- Customers table
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    region TEXT NOT NULL,
    city TEXT NOT NULL,
    signup_date DATE NOT NULL,
    customer_segment TEXT CHECK(customer_segment IN ('Bronze', 'Silver', 'Gold', 'Platinum'))
);

-- Products table
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    supplier TEXT NOT NULL,
    rating DECIMAL(2, 1) CHECK(rating >= 0 AND rating <= 5)
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_product ON transactions(product_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_products_category ON products(category);

-- Create useful views
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as full_name,
    c.email,
    c.region,
    c.customer_segment,
    COUNT(t.transaction_id) as total_orders,
    SUM(t.total_amount) as total_spent,
    AVG(t.total_amount) as avg_order_value,
    MAX(t.transaction_date) as last_purchase_date
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.region, c.customer_segment;

CREATE VIEW revenue_by_product AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    COUNT(t.transaction_id) as times_sold,
    SUM(t.quantity) as total_quantity_sold,
    SUM(t.total_amount) as total_revenue,
    SUM(t.total_amount) - (SUM(t.quantity) * p.cost) as total_profit
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost;