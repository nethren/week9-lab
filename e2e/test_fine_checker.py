import os
import unittest

from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000/")


class TestFineChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    def test_member_checks_the_fine_for_a_deluxe_duck(self):
        # From the brief: 5 days late = 3 chargeable days x $0.50,
        # doubled for Deluxe = $3.00
        page = self.page
        page.goto(BASE_URL)
        page.get_by_label("Days late").fill("5")
        page.get_by_label("Deluxe duck").check()
        page.get_by_role("button", name="Check fine").click()
        result = page.get_by_role("status")
        expect(result).to_have_text("Your fine is $3.00")


if __name__ == "__main__":
    unittest.main()
