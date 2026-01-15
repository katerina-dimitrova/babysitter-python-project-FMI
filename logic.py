from models import Babysitter

def filter_by_city(sitters: list[Babysitter], city: str) -> list[Babysitter]:
    return [s for s in sitters if s.city.lower() == city.lower()]

def get_top_rated_sitters(sitters: list[Babysitter], limit: int = 5) -> list[Babysitter]:
    sorted_sitters = sorted(sitters, key=lambda s: s.rating, reverse=True)
    return sorted_sitters[:limit]

def calculate_average_price(sitters: list[Babysitter]) -> float:
    if not sitters:
        return 0.0
    total = sum(s.hourly_rate for s in sitters)
    return total / len(sitters)

def has_affordable_sitter(sitters: list[Babysitter], max_budget: float) -> bool:
    return any(s.hourly_rate <= max_budget for s in sitters)

def sort_sitters_by_experience(sitters: list[Babysitter]) -> list[Babysitter]:
    return sorted(sitters, key=lambda s: s.experience_years, reverse=True)

def validate_rating(rating: float) -> bool:
    try:
        if 0 <= float(rating) <= 5:
            return True
        return False
    except ValueError:
        return False