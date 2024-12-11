from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from model.group import Group
from datetime import datetime

class UserCars(db.model):
    
    __tablename__ = 'userCars'
    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _make = db.Column(db.String(255), nullable=True) 
    _model = db.Column(db.String(255), nullable=True) 
    _year = db.Column(db.String(255), nullable=True) 
    _trim = db.Column(db.String(255), nullable=True) 
    _engine_type = db.Column(db.String(255), nullable=True) 
    _color = db.Column(db.String(255), nullable=True) 
    _vin = db.Column(db.String(255), nullable=True) 
    _horsepower = db.Column(db.String(255), nullable=True) 
    _zero_to_sixty = db.Column(db.String(255), nullable=True) 
    _top_speed = db.Column(db.String(255), nullable=True) 

    def __init__(self, uid, make, model, year, trim, engine_type, color, vin, horsepower, zero_to_sixty, top_speed):
        if make not in ['audi, apollo, bentley, bmw, bugatti, ferrari, honda, hyundai, jaguar, koenigsegg, lamborghini, lancia, mclaren, mercedes, pagani, porsche, toyota']:
            return {"message": "Bad Make!!"}, 404

