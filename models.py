from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Babysitter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f"<Babysitter {self.name}>"

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    children_count = db.Column(db.Integer, nullable=False)
    needed_hours_per_week = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Parent {self.name}>"