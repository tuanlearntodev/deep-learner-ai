"""
Database configuration and session management.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.settings import settings

# Create SQLAlchemy engine
# echo=settings.DEBUG: Log SQL queries in debug mode
# pool_pre_ping=True: Verify connections before using (handles connection drops)
# pool_size=5: Number of persistent connections
# max_overflow=10: Additional connections when pool is exhausted
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create SessionLocal class for database sessions
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Don't auto-flush before queries (more control)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
  