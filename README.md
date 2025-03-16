# E-Commerce Backend

A modern, scalable e-commerce backend built with Flask, SQLAlchemy, and Keycloak.

## Architecture

This project follows Clean Architecture and Domain-Driven Design principles to create a maintainable, testable, and scalable application.

### Architectural Layers

![Architecture Diagram](https://miro.medium.com/max/1400/1*0R0r_pLlFNcmYFOm3H_-Lw.png)

The application is organized into the following layers:

1. **Domain Layer** - Core business logic and rules
   - Domain Models
   - Value Objects
   - Domain Services
   - Domain Exceptions

2. **Application Layer** - Orchestration of domain objects
   - Use Cases
   - Commands and Queries
   - Application Services

3. **Infrastructure Layer** - Technical capabilities and external services
   - Database Models and Repositories
   - External Service Integrations (Keycloak, Google Drive)
   - Technical Implementations

4. **Interfaces Layer** - User interfaces and API endpoints
   - API Controllers
   - Serializers/Schemas
   - Middleware

### Directory Structure

```
backend/
├── app/                           # Application package
│   ├── __init__.py                # App initialization
│   ├── config.py                  # Configuration management
│   ├── domain/                    # Domain layer (business logic)
│   │   ├── __init__.py
│   │   ├── models/                # Domain models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   ├── services/              # Domain services
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py
│   │   ├── exceptions.py          # Domain-specific exceptions
│   │   ├── value_objects/         # Value objects
│   │   │   ├── __init__.py
│   │   │   ├── address.py
│   │   │   ├── money.py
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── database/              # Database infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── models/            # SQLAlchemy ORM models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── product.py
│   │   │   │   ├── order.py
│   │   │   ├── repositories/      # Repository implementations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_repository.py
│   │   │   │   ├── product_repository.py
│   │   │   │   ├── order_repository.py
│   │   ├── external/              # External services
│   │   │   ├── __init__.py
│   │   │   ├── keycloak/          # Keycloak integration
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py
│   │   │   │   ├── auth_provider.py
│   │   │   ├── storage/           # Storage integration
│   │   │   │   ├── __init__.py
│   │   │   │   ├── google_drive.py
│   ├── interfaces/                # Interface layer
│   │   ├── __init__.py
│   │   ├── api/                   # API interfaces
│   │   │   ├── __init__.py
│   │   │   ├── v1/                # API v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── products.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── users.py
│   │   │   ├── middleware/        # API middleware
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── error_handler.py
│   │   ├── serializers/           # Data serializers/schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── user.py
│   ├── application/               # Application layer
│   │   ├── __init__.py
│   │   ├── use_cases/             # Use cases/application services
│   │   │   ├── __init__.py
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── login.py
│   │   │   │   ├── register.py
│   │   │   ├── products/
│   │   │   ├── orders/
│   ├── core/                      # Core application components
│   │   ├── __init__.py
│   │   ├── logging.py             # Logging configuration
│   │   ├── pagination.py          # Pagination utilities
│   │   ├── security.py            # Security utilities
│   │   ├── validators.py          # Common validators
├── migrations/                    # Database migrations
├── tests/                         # Tests
│   ├── __init__.py
│   ├── conftest.py                # Test configuration
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
├── .env.example                   # Example environment variables
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose configuration
├── requirements.txt               # Python dependencies
├── run.py                         # Application entry point
```

### Key Architectural Principles

1. **Clean Architecture**:
   - Clear separation between domain, application, infrastructure, and interface layers
   - Dependencies point inward (domain doesn't depend on infrastructure)
   - Business rules isolated in the domain layer

2. **Domain-Driven Design**:
   - Rich domain models with business logic
   - Value objects for immutable concepts
   - Domain services for operations that don't belong to a single entity
   - Repositories as collection-like interfaces for domain objects

3. **CQRS Pattern** (Command Query Responsibility Segregation):
   - Separate command (write) and query (read) operations
   - Optimized data models for each type of operation

4. **Repository Pattern**:
   - Abstract data access behind repository interfaces
   - Domain layer works with repositories, not direct database access
   - Makes testing easier with mock repositories

5. **Use Case Driven**:
   - Each business operation is a distinct use case
   - Use cases orchestrate domain objects to fulfill business requirements
   - Clear entry points for all application functionality

6. **Dependency Injection**:
   - Services receive their dependencies rather than creating them
   - Improves testability and flexibility
   - Allows for easy swapping of implementations

## Features

- User authentication with Keycloak (JWT)
- Product management
- Order processing
- User management
- File storage with Google Drive

## Authentication Flow

The application uses Keycloak for authentication and authorization:

1. **Registration**:
   - User submits registration form
   - Backend validates input
   - User is created in Keycloak
   - User is created in application database

2. **Login**:
   - User submits login credentials
   - Keycloak validates credentials and returns tokens
   - Backend stores user in database if not exists
   - Frontend stores tokens for subsequent requests

3. **Token Refresh**:
   - When access token expires, refresh token is used
   - New access token is obtained without re-authentication

4. **Logout**:
   - Refresh token is invalidated in Keycloak
   - Frontend removes stored tokens

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ecommerce-backend.git
   cd ecommerce-backend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your configuration.

4. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

### Keycloak Configuration

1. Access Keycloak admin console at http://localhost:8080
2. Login with the admin credentials from your `.env` file
3. Create a new realm
4. Create a new client with the following settings:
   - Client ID: your client ID from `.env`
   - Client Protocol: openid-connect
   - Access Type: confidential
   - Valid Redirect URIs: http://localhost:5000/*
5. Note the client secret from the Credentials tab
6. Create roles (e.g., user, admin)
7. Update your `.env` file with the realm and client secret

## API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and invalidate tokens

### Product Endpoints

- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products` - Create product (admin only)
- `PUT /api/v1/products/{id}` - Update product (admin only)
- `DELETE /api/v1/products/{id}` - Delete product (admin only)

### Order Endpoints

- `GET /api/v1/orders` - List user's orders
- `GET /api/v1/orders/{id}` - Get order details
- `POST /api/v1/orders` - Create order
- `PUT /api/v1/orders/{id}/status` - Update order status (admin only)
- `POST /api/v1/orders/{id}/cancel` - Cancel order

### User Endpoints

- `GET /api/v1/users` - List users (admin only)
- `GET /api/v1/users/{id}` - Get user details
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8
```

## Deployment

The application is containerized and can be deployed to any container orchestration platform like Kubernetes or AWS ECS.

### Environment Variables

See `.env.example` for required environment variables.

## License

This project is licensed under the MIT License - see the LICENSE file for details.