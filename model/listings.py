from datetime import datetime
from __init__ import db

class UserItem(db.Model):
    __tablename__ = "user_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    user_input = db.Column(db.Text, nullable=True)  # Added column to store user input
    date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, name, user_id, user_input=None):
        self.name = name
        self.user_id = user_id
        self.user_input = user_input

    # Property for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __repr__(self):
        return f"UserItem(id={self.id}, user_id={self.user_id}, name={self.name}, user_input={self.user_input}, date_added={self.date_added})"

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "user_input": self.user_input,
            "date_added": self.date_added,
        }

    def update(self, **kwargs):
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
