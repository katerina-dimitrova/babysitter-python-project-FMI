import unittest
from models import Babysitter
from logic import filter_by_city, get_top_rated_sitters, calculate_average_price, has_affordable_sitter, sort_sitters_by_experience, validate_rating

class TestBabysitterLogic(unittest.TestCase):

    def setUp(self):
        self.sitters = [
            Babysitter(1, "Maria Petrova", "Sofia", 15.50, 5, "I love children!", 4.8, 12),
            Babysitter(2, "Ivana Ivanova", "Plovdiv", 12.00, 2, "Student of pedagogy", 4.5, 5),
            Babysitter(3, "Elena Georgieva", "Varna", 20.00, 7, "Experienced nanny", 4.9, 20),
            Babysitter(4, "Anna Dimitrova", "Sofia", 10.00, 1, "New to babysitting", 4.0, 2),
        ]

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