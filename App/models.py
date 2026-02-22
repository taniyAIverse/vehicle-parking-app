from . import db
from flask_login import UserMixin
from datetime import datetime
class User(UserMixin, db.Model):
    __tablename__= "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique = True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(60), nullable= False)
    address = db.Column(db.String(250), nullable= False)
    pincode = db.Column(db.Integer, nullable= False)
    reservations = db.relationship('Reserving_Spot', back_populates='user')

    def get_id(self):
        return f"user-{self.id}"

    def get_role(self):
        return "user"
    
    
class Parking_Lot(db.Model):
    __tablename__= "parking_lot"
    id= db.Column(db.Integer, primary_key= True)
    prime_location_name = db.Column(db.String(250), nullable= False)
    price = db.Column(db.Float, nullable= False)
    address = db.Column(db.String(250), nullable= False)
    pincode = db.Column(db.Integer, nullable= False)
    max_spots = db.Column(db.Integer, nullable= False)
    is_active = db.Column(db.Boolean, default=True)
    spots= db.relationship('Parking_Spot', back_populates = "lot")

class Parking_Spot(db.Model):
    __tablename__= "parking_spot"
    id = db.Column(db.Integer, primary_key = True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id", ondelete="CASCADE"), nullable=False)
    status= db.Column(db.String(1), default="A", nullable=False)
    lot= db.relationship('Parking_Lot', back_populates= "spots")
    is_active = db.Column(db.Boolean, default=True)
    reservations = db.relationship("Reserving_Spot", back_populates="spot")


class Reserving_Spot(db.Model):
    __tablename__ = "reserving_spot"
    id= db.Column(db.Integer, primary_key= True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spot.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    parking_time = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    leaving_time = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    vehicle_no = db.Column(db.String(20), nullable=False)
    user= db.relationship('User', back_populates='reservations')
    spot = db.relationship('Parking_Spot', back_populates= "reservations")

class Admin(UserMixin, db.Model):
    __tablename__= "admin"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable= False, unique= True)
    password = db.Column(db.String(100), nullable= False)
    name= db.Column(db.String(50), nullable=False)

    def get_id(self):
        return f"admin-{self.id}"
    def get_role(self):
        return "admin"
    

