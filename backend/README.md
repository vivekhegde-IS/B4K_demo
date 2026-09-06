# RetailMate — Backend Service (Member 3)

The **RetailMate Backend Service** is the transactional core for the RetailMate AI retail assistant. It provides product catalog search, real-time inventory management across store locations, order lookup, and deterministic return/exchange eligibility validation and ticket initiation.

---

## Features

- **Product Catalog Search**: Fast partial, case-insensitive search by product name, category, or description.
- **Store Inventory Management**: Multi-store stock tracking with specific aisle and shelf location details.
- **Order Lookup**: Complete order details including line items, quantities, and pricing.
- **Return & Exchange Policy Engine**: Deterministic 5-rule eligibility validation:
  1. Order exists in system.
  2. Product was part of that order.
  3. Order is within the 30-day return/exchange window.
  4. Product has not already been returned or exchanged.
  5. Product category is returnable (excludes non-returnable categories like Gift Cards and Innerwear).
  6. *(Exchange only)* Requested replacement item must exist and have available stock (> 0).
- **Transactional Safety**: Support tickets (`RET-xxxx` / `EXC-xxxx`) are generated and committed atomically. For exchanges, replacement stock is decremented in the same transaction.

---

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (`retailmate.db`)
- **Data Validation**: Pydantic v2
- **Testing**: Pytest + HTTPX

