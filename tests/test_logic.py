import unittest
from models import SitterProfile, User
from logic import (
    search_sitters, 
    calculate_average_price, 
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

    def test_search_sitters_by_city(self):
        sofia_sitters = search_sitters(self.sitters, city="София")
        self.assertEqual(len(sofia_sitters), 2)
        self.assertTrue(all(s.user.city == "София" for s in sofia_sitters))

    def test_search_sitters_by_price(self):
        affordable = search_sitters(self.sitters, max_price=13.00)
        self.assertEqual(len(affordable), 2) # Ivana (12) и Anna (10)
        self.assertTrue(all(s.hourly_rate <= 13.00 for s in affordable))

    def test_calculate_distance(self):
        dist = calculate_distance(42.6977, 23.3217, 42.1354, 24.7453)
        self.assertGreater(dist, 130)
        self.assertLess(dist, 160)

    def test_calculate_average_price(self):
        avg_price = calculate_average_price(self.sitters)
        expected_avg = (15.50 + 12.00 + 20.00 + 10.00) / 4
        self.assertAlmostEqual(avg_price, expected_avg)

    def test_sort_sitters_by_experience(self):
        sorted_sitters = sort_sitters_by_experience(self.sitters)
        self.assertEqual(sorted_sitters[0].experience_years, 7)
        self.assertEqual(sorted_sitters[-1].experience_years, 1)

    def test_validate_rating(self):
        self.assertTrue(validate_rating(4.5))
        self.assertTrue(validate_rating(5.0))
        self.assertFalse(validate_rating(6.0))
        self.assertFalse(validate_rating("not a number"))

if __name__ == '__main__':
    unittest.main()