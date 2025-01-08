import uuid
from sqlalchemy import Column, Integer, String
from datetime import datetime
from __init__ import app, db

class MechanicTip(db.Model):
    __tablename__ = "mechanictips"

    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _make = db.Column(db.String(255), nullable=True) 
    _model = db.Column(db.String(255), nullable=True) 
    _year = db.Column(db.String(255), nullable=True) 
    _issue = db.Column(db.String(255), nullable=False)
    _tip = db.Column(db.String(255), nullable=False)

    def __init__(self, uid, make, model, year, issue, tip):
        self._uid = uid  # Store the user id
        self._make = make
        self._model = model
        self._year = year
        self._issue = issue
        self._tip = tip

    def __repr__(self):
        return f"MechanicTip(id={self.id}, make='{self._make}', model='{self._model}', year={self._year}, issue='{self._issue}', tip='{self._tip}')"

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
            "make": self._make,
            "model": self._model,
            "year": self._year,
            "issue": self._issue,
            "tip": self._tip
        }

