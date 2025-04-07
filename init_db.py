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

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 