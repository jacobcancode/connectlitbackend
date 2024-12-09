from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from model.group import Group

class CarPost(db.Model):
    """
    CarPost Model
    
    The Post class represents an individual contribution or discussion within a group.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the post.
        _title (db.Column): A string representing the title of the post.
        _description (db.Column): A string representing the description of the post.
        _uid (db.Column): An integer representing the user who created the post.
        _car_type (db.Column): An string representing the group to which the post belongs (gas, electric, hybrid, dream).
        _image_url_table (db.Column): A JSON array of strings representing the url path to the image contained in the post
    """
    __tablename__ = 'carPosts'
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _description = db.Column(db.String(255), nullable=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _car_type = db.Column(db.String(255), nullable=False)
    _image_url_table = db.Column(db.String(255), nullable=False)

    def __init__(self, title, description, uid, car_type, image_url_table):
        """
        Constructor, 1st step in object creation.
        
        Args:
            title (str): The title of the post.
            description (str): The description of the post.
            uid (int): The user who created the post.
            car_type (str): The type of car (gas, electric, hybrid, dream).
            image_url_table (list): The url path to the image
        """
        if car_type not in ['gas', 'electric', 'hybrid', 'dream']:
            raise ValueError('Car type must be one of gas, electric, hybrid, dream')
        
        self._title = title
        self._description = description
        self._uid = uid
        self._car_type = car_type
        self._image_url_table = image_url_table

    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr(post) built-in function, where post is an instance of the Post class.
        
        Returns:
            str: A text representation of how to create the object.
        """
        return f"Post(id={self.id}, title={self._title}, description={self._description}, uid={self._uid}, car_type={self._car_type}, image_url_table={self._image_url_table})"
    
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
        except Exception as error:
            db.session.rollback()
            raise error
        
    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        
        Uses:
            The Group.query and User.query methods to retrieve the group and user objects.
        
        Returns:
            dict: A dictionary containing the post data, including user and group names.
        """
        user = User.query.get(self._uid)
        data = {
            "id": self.id,
            "title": self._title,
            "description": self._description,
            "uid": user.name if user else None,
            "car_type": self._car_type,
            "image_url_table": self._image_url_table
        }
        return data
    
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