---

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & lifespan
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite engine & session dependency
│   │   └── seed_data.py         # 15 products, 3 stores, 11 demo orders
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py           # Product ORM model
│   │   ├── inventory.py         # Inventory ORM model
│   │   ├── order.py             # Order ORM model
│   │   ├── order_item.py        # OrderItem ORM model
│   │   └── ticket.py            # SupportTicket ORM model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── products.py          # GET /api/products/search
│   │   ├── inventory.py         # GET /api/inventory/{product_id}
│   │   ├── orders.py            # GET /api/orders/{order_id}
│   │   └── returns.py           # POST /api/returns/* and /api/exchanges/*
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product_schema.py    # Product Pydantic schemas
│   │   ├── inventory_schema.py  # Inventory Pydantic schemas
│   │   ├── order_schema.py      # Order Pydantic schemas
│   │   └── return_schema.py     # Return & Exchange request/response schemas
│   └── services/
│       ├── __init__.py
│       ├── inventory_service.py # Stock aggregation & availability helpers
│       └── return_service.py    # Eligibility rules & ticket creation
├── tests/
│   ├── __init__.py
│   └── test_backend.py          # Full test suite (23 tests)
├── requirements.txt
└── README.md
```

---

## Setup & Running

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

The database `retailmate.db` is automatically created and seeded on startup.

- **Interactive API Docs (Swagger)**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Alternative Docs (ReDoc)**: [http://localhost:8002/redoc](http://localhost:8002/redoc)
- **Health Check**: [http://localhost:8002/health](http://localhost:8002/health)

---

## API Endpoints

### Health Check
- **`GET /health`**
  ```json
  {
    "status": "ok",
    "service": "retailmate-backend"
  }
  ```

---

### Products
- **`GET /api/products/search?q={query}`**
  - **Query parameters**: `q` (string, required)
  - **Example**: `GET /api/products/search?q=Nike`
  - **Response**:
    ```json
    {
      "products": [
        {
          "product_id": "P001",
          "name": "Nike Air Max 270",
          "category": "Shoes",
          "price": 4999.0,
          "description": "Black running shoes with Air Max cushioning for all-day comfort"
        },
        {
          "product_id": "P005",
          "name": "Nike Dri-FIT T-Shirt",
          "category": "Clothing",
          "price": 1299.0,
          "description": "Grey moisture-wicking performance t-shirt"
        }
      ]
    }
    ```

---

### Inventory
- **`GET /api/inventory/{product_id}`**
  - **Example**: `GET /api/inventory/P001`
  - **Response**:
    ```json
    {
      "product_id": "P001",
      "available": true,
      "inventory": [
        {
          "inventory_id": "INV001",
          "product_id": "P001",
          "store_location": "Bengaluru Central",
          "aisle": "B",
          "shelf": "4",
          "stock_quantity": 5
        },
        {
          "inventory_id": "INM002",
          "product_id": "P001",
          "store_location": "Bengaluru Mall",
          "aisle": "A",
          "shelf": "2",
          "stock_quantity": 3
        }
      ]
    }
    ```

---

### Orders
- **`GET /api/orders/{order_id}`**
  - **Example**: `GET /api/orders/ORD001`
  - **Response**:
    ```json
    {
      "order_id": "ORD001",
      "customer_id": "CUST001",
      "purchase_date": "2026-09-01",
      "items": [
        {
          "product_id": "P001",
          "product_name": "Nike Air Max 270",
          "quantity": 1,
          "price": 4999.0
        }
      ]
    }
    ```

---

### Returns
- **`POST /api/returns/check`**
  - **Request**:
    ```json
    {
      "order_id": "ORD001",
      "product_id": "P001"
    }
    ```
  - **Response (Eligible)**:
    ```json
    {
      "eligible": true,
      "message": "Your product is eligible for return.",
      "order_id": "ORD001",
      "product_id": "P001",
      "status": "ELIGIBLE",
      "ticket_id": null,
      "reasons": []
    }
    ```

- **`POST /api/returns/initiate`**
  - **Request**:
    ```json
    {
      "order_id": "ORD001",
      "product_id": "P001"
    }
    ```
  - **Response (Initiated)**:
    ```json
    {
      "eligible": true,
      "message": "Your return has been initiated successfully.",
      "order_id": "ORD001",
      "product_id": "P001",
      "ticket_id": "RET-1002",
      "status": "RETURN_INITIATED",
      "reasons": []
    }
    ```

---

### Exchanges
- **`POST /api/exchanges/check`**
  - **Request**:
    ```json
    {
      "order_id": "ORD002",
      "product_id": "P004",
      "replacement_product_id": "P001"
    }
    ```
  - **Response (Eligible)**:
    ```json
    {
      "eligible": true,
      "message": "Your product is eligible for exchange.",
      "order_id": "ORD002",
      "product_id": "P004",
      "replacement_product_id": "P001",
      "status": "ELIGIBLE",
      "ticket_id": null,
      "reasons": []
    }
    ```

- **`POST /api/exchanges/initiate`**
  - **Request**:
    ```json
    {
      "order_id": "ORD002",
      "product_id": "P004",
      "replacement_product_id": "P001"
    }
    ```
  - **Response (Initiated)**:
    ```json
    {
      "eligible": true,
      "message": "Your exchange has been initiated successfully.",
      "order_id": "ORD002",
      "product_id": "P004",
      "replacement_product_id": "P001",
      "ticket_id": "EXC-1001",
      "status": "EXCHANGE_INITIATED",
      "reasons": []
    }
    ```

---

## Seed Data Scenarios

| Order ID | Customer | Purchase Date | Products | Purpose / Demo Scenario |
|----------|----------|---------------|----------|-------------------------|
| `ORD001` | `CUST001` | 5 days ago | `P001` (Nike Air Max) | Return eligible demo |
| `ORD002` | `CUST001` | 3 days ago | `P004` (Levi's Jeans) | Exchange eligible demo |
| `ORD003` | `CUST002` | 45 days ago | `P007` (Galaxy Buds) | Return window expired (`RETURN_WINDOW_EXPIRED`) |
| `ORD004` | `CUST002` | 10 days ago | `P005` (Nike T-Shirt) | Already returned (`RET-1001` exists) |
| `ORD005` | `CUST003` | 7 days ago | `P001`, `P004`, `P010` | Multi-item order |
| `ORD006` | `CUST004` | 2 days ago | `P002` (Adidas Ultraboost) | Recent eligible order |
| `ORD007` | `CUST004` | 60 days ago | `P009` (Apple Watch) | Expired window |
| `ORD008` | `CUST005` | 1 day ago | `P006`, `P012` | Multi-item eligible order |
| `ORD009` | `CUST003` | 15 days ago | `P003`, `P008`, `P013` | Multi-item eligible order |
| `ORD010` | `CUST005` | 35 days ago | `P011` (Ray-Ban) | Barely expired window |
| `ORD011` | `CUST001` | 5 days ago | `P015` (Gift Card) | Non-returnable category (`CATEGORY_NOT_RETURNABLE`) |

---

## Running Tests

Run the automated test suite with pytest:

```bash
cd backend
python -m pytest tests/test_backend.py -v
```
