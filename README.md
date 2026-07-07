# Portfolio and Alert Management API

A modular backend service built with FastAPI, SQLAlchemy, and Pydantic for a stock market application. It supports secure JWT authentication, portfolio tracking, watchlist management, and price alerts with caching and rate limiting.

## Technology Stack

- Core Framework: FastAPI
- ORM: SQLAlchemy
- Database: SQLite (default for local development) or PostgreSQL (configured for production)
- Cache: Redis with in-memory fallback
- Hashing: Native bcrypt
- Authentication: JSON Web Tokens (JWT)
- Rate Limiting: SlowAPI
- Testing: Pytest

## Features

- User Authentication: Features user registration, login, token refresh, and token-blacklist logout using JWT.
- Portfolio Management: Full CRUD endpoints to retrieve, add, update, and delete stock holding quantities and average buy prices.
- Alert Management: Create and remove price threshold alerts for stocks based on target conditions (above or below).
- Watchlist Management: Add and remove stock symbols on a watchlist.
- Cache and Rate Limits: Speeds up reads for portfolio and watchlist, invalidates cache automatically on writes, and enforces rate limits of 100 requests per minute.
- Automatic Documentation: Fully documented endpoints accessible via built-in Swagger UI.

## Directory Structure

```
app/
  ├── config.py          # Configuration settings and environment validation
  ├── database.py        # Database connection engine and session dependency
  ├── main.py            # Application entrypoint, middlewares, and exception handling
  ├── models/            # SQLAlchemy database schemas
  ├── schemas/           # Pydantic schemas for data validation and formatting
  ├── services/          # Services for authentication and caching
  └── routers/           # Endpoint controllers for auth, portfolio, alerts, and watchlist
tests/                   # Pytest test suite for validating all API endpoints
Dockerfile               # Application containerization script
docker-compose.yml       # Production-ready PostgreSQL, Redis, and FastAPI configuration
requirements.txt         # List of Python library dependencies
.env                     # Local environment settings
.gitignore               # Git files and directories to ignore
```

## Getting Started

### Prerequisites

You need Python 3.10 or higher installed.

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     .\.venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source .venv/bin/activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the local server using Uvicorn:
```bash
python -m uvicorn app.main:app --reload
```

The application will start on `http://127.0.0.1:8000`.

### API Documentation

Interactive API documentation is generated automatically by FastAPI:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Running the Test Suite

Run the unit tests with pytest:
```bash
python -m pytest
```

## Docker Configuration

To run the application with PostgreSQL and Redis cache using Docker:

1. Build and launch all containers:
   ```bash
   docker-compose up --build
   ```

2. Access the API on port 8000:
   - Base URL: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
