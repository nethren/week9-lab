import unittest

from duckfine import DuckFine


class TestDuckFine(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("M001")

    def test_first_two_days_are_free(self):
        for days in (0, 1, 2):
            with self.subTest(days=days):
                self.assertEqual(self.fine.charge(days), 0)

    def test_first_chargeable_day_costs_fifty_cents(self):
        self.assertEqual(self.fine.charge(3), 0.50)

    def test_five_days_late_costs_one_fifty(self):
        self.assertEqual(self.fine.charge(5), 1.50)

    def test_deluxe_doubles_the_fee(self):
        self.assertEqual(self.fine.charge(5, deluxe=True), 3.00)

    def test_standard_fine_is_capped_at_five_dollars(self):
        self.assertEqual(self.fine.charge(100), 5.00)

    def test_deluxe_fine_is_capped_after_doubling(self):
        self.assertEqual(self.fine.charge(30, deluxe=True), 5.00)

    def test_fines_accumulate_for_the_member(self):
        self.fine.charge(5)
        self.fine.charge(5, deluxe=True)
        self.assertEqual(self.fine.total_owed, 4.50)

    def test_accounts_have_independent_totals(self):
        other = DuckFine("M002")
        self.fine.charge(5)
        self.assertEqual(other.total_owed, 0)

    def test_negative_days_rejected_without_changing_total(self):
        self.fine.charge(5)
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 1.50)


if __name__ == "__main__":
    unittest.main()
