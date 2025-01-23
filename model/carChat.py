from sqlite3 import IntegrityError
from datetime import datetime
from __init__ import app, db
from model.user import User

class CarChat(db.Model):
    __tablename__ = 'carChats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _message = db.Column(db.String(255), nullable=False)
    _user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    _timestamp = db.Column('_timestamp', db.DateTime, default=datetime.utcnow)
    
    def __init__(self, message, user_id):
        """
        Constructor, 1st step in object creation.
        
        Args:
            name (str): The name of the group.
            section_id (int): The section to which the group belongs.
            moderators (list, optional): A list of users who are the moderators of the group. Defaults to None.
        """
        self._message = message
        self._user_id = user_id
        self._timestamp = datetime.utcnow()  # Set timestamp when message is created

    @property
    def message(self):
        return self._message
    
    def create(self):
        """
        The create method adds the object to the database and commits the transaction.
        
        Uses:
            The db ORM methods to add and commit the transaction.
        
        Raises:
            Exception: An error occurred when adding the object to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def read(self):
        """Returns chat message data with user details"""
        user = User.query.get(self._user_id)
        if user:
            user_data = user.read()
            username = user_data.get("name", "Unknown User")  # Get actual username
        else:
            username = "Unknown User"
            
        return {
            'id': self.id,
            'message': self._message,
            'username': username,  # Include username in response
            'user_id': self._user_id,
            'timestamp': self._timestamp.isoformat() if self._timestamp else None  # Changed to ISO format
        }

    def update(self):
        """
        The update method commits the transaction to the database.
        
        Uses:
            The db ORM method to commit the transaction.
        
        Raises:
            Exception: An error occurred when updating the object in the database.
        """
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    def delete(self):
        """
        The delete method removes the object from the database and commits the transaction.
        
        Uses:
            The db ORM methods to delete and commit the transaction.
        
        Raises:
            Exception: An error occurred when deleting the object from the database.
        """    
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error