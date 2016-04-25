from django.test import TestCase

from issues.analysis import calc_fixing_time
from issues.tests.db_utils import clear_db, insert_issues_for_estimation


class EstimationTimeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        clear_db()
        insert_issues_for_estimation()

    @classmethod
    def tearDownClass(cls):
        clear_db()

    def test_estimation_for_one_record(self):
        estimated_time = calc_fixing_time(173)
        self.assertTrue(estimated_time == 2578233000)

    def test_estimation_unexisting_service_code(self):
        estimated_time = calc_fixing_time(100500)
        self.assertTrue(estimated_time == 0)

    def test_estimation_two_closed_one_open_case(self):
        estimated_time = calc_fixing_time(175)
        self.assertTrue(estimated_time == 33000)

    def test_estimation_for_all_open_case(self):
        estimated_time = calc_fixing_time(176)
        self.assertTrue(estimated_time == 0)

    def test_estimation_for_all_closed_case(self):
        estimated_time = calc_fixing_time(177)
        self.assertTrue(estimated_time == 1000)
