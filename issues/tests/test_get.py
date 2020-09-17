import iso8601
import pytest

from issues.gis import determine_gissiness
from issues.models import Issue
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response, verify_issue

GISSY = determine_gissiness()


def test_get_requests(testing_issues, mf_api_client):
    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT), schema=LIST_OF_ISSUES_SCHEMA)
    assert len(content) == Issue.objects.count()


def test_get_by_service_request_id(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': '1982hglaqe8pdnpophff'}),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert len(content) == 1
    verify_issue(content[0])


def test_get_by_service_request_ids(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {'service_request_id': '1982hglaqe8pdnpophff,2981hglaqe8pdnpoiuyt'}
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert {c['service_request_id'] for c in content} == {
        '1982hglaqe8pdnpophff',
        '2981hglaqe8pdnpoiuyt'
    }
    assert all(verify_issue(c) for c in content)


def test_get_by_unexisting_request_id(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': 'unexisting_req_id'}),
    )
    assert not content


def test_get_by_service_code(testing_issues, mf_api_client):
    service_code = '171'
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_code': service_code}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    for issue in content:
        assert verify_issue(issue)
        assert issue['service_code'] == service_code


def test_get_by_start_date(testing_issues, mf_api_client):
    start_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 3

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'start_date': start_date}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == expected_number_of_requests
    for issue in content:
        assert verify_issue(issue)
        assert iso8601.parse_date(issue['requested_datetime']) > iso8601.parse_date(start_date)


def test_get_by_end_data(testing_issues, mf_api_client):
    end_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 1

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'end_date': end_date}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == expected_number_of_requests
    for issue in content:
        assert verify_issue(issue)
        assert iso8601.parse_date(issue['requested_datetime']) < iso8601.parse_date(end_date)


def test_get_by_status(testing_issues, mf_api_client):
    issue_status = 'open'
    expected_number_of_requests = 2

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'status': issue_status}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == expected_number_of_requests
    for issue in content:
        assert verify_issue(issue)
        assert issue['status'] == issue_status


@pytest.mark.parametrize("extensions", (False, True))
def test_get(testing_issues, mf_api_client, extensions):
    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'format': format,
                'service_request_id': '1982hglaqe8pdnpophff',
                'extensions': ('true' if extensions else 'false'),
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert verify_issue(content[0])
    if extensions:
        assert 'extended_attributes' in content[0]
    else:
        assert 'extended_attributes' not in content[0]


def test_get_by_updated_after(testing_issues, mf_api_client):
    updated_after = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 3

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'updated_after': updated_after}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == expected_number_of_requests
    for issue in content:
        assert verify_issue(issue)
        assert iso8601.parse_date(issue['updated_datetime']) > iso8601.parse_date(updated_after)


def test_get_by_updated_before(testing_issues, mf_api_client):
    updated_before = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 1

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'updated_before': updated_before}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == expected_number_of_requests
    for issue in content:
        assert verify_issue(issue)
        assert iso8601.parse_date(issue['updated_datetime']) < iso8601.parse_date(updated_before)


def test_get_within_radius(testing_issues, mf_api_client):
    lat = 60.187394
    long = 24.940773
    radius = 1000
    expected_number_of_requests = 3

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'lat': lat, 'long': long, 'radius': radius}),
        schema=(LIST_OF_ISSUES_SCHEMA if GISSY else None),
        status_code=(500 if not GISSY else 200)
    )

    if not GISSY:
        return

    assert len(content) == expected_number_of_requests

    for issue in content:
        assert verify_issue(issue)
        assert float(issue['distance']) < 1000


@pytest.mark.parametrize('flip_lat', (False, True))
@pytest.mark.parametrize('flip_long', (False, True))
@pytest.mark.parametrize('sep', ";,")
def test_get_with_bbox(testing_issues, mf_api_client, flip_lat, flip_long, sep):
    longs = (24.768, 24.77)
    lats = (60.191, 60.194)
    if flip_lat:
        lats = lats[::-1]
    if flip_long:
        longs = longs[::-1]

    bbox_string = sep.join(str(c) for c in (longs[0], lats[0], longs[1], lats[1]))

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'bbox': bbox_string}),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    assert len(content) == 1
    assert content[0]['service_request_id'] == '9374kdfksdfhsdfasdf'

    for issue in content:
        assert verify_issue(issue)
