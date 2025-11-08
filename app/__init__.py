"""
Deep Learner AI - FastAPI application with LangGraph agents.

This package provides the core application functionality including:
- FastAPI web framework
- LangGraph-based AI agents
- PostgreSQL database with pgvector
- Celery background tasks
- Redis caching
"""

__version__ = "0.1.0"
__app_name__ = "Deep Learner AI"

# Expose commonly used imports for convenience
from app.settings import settings, get_settings

__all__ = [
    "__version__",
    "__app_name__",
    "settings",
    "get_settings",
]

