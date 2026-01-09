from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import orders, auth
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging("INFO" if not settings.DEBUG else "DEBUG")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade event-driven order management system with authentication, caching, and event streaming"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Table creation is now handled by Alembic migrations
# Remove the startup event that creates tables automatically

# Include routers
app.include_router(auth.router)
app.include_router(orders.router)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "UP",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Order Management API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

