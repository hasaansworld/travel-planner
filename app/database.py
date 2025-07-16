from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Database configuration
DATABASE_URL = 'mysql+pymysql://user:password@db:3306/travel_planner'

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    pool_pre_ping=True,  # Enables automatic reconnection
    pool_recycle=3600,   # Recycle connections every hour
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session

def get_db() -> Session:
    """Get database session (for direct use)"""
    return Session(engine)

# Export the main objects
db_engine = engine
db_session = get_session