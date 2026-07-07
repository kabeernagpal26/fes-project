from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import engine, Base
from app.routers import auth, portfolio, alert, watchlist

# Set up Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables automatically on startup (perfect for out-of-the-box sqlite run)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup tasks can go here

app = FastAPI(
    title="Portfolio & Alert Management API",
    description="A robust backend service powering a stock market application with JWT auth, portfolio tracking, watchlist management, and price alerts.",
    version="1.0.0",
    lifespan=lifespan
)

# Connect Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Handling for Validation Errors (HTTP 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # Get the field path name (e.g. loc = ('body', 'stockSymbol'))
        field = ".".join([str(loc) for loc in error["loc"][1:]]) if len(error["loc"]) > 1 else str(error["loc"][0])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Input validation failed", "errors": errors}
    )

# Custom Error Handling for General HTTP Exceptions
@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Register/Mount Routers
# Authentication routes at root level as requested (POST /register, /login, /refresh, /logout)
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(alert.router)
app.include_router(watchlist.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Portfolio & Alert Management API",
        "docs_url": "/docs",
        "status": "healthy"
    }
