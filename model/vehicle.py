from datetime import datetime
from sqlalchemy.exc import IntegrityError

from __init__ import app, db

class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _vin = db.Column(db.String(17), unique=True, nullable=False)
    _make = db.Column(db.String(100), nullable=False)
    _model = db.Column(db.String(100), nullable=False)
    _year = db.Column(db.Integer, nullable=False)
    _engine_type = db.Column(db.String(50), nullable=False)
    _date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, vin, make, model, year, engine_type, uid):
        self._vin = vin
        self._make = make
        self._model = model
        self._year = year
        self._engine_type = engine_type
        self._uid = uid  # Pass the user ID

    # Property for vin
    @property
    def vin(self):
        return self._vin

    @vin.setter
    def vin(self, value):
        self._vin = value

    def __repr__(self):
        return (f"Vehicle(id={self.id}, user_id={self._uid}), vin={self.vin}, make={self._make}, "
                f"model={self._model}, year={self._year}, engine_type={self._engine_type}, "
                f"date_added={self._date_added})")

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
            "user_id": self._uid,
            "vin": self.vin,  # Use property here
            "make": self._make,
            "model": self._model,
            "year": self._year,
            "engine_type": self._engine_type,
            "date_added": self._date_added,
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}") and value is not None:
                setattr(self, f"_{key}", value)
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

def initVehicles():
    """
    Initialize default vehicles and ensure the Vehicle table has valid data before inserting more entries.
    """
    with app.app_context():
        db.create_all()

        # Add default vehicles
        vehicles = [
            Vehicle(
                vin="3VWJP7ATXEM256789",
                make="Volkswagen",
                model="Beetle",
                year=2014,
                engine_type="Electric",
                uid=3
            )
        ]

        for vehicle in vehicles:
            try:
                vehicle.create()  # Assuming you have a `create()` method in your `Vehicle` class
                print(f"Added vehicle: {vehicle.vin}")
            except IntegrityError as e:
                db.session.rollback()
                print(f"IntegrityError: {e} - Could not add vehicle {vehicle.vin}")
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e} - Could not add vehicle {vehicle.vin}")
