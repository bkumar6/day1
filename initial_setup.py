# initial_setup.py

from sqlalchemy.orm import Session
from main import app # Assuming main.py is where you defined Base.metadata.create_all
from database import engine, SessionLocal, Base, get_db
from models import User

# 1. Ensure the tables are created
# This function call creates the 'user_auth.db' file and the 'users' table inside it.
Base.metadata.create_all(bind=engine)

# 2. Function to add the test user
def add_test_user():
    # Use SessionLocal() to get a database session outside of FastAPI dependency
    db: Session = SessionLocal() 
    
    try:
        # Check if the test user already exists
        if db.query(User).filter(User.username == "testuser").first():
            print("Test user already exists. Skipping insertion.")
            return

        # Create a new User instance
        new_user = User(
            username="testuser",
            # NOTE: NEVER store raw passwords in production! 
            # This should be a securely hashed password.
            hashed_password="password123", 
            is_active=True
        )
        
        # Add the new user and commit the transaction
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("Successfully added testuser/password123 to the database.")
        
    except Exception as e:
        print(f"An error occurred during user creation: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    add_test_user()