#!/usr/bin/env python3
"""
Generate sample sales data for testing MCP servers
Creates realistic e-commerce transaction data
"""

import json
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 100
NUM_TRANSACTIONS = 10000
OUTPUT_DIR = Path("../../datasets/sales")

# Sample data
FIRST_NAMES = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", 
               "William", "Jennifer", "James", "Mary", "Christopher", "Patricia", "Daniel"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
              "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"]

PRODUCT_CATEGORIES = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Camera", "Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes", "Hat"],
    "Home": ["Coffee Maker", "Blender", "Vacuum", "Lamp", "Pillow", "Blanket"],
    "Books": ["Fiction Novel", "Cookbook", "Biography", "Self-Help", "Textbook"],
    "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Bicycle", "Tennis Racket"]
}

REGIONS = ["North", "South", "East", "West", "Central"]
CITIES = {
    "North": ["Seattle", "Portland", "Spokane"],
    "South": ["Austin", "Houston", "Miami"],
    "East": ["New York", "Boston", "Philadelphia"],
    "West": ["San Francisco", "Los Angeles", "San Diego"],
    "Central": ["Chicago", "Denver", "Minneapolis"]
}

def generate_customers(n: int) -> list:
    """Generate customer data"""
    customers = []
    for i in range(1, n + 1):
        region = random.choice(REGIONS)
        customers.append({
            "customer_id": f"CUST{i:05d}",
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "email": f"customer{i}@email.com",
            "region": region,
            "city": random.choice(CITIES[region]),
            "signup_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "customer_segment": random.choice(["Bronze", "Silver", "Gold", "Platinum"])
        })
    return customers

def generate_products(n: int) -> list:
    """Generate product catalog"""
    products = []
    product_id = 1
    
    for category, items in PRODUCT_CATEGORIES.items():
        for item in items:
            base_price = random.uniform(10, 500)
            products.append({
                "product_id": f"PROD{product_id:04d}",
                "product_name": f"{item}",
                "category": category,
                "price": round(base_price, 2),
                "cost": round(base_price * 0.6, 2),  # 40% margin
                "stock_quantity": random.randint(0, 500),
                "supplier": f"Supplier {random.randint(1, 10)}",
                "rating": round(random.uniform(3.5, 5.0), 1)
            })
            product_id += 1
            
            # Generate variants if not enough products
            if product_id <= n and random.random() > 0.5:
                variant_price = base_price * random.uniform(0.8, 1.2)
                products.append({
                    "product_id": f"PROD{product_id:04d}",
                    "product_name": f"{item} - Premium",
                    "category": category,
                    "price": round(variant_price, 2),
                    "cost": round(variant_price * 0.6, 2),
                    "stock_quantity": random.randint(0, 300),
                    "supplier": f"Supplier {random.randint(1, 10)}",
                    "rating": round(random.uniform(4.0, 5.0), 1)
                })
                product_id += 1
    
    return products[:n]

def generate_transactions(customers: list, products: list, n: int) -> list:
    """Generate transaction data"""
    transactions = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, n + 1):
        transaction_date = start_date + timedelta(days=random.randint(0, 365))
        customer = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        
        # Add some seasonality and trends
        month = transaction_date.month
        seasonal_factor = 1.0
        if month in [11, 12]:  # Holiday season
            seasonal_factor = 1.3
        elif month in [6, 7]:  # Summer
            seasonal_factor = 1.1
        
        transactions.append({
            "transaction_id": f"TXN{i:06d}",
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": product["price"],
            "total_amount": round(product["price"] * quantity * seasonal_factor, 2),
            "discount": round(random.uniform(0, 0.15) if random.random() > 0.7 else 0, 2),
            "payment_method": random.choice(["Credit Card", "Debit Card", "PayPal", "Apple Pay"]),
            "status": random.choice(["Completed", "Completed", "Completed", "Pending", "Cancelled"])
        })
    
    return sorted(transactions, key=lambda x: x["transaction_date"])

def save_data(customers: list, products: list, transactions: list):
    """Save data to CSV and JSON files"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    with open(OUTPUT_DIR / "customers.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)
    
    with open(OUTPUT_DIR / "products.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)
    
    with open(OUTPUT_DIR / "transactions.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)
    
    # Save as JSON
    with open(OUTPUT_DIR / "customers.json", 'w') as f:
        json.dump(customers, f, indent=2)
    
    with open(OUTPUT_DIR / "products.json", 'w') as f:
        json.dump(products, f, indent=2)
    
    with open(OUTPUT_DIR / "transactions.json", 'w') as f:
        json.dump(transactions, f, indent=2)
    
    # Create metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "num_customers": len(customers),
        "num_products": len(products),
        "num_transactions": len(transactions),
        "date_range": {
            "start": transactions[0]["transaction_date"],
            "end": transactions[-1]["transaction_date"]
        },
        "total_revenue": sum(t["total_amount"] for t in transactions),
        "description": "Synthetic e-commerce sales data for testing and learning"
    }
    
    with open(OUTPUT_DIR / "README.json", 'w') as f:
        json.dump(metadata, f, indent=2)

def main():
    print("Generating sample sales data...")
    
    customers = generate_customers(NUM_CUSTOMERS)
    print(f"✓ Generated {len(customers)} customers")
    
    products = generate_products(NUM_PRODUCTS)
    print(f"✓ Generated {len(products)} products")
    
    transactions = generate_transactions(customers, products, NUM_TRANSACTIONS)
    print(f"✓ Generated {len(transactions)} transactions")
    
    save_data(customers, products, transactions)
    print(f"\n✅ Data saved to {OUTPUT_DIR}/")
    print(f"   - customers.csv / customers.json")
    print(f"   - products.csv / products.json")
    print(f"   - transactions.csv / transactions.json")
    print(f"   - README.json (metadata)")
    
    # Print sample statistics
    total_revenue = sum(t["total_amount"] for t in transactions)
    avg_order = total_revenue / len(transactions)
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Average Order: ${avg_order:.2f}")
    print(f"   Date Range: {transactions[0]['transaction_date']} to {transactions[-1]['transaction_date']}")

if __name__ == "__main__":
    main()