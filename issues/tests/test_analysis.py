import pytest

from issues.analysis import calc_fixing_time
from issues.tests.db_utils import execute_fixture


@pytest.fixture()
def estimation_issues(db):
    execute_fixture('insert_requests_for_estimation')


@pytest.mark.django_db
def test_estimation_for_one_record(estimation_issues):
    estimated_time = calc_fixing_time(173)
    assert estimated_time == 2578233000


@pytest.mark.django_db
def test_estimation_unexisting_service_code(estimation_issues):
    estimated_time = calc_fixing_time(100500)
    assert estimated_time == 0


@pytest.mark.django_db
def test_estimation_two_closed_one_open_case(estimation_issues):
    estimated_time = calc_fixing_time(175)
    assert estimated_time == 33000


@pytest.mark.django_db
def test_estimation_for_all_open_case(estimation_issues):
    estimated_time = calc_fixing_time(176)
    assert estimated_time == 0


@pytest.mark.django_db
def test_estimation_for_all_closed_case(estimation_issues):
    estimated_time = calc_fixing_time(177)
    assert estimated_time == 1000
