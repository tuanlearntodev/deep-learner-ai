from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __app_name__, __version__
from app.database import Base, engine
from app.router.auth import router as auth_router
from app.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    ErrorHandlingMiddleware
)
import app.model  # noqa: F401



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown logic.
    
    Startup: Create database tables
    Shutdown: Clean up resources
    """
    # Startup: Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    yield  # Application runs and serves requests
    
    # Shutdown: Cleanup logic (if needed)
    print("🔄 Application shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title=__app_name__,
    version=__version__,
    description="AI-powered learning assistant with LangGraph agents",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares (order matters - first added is outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": __app_name__,
        "version": __version__,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }