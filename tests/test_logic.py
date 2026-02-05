import datetime
import unittest
from models import Booking, SitterProfile, User
from logic import (
    get_coords_from_address,
    has_affordable_sitter,
    search_sitters, 
    calculate_average_price,
    sort_sitters_by_distance, 
    sort_sitters_by_experience, 
    validate_rating,
    calculate_distance
)

class TestSitterLogic(unittest.TestCase):

    def setUp(self):
        u1 = User(city="София", lat=42.6977, lng=23.3217)
        u2 = User(city="Пловдив", lat=42.1354, lng=24.7453)
        u3 = User(city="Варна", lat=43.2141, lng=27.9147)
        u4 = User(city="София", lat=42.6977, lng=23.3217)

        s1 = SitterProfile(name="Maria Petrova", hourly_rate=15.50, experience_years=5, rating=4.8, user=u1)
        s2 = SitterProfile(name="Ivana Ivanova", hourly_rate=12.00, experience_years=2, rating=4.5, user=u2)
        s3 = SitterProfile(name="Elena Georgieva", hourly_rate=20.00, experience_years=7, rating=4.9, user=u3)
        s4 = SitterProfile(name="Anna Dimitrova", hourly_rate=10.00, experience_years=1, rating=4.0, user=u4)

        self.sitters = [s1, s2, s3, s4]

    def test_search_sitters_by_city(self) -> None:
        sofia_sitters = search_sitters(self.sitters, city="София")
        self.assertEqual(len(sofia_sitters), 2)
        self.assertTrue(all(s.user.city == "София" for s in sofia_sitters))

    def test_search_sitters_by_price(self) -> None:
        affordable = search_sitters(self.sitters, max_price=13.00)
        self.assertEqual(len(affordable), 2) # Ivana (12) и Anna (10)
        self.assertTrue(all(s.hourly_rate <= 13.00 for s in affordable))

    def test_calculate_distance(self) -> None:
        dist = calculate_distance(42.6977, 23.3217, 42.1354, 24.7453)
        self.assertGreater(dist, 130)
        self.assertLess(dist, 160)

    def test_calculate_average_price(self) -> None:
        avg_price = calculate_average_price(self.sitters)
        expected_avg = (15.50 + 12.00 + 20.00 + 10.00) / 4
        self.assertAlmostEqual(avg_price, expected_avg)

    def test_sort_sitters_by_experience(self) -> None:
        sorted_sitters = sort_sitters_by_experience(self.sitters)
        self.assertEqual(sorted_sitters[0].experience_years, 7)
        self.assertEqual(sorted_sitters[-1].experience_years, 1)

    def test_validate_rating(self) -> None:
        self.assertTrue(validate_rating(4.5))
        self.assertTrue(validate_rating(5.0))
        self.assertFalse(validate_rating(6.0))
        self.assertFalse(validate_rating("not a number"))
        
        
    def test_calculate_average_price_empty(self) -> None:
        """Test the average price calculation with an empty list of sitters."""
        self.assertEqual(calculate_average_price([]), 0.0)

    def test_calculate_distance_invalid_coords(self) -> None:
        """Test the distance calculation with invalid coordinates, expecting a default large distance value."""
        dist = calculate_distance(None, 23.32, 42.69, 23.32)
        self.assertEqual(dist, 999.0)

    def test_has_affordable_sitter(self) -> None:
        """Test the function that checks for affordable sitters, ensuring it correctly identifies when a sitter is within the budget and when no sitters are affordable."""
        self.assertTrue(has_affordable_sitter(self.sitters, 11.0))
        self.assertFalse(
            has_affordable_sitter(self.sitters, 5.0)
        )
        
    def test_sort_sitters_by_distance(self) -> None:
        """Test the sorting of sitters by distance from a given location, verifying that the closest sitter is correctly identified and that the distance is calculated as expected."""
        parent_lat, parent_lng = 42.6977, 23.3217
        sorted_list = sort_sitters_by_distance(parent_lat, parent_lng, self.sitters)
        self.assertEqual(sorted_list[0].name, "Maria Petrova")
        self.assertEqual(sorted_list[0].distance, 0.0)
        
    def test_get_coords_from_address_empty(self) -> None:
        """Test the geocoding function with an empty address, expecting it to return None for both latitude and longitude."""
        lat, lng = get_coords_from_address("")
        self.assertIsNone(lat)
        self.assertIsNone(lng)
        
    def test_search_sitters_by_experience(self) -> None:
        """Test the search function for sitters by minimum experience, ensuring that it correctly filters sitters based on their years of experience."""
        experienced = search_sitters(self.sitters, min_experience=6)
        self.assertEqual(len(experienced), 1)
        self.assertEqual(experienced[0].name, "Elena Georgieva")

    def test_user_password_hashing(self) -> None:
        """Test the password hashing and verification methods of the User model."""
        user = User(email="test@example.com")
        user.set_password("my_secure_password")
        self.assertNotEqual(user.password_hash, "my_secure_password")
        self.assertTrue(user.check_password("my_secure_password"))
        self.assertFalse(user.check_password("wrong_password"))
        
    def test_user_sitter_relationship(self) -> None:
        """Test the relationship between User and SitterProfile models."""
        user = User(email="sitter@test.com", city="Пловдив", address="Център")
        sitter = SitterProfile(name="Maria", hourly_rate=15.0, user=user)
        
        self.assertEqual(user.sitter_profile.name, "Maria")
        self.assertEqual(sitter.user.email, "sitter@test.com")
        
    def test_booking_creation(self) -> None:
        """Test the creation of a Booking instance and its default status."""
        start_dt = datetime.datetime.now()
        end_dt = start_dt + datetime.timedelta(hours=2)
        booking = Booking(parent_id=1, sitter_id=2, start_time=start_dt, end_time=end_dt, status='Pending')
    
        self.assertEqual(booking.status, "Pending")

if __name__ == '__main__':
    unittest.main()