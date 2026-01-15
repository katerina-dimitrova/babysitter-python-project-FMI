from dataclasses import dataclass

@dataclass
class Babysitter:
    id: int
    name: str
    city: str
    hourly_rate: float
    experience_years: int
    bio: str
    rating: float = 0.0
    reviews_count: int = 0

@dataclass
class Parent:
    id: int
    name: str
    city: str
    needed_hours_per_week: int
    children_count: int
    bio: str