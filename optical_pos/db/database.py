import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Robust Path Configuration ---
# The project root is defined as the parent directory of the `db` directory.
PROJECT_ROOT = Path(__file__).parent.parent
# Define the path for the data directory
DB_PATH = PROJECT_ROOT / "data"
# Create the data directory if it doesn't exist
DB_PATH.mkdir(parents=True, exist_ok=True)
# Define the full path to the database file
DB_FILE = DB_PATH / "demo.sqlite"
# Default database URL using the absolute path
DEFAULT_DATABASE_URL = f"sqlite:///{DB_FILE.resolve()}"
# --- End Robust Path Configuration ---

# Get the database URL from environment variables, with a default fallback
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Create the SQLAlchemy engine
# The connect_args is specific to SQLite for allowing multithreaded access
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models
Base = declarative_base()

def init_db():
    """
    Initialize the database and create tables.
    This is called from the seed script.
    """
    from . import models
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency function to get a database session.
    This will be used by service layers to interact with the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
