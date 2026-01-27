#!/usr/bin/env python3
"""
Mock API Server
Simulates e-commerce and analytics APIs for testing the Web API MCP Server
No external API accounts needed - runs locally on port 8000
"""

import random
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock E-commerce & Analytics API")

# In-memory data store (simulates a real API's backend)
REQUEST_COUNTS: Dict[str, int] = {}
RATE_LIMIT = 100  # requests per minute per API key

# Sample data matching the sales datasets
PRODUCTS_DATA = [
    {
        "id": f"PROD{str(i).zfill(4)}",
        "name": f"Product {i}",
        "category": random.choice(["Electronics", "Clothing", "Home", "Books", "Sports"]),
        "price": round(random.uniform(10, 500), 2),
        "stock": random.randint(0, 100),
        "sku": f"SKU-{i:04d}",
        "rating": round(random.uniform(3.0, 5.0), 1),
    }
    for i in range(1, 46)
]

ORDERS_DATA = [
    {
        "id": f"ORD{str(i).zfill(5)}",
        "customer_id": f"CUST{str(random.randint(1, 1000)).zfill(4)}",
        "product_id": random.choice(PRODUCTS_DATA)["id"],
        "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
        "total": round(random.uniform(20, 1000), 2),
        "created_at": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
        "items": random.randint(1, 5),
    }
    for i in range(1, 101)
]

ANALYTICS_DATA = {
    "page_views": [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "views": random.randint(1000, 5000),
            "unique_visitors": random.randint(500, 2000),
            "bounce_rate": round(random.uniform(30, 70), 1),
        }
        for i in range(30)
    ],
    "traffic_sources": [
        {"source": "organic", "visitors": random.randint(5000, 10000), "percentage": 45},
        {"source": "direct", "visitors": random.randint(3000, 6000), "percentage": 25},
        {"source": "social", "visitors": random.randint(2000, 4000), "percentage": 15},
        {"source": "paid", "visitors": random.randint(1000, 3000), "percentage": 10},
        {"source": "referral", "visitors": random.randint(500, 1500), "percentage": 5},
    ],
}


def check_rate_limit(api_key: str) -> bool:
    """Simple rate limiting check"""
    now = datetime.now().minute
    key = f"{api_key}:{now}"
    
    REQUEST_COUNTS[key] = REQUEST_COUNTS.get(key, 0) + 1
    
    # Clean old entries
    for k in list(REQUEST_COUNTS.keys()):
        if k != key:
            del REQUEST_COUNTS[k]
    
    return REQUEST_COUNTS[key] <= RATE_LIMIT


def verify_api_key(authorization: Optional[str]) -> str:
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer YOUR_API_KEY")
    
    api_key = authorization.replace("Bearer ", "")
    
    if api_key not in ["test_api_key", "demo_key_12345"]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not check_rate_limit(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 100 requests per minute.")
    
    return api_key


# E-commerce Endpoints

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "Mock E-commerce & Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "orders": "/api/orders",
            "inventory": "/api/inventory/{product_id}",
            "analytics": "/api/analytics/report",
        },
        "authentication": "Use header: Authorization: Bearer YOUR_API_KEY",
        "valid_keys": ["test_api_key", "demo_key_12345"],
    }


@app.get("/api/products")
def list_products(
    authorization: Optional[str] = Header(None),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List products with optional filters"""
    verify_api_key(authorization)
    
    # Apply filters
    filtered_products = PRODUCTS_DATA.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    if in_stock is not None:
        if in_stock:
            filtered_products = [p for p in filtered_products if p["stock"] > 0]
        else:
            filtered_products = [p for p in filtered_products if p["stock"] == 0]
    
    # Pagination
    total = len(filtered_products)
    paginated_products = filtered_products[offset:offset + limit]
    
    return {
        "data": paginated_products,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        },
    }


@app.get("/api/products/{product_id}")
def get_product(
    product_id: str,
    authorization: Optional[str] = Header(None),
):
    """Get a specific product by ID"""
    verify_api_key(authorization)
    
    product = next((p for p in PRODUCTS_DATA if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return {"data": product}


@app.get("/api/inventory/{product_id}")
def check_inventory(
    product_id: str,
    authorization: Optional[str] = Header(None),
):
    """Check inventory for a specific product"""
    verify_api_key(authorization)
    
    product = next((p for p in PRODUCTS_DATA if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return {
        "data": {
            "product_id": product_id,
            "product_name": product["name"],
            "stock": product["stock"],
            "available": product["stock"] > 0,
            "low_stock_warning": product["stock"] < 10,
            "last_updated": datetime.now().isoformat(),
        }
    }


@app.get("/api/orders")
def list_orders(
    authorization: Optional[str] = Header(None),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List orders with optional filters"""
    verify_api_key(authorization)
    
    # Apply filters
    filtered_orders = ORDERS_DATA.copy()
    
    if status:
        filtered_orders = [o for o in filtered_orders if o["status"].lower() == status.lower()]
    
    if customer_id:
        filtered_orders = [o for o in filtered_orders if o["customer_id"] == customer_id]
    
    # Pagination
    total = len(filtered_orders)
    paginated_orders = filtered_orders[offset:offset + limit]
    
    return {
        "data": paginated_orders,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        },
    }


@app.get("/api/orders/{order_id}")
def get_order(
    order_id: str,
    authorization: Optional[str] = Header(None),
):
    """Get a specific order by ID"""
    verify_api_key(authorization)
    
    order = next((o for o in ORDERS_DATA if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return {"data": order}


# Analytics Endpoints

@app.post("/api/analytics/report")
def get_analytics_report(
    authorization: Optional[str] = Header(None),
    metric: str = Query(..., description="Metric to report on: page_views, traffic_sources"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get analytics report for specified metric"""
    verify_api_key(authorization)
    
    if metric == "page_views":
        data = ANALYTICS_DATA["page_views"]
        
        # Filter by date range if provided
        if start_date:
            data = [d for d in data if d["date"] >= start_date]
        if end_date:
            data = [d for d in data if d["date"] <= end_date]
        
        total_views = sum(d["views"] for d in data)
        total_visitors = sum(d["unique_visitors"] for d in data)
        avg_bounce_rate = sum(d["bounce_rate"] for d in data) / len(data) if data else 0
        
        return {
            "data": data,
            "summary": {
                "total_page_views": total_views,
                "total_unique_visitors": total_visitors,
                "average_bounce_rate": round(avg_bounce_rate, 1),
                "date_range": {
                    "start": data[-1]["date"] if data else None,
                    "end": data[0]["date"] if data else None,
                },
            },
        }
    
    elif metric == "traffic_sources":
        return {
            "data": ANALYTICS_DATA["traffic_sources"],
            "summary": {
                "total_visitors": sum(s["visitors"] for s in ANALYTICS_DATA["traffic_sources"]),
                "top_source": max(ANALYTICS_DATA["traffic_sources"], key=lambda x: x["visitors"])["source"],
            },
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown metric: {metric}. Available: page_views, traffic_sources",
        )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mock API Server on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔑 Valid API Keys: test_api_key, demo_key_12345")
    uvicorn.run(app, host="0.0.0.0", port=8000)