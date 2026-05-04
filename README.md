# Shopify Backend App

A robust backend for Shopify applications built with FastAPI, SQLAlchemy (Async), and Celery.

## 🚀 Features

- **FastAPI**: High-performance async API framework.
- **Shopify OAuth**: Secure authentication flow for Shopify merchants.
- **Async Shopify Client**: Efficient communication with Shopify GraphQL/REST APIs.
- **Database**: PostgreSQL with SQLAlchemy 2.0 (Async).
- **Background Tasks**: Celery with Redis for heavy lifting (product/order sync).
- **Push Notifications**: Firebase Cloud Messaging (FCM) integration.
- **Webhooks**: Secure handling of Shopify webhooks.

## 📂 Project Structure

```text
app/
├── main.py                    # FastAPI app, middleware, routers
├── config.py                  # Settings via pydantic-settings (.env)
├── dependencies.py            # get_db, get_current_merchant
├── api/
│   └── v1/
│       ├── auth.py            # /auth/install, /auth/callback, /auth/token
│       ├── orders.py          # GET/PATCH /orders
│       ├── products.py        # GET/POST/PATCH/DELETE /products
│       ├── analytics.py       # GET /analytics/revenue, /sessions
│       └── webhooks.py        # POST /webhooks/orders, /webhooks/inventory
├── services/
│   ├── shopify_client.py      # Async GQL client (httpx + gql)
│   ├── auth_service.py        # OAuth flow, token encrypt/store
│   ├── order_service.py       # Business logic wrapping Shopify calls
│   ├── product_service.py
│   ├── analytics_service.py
│   └── notification_service.py # FCM push via firebase-admin
├── models/
│   ├── db/                    # SQLAlchemy ORM models
│   │   ├── merchant.py
│   │   ├── order.py
│   │   └── webhook_log.py
│   └── schemas/               # Pydantic request/response schemas
│       ├── order.py
│       └── product.py
├── tasks/
│   ├── celery_app.py          # Celery + Redis config
│   └── sync_tasks.py          # Periodic product/order sync jobs
├── db/
│   ├── session.py             # Async SQLAlchemy engine
│   └── migrations/            # Alembic versions
└── tests/
    ├── unit/
    └── integration/
```

## 🛠️ Setup

1. **Clone the repository**
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**
   - Copy `.env` template and fill in your Shopify App credentials, Database URL, and Encryption Key.
5. **Database Migrations**
   ```bash
   alembic upgrade head
   ```
6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 Testing

Run tests using pytest:
```bash
pytest
```
