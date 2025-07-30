from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    location = db.Column(db.String(120))
    capacity = db.Column(db.Integer)
    price_per_hour = db.Column(db.Float)
    spots = db.relationship('ParkingSpot', backref='lot',
                            lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ParkingLot {self.name}>'


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.Integer)
    # e.g., 'Available', 'Occupied'
    status = db.Column(db.String(20), default='Available')
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    booking = db.relationship('Booking', backref='spot', uselist=False)

    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} in Lot {self.lot_id}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))

    def __repr__(self):
        return f'<Booking {self.id}>'
