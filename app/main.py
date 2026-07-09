from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Status Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                --card-bg: rgba(30, 41, 59, 0.7);
                --card-border: rgba(255, 255, 255, 0.08);
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --success: #10b981;
                --accent: #6366f1;
                --accent-hover: #4f46e5;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Inter', sans-serif;
                background: var(--bg-gradient);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                width: 100%;
                max-width: 800px;
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                backdrop-filter: blur(12px);
                padding: 40px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.3);
            }

            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--card-border);
                padding-bottom: 24px;
                margin-bottom: 32px;
            }

            h1 {
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.025em;
            }

            .status-badge {
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                color: var(--success);
                padding: 6px 12px;
                border-radius: 9999px;
                font-size: 14px;
                font-weight: 600;
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background: var(--success);
                border-radius: 50%;
                box-shadow: 0 0 8px var(--success);
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }

            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 32px;
            }

            @media (max-width: 640px) {
                .grid { grid-template-columns: 1fr; }
            }

            .card {
                background: rgba(15, 23, 42, 0.4);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 20px;
            }

            .card h2 {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 12px;
                color: var(--text-primary);
            }

            .endpoint-list {
                list-style: none;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .endpoint {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 13px;
            }

            .method {
                font-family: monospace;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 11px;
            }

            .method.post { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
            .method.get { background: rgba(16, 185, 129, 0.15); color: #34d399; }
            .method.put { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
            .method.delete { background: rgba(239, 68, 68, 0.15); color: #f87171; }

            .path {
                color: var(--text-secondary);
                font-family: monospace;
            }

            .actions {
                display: flex;
                justify-content: center;
            }

            .btn {
                display: inline-block;
                background: var(--accent);
                color: white;
                text-decoration: none;
                font-weight: 600;
                padding: 12px 28px;
                border-radius: 8px;
                transition: background 0.2s ease, transform 0.1s ease;
                text-align: center;
                width: 100%;
                max-width: 300px;
            }

            .btn:hover {
                background: var(--accent-hover);
            }

            .btn:active {
                transform: scale(0.98);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Portfolio and Alert Management API</h1>
                <div class="status-badge">
                    <span class="status-dot"></span>
                    <span>Operational</span>
                </div>
            </header>
            
            <div class="grid">
                <div class="card">
                    <h2>Authentication</h2>
                    <ul class="endpoint-list">
                        <li class="endpoint"><span class="path">/register</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/login</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/refresh</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/logout</span><span class="method post">POST</span></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Portfolio Management</h2>
                    <ul class="endpoint-list">
                        <li class="endpoint"><span class="path">/portfolio</span><span class="method get">GET</span></li>
                        <li class="endpoint"><span class="path">/portfolio</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/portfolio/{id}</span><span class="method put">PUT</span></li>
                        <li class="endpoint"><span class="path">/portfolio/{id}</span><span class="method delete">DELETE</span></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Alert Management</h2>
                    <ul class="endpoint-list">
                        <li class="endpoint"><span class="path">/alerts</span><span class="method get">GET</span></li>
                        <li class="endpoint"><span class="path">/alerts</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/alerts/{id}</span><span class="method delete">DELETE</span></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Watchlist</h2>
                    <ul class="endpoint-list">
                        <li class="endpoint"><span class="path">/watchlist</span><span class="method get">GET</span></li>
                        <li class="endpoint"><span class="path">/watchlist</span><span class="method post">POST</span></li>
                        <li class="endpoint"><span class="path">/watchlist/{id}</span><span class="method delete">DELETE</span></li>
                    </ul>
                </div>
            </div>
            
            <div class="actions">
                <a href="/docs" class="btn">View Interactive API Docs</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
