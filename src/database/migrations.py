"""Database migrations and initialization."""
from pathlib import Path
from .models import create_tables, get_engine


def initialize_database(database_path: str):
    """Initialize the database with all tables.

    Args:
        database_path: Path to SQLite database file
    """
    # Ensure directory exists
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create engine and tables
    engine = get_engine(database_path)
    create_tables(engine)

    print(f"Database initialized at: {database_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "data/competitive_intel.db"

    initialize_database(db_path)
