from __init__ import app, db
from model.user import User
from model.section import Section
from model.group import Group
from model.channel import Channel
from model.post import Post
from model.carPost import CarPost
from model.vehicle import Vehicle
from model.carChat import carChat
from model.carComments import CarComments
from model.mechanicsTips import MechanicsTip
from model.vote import Vote
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
            
            # Verify the database file exists
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'volumes', 'user_management.db')
            if not os.path.exists(db_path):
                raise Exception(f"Database file not created at {db_path}")
            print(f"Database file verified at {db_path}")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_db() 