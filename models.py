from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20))
    
    city = db.Column(db.String(50), nullable=False)
    neighborhood = db.Column(db.String(50), nullable=True)
    street = db.Column(db.String(100), nullable=True)
    street_number = db.Column(db.String(10), nullable=True)
    block = db.Column(db.String(10), nullable=True)
    entrance = db.Column(db.String(10), nullable=True)
    
    address = db.Column(db.String(255), nullable=False)
    
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    
    sitter_profile = db.relationship('SitterProfile', backref='user', uselist=False)
    parent_profile = db.relationship('ParentProfile', backref='user', uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class SitterProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)

class ParentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    children_count = db.Column(db.Integer, default=1)
    bio = db.Column(db.Text)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sitter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False) 
    end_time = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(20), default='Pending') 
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))


    parent = db.relationship('User', foreign_keys=[parent_id], backref='my_hires')
    sitter = db.relationship('User', foreign_keys=[sitter_id], backref='my_jobs')