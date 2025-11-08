from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __app_name__, __version__
from app.database import Base, engine



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