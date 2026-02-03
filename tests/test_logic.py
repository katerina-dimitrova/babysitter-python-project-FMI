import unittest
from models import SitterProfile
from logic import (
    filter_by_city, 
    get_top_rated_sitters, 
    calculate_average_price, 
    has_affordable_sitter, 
    sort_sitters_by_experience, 
    validate_rating
)

class TestSitterLogic(unittest.TestCase):

    def setUp(self):
        s1 = SitterProfile(name="Maria Petrova", hourly_rate=15.50, experience_years=5, rating=4.8)
        s1.city = "Sofia" 
        
        s2 = SitterProfile(name="Ivana Ivanova", hourly_rate=12.00, experience_years=2, rating=4.5)
        s2.city = "Plovdiv"
        
        s3 = SitterProfile(name="Elena Georgieva", hourly_rate=20.00, experience_years=7, rating=4.9)
        s3.city = "Varna"
        
        s4 = SitterProfile(name="Anna Dimitrova", hourly_rate=10.00, experience_years=1, rating=4.0)
        s4.city = "Sofia"

        self.sitters = [s1, s2, s3, s4]

    def test_filter_by_city(self):
        sofia_sitters = filter_by_city(self.sitters, "Sofia")
        self.assertEqual(len(sofia_sitters), 2)
        self.assertTrue(all(s.city == "Sofia" for s in sofia_sitters))

    def test_get_top_rated_sitters(self):
        top_sitters = get_top_rated_sitters(self.sitters, limit=2)
        self.assertEqual(len(top_sitters), 2)
        self.assertEqual(top_sitters[0].rating, 4.9)
        self.assertEqual(top_sitters[1].rating, 4.8)

    def test_calculate_average_price(self):
        avg_price = calculate_average_price(self.sitters)
        expected_avg = (15.50 + 12.00 + 20.00 + 10.00) / 4
        self.assertAlmostEqual(avg_price, expected_avg)

    def test_has_affordable_sitter(self):
        self.assertTrue(has_affordable_sitter(self.sitters, max_budget=12.00))
        self.assertFalse(has_affordable_sitter(self.sitters, max_budget=9.00))

    def test_sort_sitters_by_experience(self):
        sorted_sitters = sort_sitters_by_experience(self.sitters)
        self.assertEqual(sorted_sitters[0].experience_years, 7)
        self.assertEqual(sorted_sitters[-1].experience_years, 1)

    def test_validate_rating(self):
        self.assertTrue(validate_rating(4.5))
        self.assertTrue(validate_rating(0))
        self.assertTrue(validate_rating(5))
        self.assertFalse(validate_rating(-1))
        self.assertFalse(validate_rating(6))
        self.assertFalse(validate_rating("invalid"))

if __name__ == '__main__':
    unittest.main()