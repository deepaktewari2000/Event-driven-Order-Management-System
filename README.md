# Production-Grade Order Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **production-ready, event-driven order management system** built with FastAPI, featuring JWT authentication, role-based access control, caching, event streaming, and comprehensive testing.

## 🚀 Features

### Core Functionality
- ✅ **Complete REST API** - Full CRUD operations for orders
- ✅ **Authentication & Authorization** - JWT-based auth with role-based access (Admin/Customer)
- ✅ **Advanced Querying** - Pagination, filtering, and sorting
- ✅ **Event-Driven Architecture** - Kafka integration with Producer/Consumer pattern
- ✅ **Email Notifications** - Automated order confirmations via background workers
- ✅ **Caching Layer** - Redis for performance optimization
- ✅ **Database Migrations** - Alembic for schema management
- ✅ **Email Testing** - MailHog integration for local development

### Production Features
- ✅ **Structured Logging** - JSON logging for production
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **API Documentation** - Auto-generated Swagger/ReDoc
- ✅ **Docker Support** - Full containerization with Docker Compose
- ✅ **Testing Suite** - Unit and integration tests with 90%+ coverage
- ✅ **Type Safety** - Full type hints with Pydantic validation

## 📋 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.100+ |
| **Database** | PostgreSQL 15 + SQLAlchemy (async) |
| **Cache** | Redis 7 |
| **Message Broker** | Apache Kafka |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt (passlib) |
| **Migrations** | Alembic |
| **Email Testing** | MailHog |
| **Testing** | pytest + pytest-asyncio |
| **Containerization** | Docker + Docker Compose |

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI App │─────▶│ PostgreSQL  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                     │
                            ├──────────────▶ Redis (Cache)
                            │
                            └──────────────▶ Kafka (Events)
                                               │
                                               ▼
                                     ┌─────────────────┐
                                     │ Background      │
                                     │ Order Consumer  │
                                     └─────────────────┘
                                               │
                                               ▼
                                     ┌─────────────────┐
                                     │ Email Notification│
                                     │   (MailHog)     │
                                     └─────────────────┘
```

## 🚦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fastapi-order-system
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration (optional for development)
```

### 3. Start with Docker Compose
```bash
# Start all services (PostgreSQL, Redis, Kafka, FastAPI)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Run Database Migrations
```bash
# Inside the container
docker-compose exec app alembic upgrade head

# Or locally (if running without Docker)
alembic upgrade head
```

### 5. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MailHog UI (Emails)**: http://localhost:8025

## 📖 API Usage

### Authentication

#### Register a New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Order Management

#### Create an Order
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "LAPTOP-001",
    "quantity": 2,
    "customer_email": "customer@example.com",
    "shipping_address": "123 Main St, City, Country"
  }'
```

#### List Orders (with Pagination & Filtering)
```bash
# List all orders (paginated)
curl -X GET "http://localhost:8000/orders?skip=0&limit=10" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Filter by status
curl -X GET "http://localhost:8000/orders?status=CONFIRMED" \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# Filter by price range
curl -X GET "http://localhost:8000/orders?min_price=100&max_price=500" \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

#### Get Specific Order
```bash
curl -X GET http://localhost:8000/orders/1 \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

#### Update Order
```bash
curl -X PUT http://localhost:8000/orders/1 \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3,
    "shipping_address": "456 New Address"
  }'
```

#### Update Order Status (Admin Only)
```bash
curl -X PATCH http://localhost:8000/orders/1/status \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "SHIPPED"}'
```

#### Delete Order (Admin Only)
```bash
curl -X DELETE http://localhost:8000/orders/1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

## 🧪 Testing

### Run All Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_auth.py -v

# Run with detailed output
pytest tests/ -vv -s
```

### Test Coverage
The project maintains **90%+ test coverage** including:
- ✅ Authentication flows (register, login, token validation)
- ✅ Order CRUD operations
- ✅ Authorization (role-based access)
- ✅ Pagination and filtering
- ✅ Error handling
- ✅ Service layer logic

## 🔧 Development

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (via Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Code Quality
```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## 📊 Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String | Unique email |
| hashed_password | String | Bcrypt hashed password |
| full_name | String | User's full name |
| role | Enum | ADMIN or CUSTOMER |
| is_active | Boolean | Account status |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Orders Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| product_id | String | Product identifier |
| quantity | Integer | Order quantity |
| total_price | Float | Total order price |
| status | Enum | Order status |
| customer_email | String | Customer email |
| shipping_address | String | Shipping address |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt with salt
- **Role-Based Access Control** - Admin and Customer roles
- **CORS Configuration** - Configurable allowed origins
- **Rate Limiting** - Protection against abuse (via middleware)
- **Input Validation** - Pydantic schemas for all inputs
- **Async Processing** - Background email sending via Kafka

## 📈 Performance Optimizations

- **Async/Await** - Non-blocking I/O operations
- **Connection Pooling** - Efficient database connections
- **Redis Caching** - Reduced database load
- **Database Indexing** - Optimized queries
- **Pagination** - Efficient data retrieval

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f app

# Rebuild containers
docker-compose up -d --build

# Access app container shell
docker-compose exec app /bin/bash

# Run migrations in container
docker-compose exec app alembic upgrade head
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address | `localhost:9092` |
| `SECRET_KEY` | JWT secret key | *Required* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `DEBUG` | Debug mode | `True` |
| `ENVIRONMENT` | Environment name | `development` |
| `SMTP_HOST` | Mail server host | `mailhog` |
| `SMTP_PORT` | Mail server port | `1025` |
| `SMTP_FROM_EMAIL` | Sender address | `noreply@ordersystem.com` |

## 🎯 Resume Highlights

This project demonstrates:

✅ **Backend Engineering** - FastAPI, async Python, SQLAlchemy, Pydantic  
✅ **Security** - JWT authentication, password hashing, RBAC  
✅ **Architecture** - Event-driven design, microservices patterns  
✅ **Database** - Migrations, relationships, indexing, async queries  
✅ **Testing** - Unit tests, integration tests, 90%+ coverage  
✅ **DevOps** - Docker, Docker Compose, containerization  
✅ **Best Practices** - Logging, error handling, documentation  

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI**
