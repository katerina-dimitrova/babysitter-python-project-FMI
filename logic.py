from models import SitterProfile
import math
from geopy.geocoders import Nominatim


def get_coords_from_address(address: str):
    """Convert a textual address into latitude and longitude using geopy's Nominatim geocoder."""
    if not address:
        return None, None
    try:
        search_query = f"{address}, Bulgaria"

        geolocator = Nominatim(user_agent="babysitter_fmi_project")
        location = geolocator.geocode(search_query, timeout=10)

        if location:
            return location.latitude, location.longitude

        parts = address.split(",")
        if len(parts) > 1:
            fallback = f"{parts[0]}, {parts[-1]}, Bulgaria"
            location = geolocator.geocode(fallback, timeout=10)
            if location:
                return location.latitude, location.longitude

        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the Haversine distance between two geographic coordinates."""
    if not all([lat1, lng1, lat2, lng2]):
        return 999.0

    R = 6371.0  # Earth's radius
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


def sort_sitters_by_distance(
    parent_lat: float, parent_lng: float, sitters: list[SitterProfile]
) -> list[SitterProfile]:
    """Sort sitters based on their distance from a given latitude and longitude."""
    for sitter in sitters:
        sitter.distance = calculate_distance(
            parent_lat, parent_lng, sitter.user.lat, sitter.user.lng
        )

    return sorted(sitters, key=lambda x: getattr(x, "distance", 999))


def calculate_average_price(sitters: list[SitterProfile]) -> float:
    """Calculate the average hourly rate of a list of sitters."""
    try:
        total_price = sum(s.hourly_rate for s in sitters)
        return total_price / len(sitters)
    except ZeroDivisionError:
        return 0.0


def has_affordable_sitter(sitters: list[SitterProfile], max_budget: float) -> bool:
    """Check if there is at least one sitter within the specified budget."""
    return any(s.hourly_rate <= max_budget for s in sitters)


def sort_sitters_by_experience(sitters: list[SitterProfile]) -> list[SitterProfile]:
    """Sort sitters by their years of experience in descending order."""
    return sorted(sitters, key=lambda s: s.experience_years, reverse=True)


def validate_rating(rating: float) -> bool:
    """Validate if the rating is between 0 and 5."""
    try:
        if 0 <= float(rating) <= 5:
            return True
        return False
    except ValueError:
        return False


def search_sitters(
    sitters: list[SitterProfile], city=None, max_price=None, min_experience=0) -> list[SitterProfile]:
    """Filter sitters based on city, maximum price, and minimum experience."""
    filtered = [s for s in sitters if s.experience_years >= min_experience]

    if city:
        filtered = [s for s in filtered if s.user.city.lower() == city.lower()]

    if max_price:
        filtered = [s for s in filtered if s.hourly_rate <= max_price]

    return filtered
