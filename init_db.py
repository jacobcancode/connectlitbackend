from __init__ import app, db
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.carPost import CarPost
from model.vehicle import Vehicle, initVehicles
from model.carChat import carChat
from model.carComments import CarComments
from model.mechanicsTips import MechanicsTip
from model.vote import Vote, initVotes
import os
import sys

def init_db():
    try:
        with app.app_context():
            # Drop all tables
            db.drop_all()
            print("Dropped all existing tables")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Initialize default data in order of dependencies
            print("\nInitializing users...")
            admin = initUsers()
            if not admin:
                raise Exception("Failed to initialize admin user")
            
            print("\nInitializing sections...")
            sections = initSections()
            if not sections:
                raise Exception("Failed to initialize sections")
            
            print("\nInitializing groups...")
            groups = initGroups()
            if not groups:
                raise Exception("Failed to initialize groups")
            
            print("\nInitializing channels...")
            channels = initChannels()
            if not channels:
                raise Exception("Failed to initialize channels")
            
            print("\nInitializing posts...")
            posts = initPosts()
            if not posts:
                raise Exception("Failed to initialize posts")
            
            print("\nInitializing votes...")
            votes = initVotes()
            if not votes:
                raise Exception("Failed to initialize votes")
            
            print("\nInitializing vehicles...")
            vehicles = initVehicles()
            if not vehicles:
                raise Exception("Failed to initialize vehicles")
            
            print("\nDefault data initialized successfully!")
            
            # Verify the database file exists
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'volumes', 'user_management.db')
            if not os.path.exists(db_path):
                raise Exception(f"Database file not created at {db_path}")
            print(f"\nDatabase file verified at {db_path}")
            
    except Exception as e:
        print(f"\nError initializing database: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_db() 