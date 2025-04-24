import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cfp_tracker.storage.database import engine
from src.cfp_tracker.models.cfp import Base

def init_db():
    """Initialize the database by creating all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 