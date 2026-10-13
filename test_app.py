import unittest

from app import app


class TestFineEndpoint(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_is_ok(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    def test_missing_days_is_a_400_with_an_error(self):
        resp = self.client.get("/fine")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    def test_fine_is_returned_as_json(self):
        resp = self.client.get("/fine?days=5")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"days_late": 5, "deluxe": False, "fee": 1.50})

    def test_deluxe_flag_reaches_the_fee_calculation(self):
        resp = self.client.get("/fine?days=5&deluxe=1")
        self.assertEqual(resp.get_json()["fee"], 3.00)

    def test_non_numeric_days_is_a_400_not_a_crash(self):
        resp = self.client.get("/fine?days=abc")
        self.assertEqual(resp.status_code, 400)

    def test_negative_days_is_a_400_not_a_crash(self):
        resp = self.client.get("/fine?days=-1")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
