from datetime import datetime, timedelta
from src.cfp_tracker.models.cfp import CFP
from src.cfp_tracker.storage.database import SessionLocal

# Create a test CFP
test_cfp = CFP(
    conference_name="Test Conference 2024",
    submission_deadline=datetime.now() + timedelta(days=30),
    conference_start_date=datetime.now() + timedelta(days=60),
    conference_end_date=datetime.now() + timedelta(days=62),
    location="San Francisco, CA",
    is_virtual=False,
    topics=["python", "testing"],
    submission_url="https://example.com/cfp",
    source="test",
    source_url="https://example.com",
    description="A test conference to verify database connection"
)

# Create a database session
db = SessionLocal()

try:
    # Add the test CFP to the database
    db.add(test_cfp)
    db.commit()
    print("Successfully added test CFP to database")
    
    # Query the CFP back
    retrieved_cfp = db.query(CFP).filter_by(conference_name="Test Conference 2024").first()
    if retrieved_cfp:
        print("\nRetrieved CFP details:")
        print(f"Conference Name: {retrieved_cfp.conference_name}")
        print(f"Submission Deadline: {retrieved_cfp.submission_deadline}")
        print(f"Location: {retrieved_cfp.location}")
        print(f"Topics: {retrieved_cfp.topics}")
        print(f"Source: {retrieved_cfp.source}")
    else:
        print("Failed to retrieve the test CFP")
        
except Exception as e:
    print(f"Error: {str(e)}")
    db.rollback()
finally:
    db.close() 