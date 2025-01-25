from datetime import datetime
from __init__ import app, db
from sqlalchemy.exc import IntegrityError


class UserItem(db.Model):
    __tablename__ = "user_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    user_input = db.Column(db.Text, nullable=True)  # Added column to store user input
    date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, name, user_id, user_input=None, date_added=None):
        self.name = name
        self.user_id = user_id
        self.user_input = user_input
        if date_added:
            self.date_added = datetime.fromisoformat(date_added)

    def __repr__(self):
        return f"UserItem(id={self.id}, user_id={self.user_id}, name={self.name}, user_input={self.user_input}, date_added={self.date_added})"

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error

    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "user_input": self.user_input,
            "date_added": self.date_added.isoformat() if self.date_added else None,
        }

    def update(self, data, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    @staticmethod
    def restore(data):
        for post_data in data:
            _ = post_data.pop('id', None)  # Remove 'id' from post_data
            name = post_data.get("name", None)
            post = UserItem.query.filter_by(name=name).first()
            if post:
                post.update(post_data)
            else:
                post = UserItem(post_data["name"], post_data["user_id"], post_data["user_input"], post_data["date_added"])
                post.update(post_data)
                post.create()

def initDefaultUser():
    """
    Initializes the database with default UserItem entries.
    """
    with app.app_context():
        try:
            # Create database and tables
            db.create_all()

            # Default tester data for the UserItem table
            default_items = [
                UserItem(name='2000s Jeep', user_id=1, ),
            ]

            # Add default items to the database
            for item in default_items:
                try:
                    item.create()  # Add the item using the `create` method in the model
                except IntegrityError:
                    db.session.rollback()
                    print(f"Item '{item.name}' already exists or there was an issue adding it.")

        except Exception as e:
            print(f"An error occurred during initialization: {str(e)}")
