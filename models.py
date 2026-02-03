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
    
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(200), nullable=True)

    sitter_profile = db.relationship('SitterProfile', backref='user', uselist=False)
    parent_profile = db.relationship('ParentProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SitterProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False) # Ново поле
    hourly_rate = db.Column(db.Float, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)

class ParentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False) # Ново поле
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