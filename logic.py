from models import SitterProfile
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

def get_coords_from_address(address: str):
    try:
        geolocator = Nominatim(user_agent="babysitter_app_project")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        return None, None
    except GeopyError:
        return None, None

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    if not all([lat1, lng1, lat2, lng2]):
        return 999.0 # Return large distance if coords are missing
        
    R = 6371.0 # Earth's radius
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return round(R * c, 2)

def sort_sitters_by_distance(parent_lat, parent_lng, sitters):
    for sitter in sitters:
        sitter.distance = calculate_distance(parent_lat, parent_lng, sitter.user.lat, sitter.user.lng)
    
    return sorted(sitters, key=lambda x: x.distance)

def find_nearby_sitters(current_user_lat: float, current_user_lng: float, all_sitters: list, max_km: float = 10.0) -> list:
    nearby = []
    for sitter in all_sitters:
        dist = calculate_distance(current_user_lat, current_user_lng, sitter.user.lat, sitter.user.lng)
        if dist <= max_km:
            sitter.current_distance = dist
            nearby.append(sitter)
    return sorted(nearby, key=lambda x: x.current_distance)

def filter_by_city(sitters: list[SitterProfile], city: str) -> list[SitterProfile]:
    return [s for s in sitters if s.city.lower() == city.lower()]

def get_top_rated_sitters(sitters: list[SitterProfile], limit: int = 5) -> list[SitterProfile]:
    sorted_sitters = sorted(sitters, key=lambda s: s.rating, reverse=True)
    return sorted_sitters[:limit]

def calculate_average_price(sitters: list[SitterProfile]) -> float:
    try:
        total_price = sum(s.hourly_rate for s in sitters)
        return total_price / len(sitters)
    except ZeroDivisionError:
        return 0.0

def has_affordable_sitter(sitters: list[SitterProfile], max_budget: float) -> bool:
    return any(s.hourly_rate <= max_budget for s in sitters)

def sort_sitters_by_experience(sitters: list[SitterProfile]) -> list[SitterProfile]:
    return sorted(sitters, key=lambda s: s.experience_years, reverse=True)

def validate_rating(rating: float) -> bool:
    try:
        if 0 <= float(rating) <= 5:
            return True
        return False
    except ValueError:
        return False
    

def search_sitters(
    sitters: list[SitterProfile], 
    city: str | None = None, 
    max_price: float | None = None, 
    min_experience: int = 0
) -> list[SitterProfile]:
    filtered = (s for s in sitters if s.experience_years >= min_experience)
    if city:
        filtered = (s for s in filtered if s.city.lower() == city.lower())
    if max_price:
        filtered = (s for s in filtered if s.hourly_rate <= max_price)
    return list(filtered)