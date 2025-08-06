import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from dotenv import load_dotenv

load_dotenv()
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = 3306
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "travel_planner")
MYSQL_USER = "root"
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "password")

# Database configuration
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
print(DATABASE_URL)
# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=3600,         # Recycle connections every hour
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Additional connections if needed
    pool_timeout=30,   # Recycle connections every hour
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