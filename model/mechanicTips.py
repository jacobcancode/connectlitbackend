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

    def __init__(self, make, model, year, issue, tip):
        self.make = make
        self.model = model
        self.year = year
        self.issue = issue
        self.tip = tip

    def __repr__(self):
        return f"MechanicTip(id={self.id}, make='{self.make}', model='{self.model}', year={self.year}, issue='{self.issue}', tip='{self.tip}')"

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
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "issue": self.issue,
            "tip": self.tip
        }


