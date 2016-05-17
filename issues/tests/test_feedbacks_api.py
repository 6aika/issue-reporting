import jsonschema
import pytest
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.crypto import get_random_string

from issues.models import Issue
from issues.models.jurisdictions import Jurisdiction
from issues.tests.db_utils import execute_fixture
from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.utils import get_data_from_response

ISSUE_LIST_ENDPOINT = reverse_lazy('georeport/v2:issue-list')


def assert_all_valid_issues(issue_list):
    for obj in issue_list:
        jsonschema.validate(obj, ISSUE_SCHEMA)


@pytest.fixture()
def testing_issues(db):
    execute_fixture('insert_requests')


def test_get_requests(testing_issues, mf_api_client):
    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT))
    assert len(content) == Issue.objects.count()
    assert_all_valid_issues(content)


def test_get_by_service_request_id(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': '1982hglaqe8pdnpophff'})
    )
    assert len(content) == 1
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'
    assert_all_valid_issues(content)


def test_get_by_service_request_ids(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {'service_request_id': '1982hglaqe8pdnpophff,2981hglaqe8pdnpoiuyt'}
        )
    )
    assert len(content) == 2
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'
    assert content[1]['service_request_id'] == '2981hglaqe8pdnpoiuyt'
    assert_all_valid_issues(content)


def test_get_by_unexisting_request_id(testing_issues, mf_api_client):
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': 'unexisting_req_id'})
    )
    assert not content


def test_get_by_service_code(testing_issues, mf_api_client):
    service_code = '171'
    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'service_code': service_code})
    )

    for issue in content:
        assert issue['service_code'] == service_code
    assert_all_valid_issues(content)


def test_get_by_start_date(testing_issues, mf_api_client):
    start_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 3

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'start_date': start_date})
    )

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['requested_datetime'] > start_date


def test_get_by_end_data(testing_issues, mf_api_client):
    end_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 1

    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT, {'end_date': end_date}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for request in content:
        assert request['requested_datetime'] < end_date


def test_get_by_status(testing_issues, mf_api_client):
    issue_status = 'open'
    expected_number_of_requests = 2

    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT, {'status': issue_status}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['status'] == issue_status


@pytest.mark.parametrize("extensions", (False, True))
def test_get(testing_issues, mf_api_client, extensions):
    if extensions:
        pytest.xfail("extensions not implemented rn")  # TODO: Fix me
    content = get_data_from_response(mf_api_client.get(
        ISSUE_LIST_ENDPOINT,
        {
            'format': format,
            'service_request_id': '1982hglaqe8pdnpophff',
            'extensions': ('true' if extensions else 'false'),
        }
    ))

    assert_all_valid_issues(content)
    if extensions:
        assert 'extended_attributes' in content[0]
    else:
        assert 'extended_attributes' not in content[0]


def test_get_by_updated_after(testing_issues, mf_api_client):
    updated_after = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 3

    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT, {'updated_after': updated_after}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] > updated_after


def test_get_by_updated_before(testing_issues, mf_api_client):
    updated_before = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 1

    content = get_data_from_response(mf_api_client.get(ISSUE_LIST_ENDPOINT, {'updated_before': updated_before}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] < updated_before


def test_get_within_radius(testing_issues, mf_api_client):
    lat = 60.187394
    long = 24.940773
    radius = 1000
    expected_number_of_requests = 3

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {'lat': lat, 'long': long, 'radius': radius})
    )
    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests

    for issue in content:
        assert float(issue['distance']) < 1000


@pytest.mark.django_db
def test_post_issue_no_jurisdiction(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()
    for attempt in [1, 2]:
        issue = get_data_from_response(
            mf_api_client.post(ISSUE_LIST_ENDPOINT, {
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
                "description": get_random_string(),
            }),
            201
        )
        assert_all_valid_issues([issue])
        assert Issue.objects.filter(identifier=issue['service_request_id']).exists()
        assert Jurisdiction.objects.filter(identifier="default").exists()  # default Jurisdiction was created
        assert Jurisdiction.objects.count() == 1

        issue = get_data_from_response(mf_api_client.get(
            reverse('georeport/v2:issue-detail', kwargs={'identifier': issue['service_request_id']}),
        ))
        assert_all_valid_issues([issue])


@pytest.mark.django_db
def test_post_issue_multi_jurisdiction(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    Jurisdiction.objects.create(identifier="j1", name="j1")
    Jurisdiction.objects.create(identifier="j2", name="j2")
    # Can't post without a Jurisdiction when there are multiple
    get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, {
            "service_code": random_service.service_code,
            "lat": 30,
            "long": 30,
            "description": get_random_string(),
        }),
        400
    )
    for j in Jurisdiction.objects.all():
        # Can't post without a Jurisdiction when there are multiple
        issue = get_data_from_response(
            mf_api_client.post(ISSUE_LIST_ENDPOINT, {
                "jurisdiction_id": j.identifier,
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
                "description": get_random_string(),
            }),
            201
        )
        assert_all_valid_issues([issue])
        assert Issue.objects.get(identifier=issue["service_request_id"]).jurisdiction == j


@pytest.mark.django_db
def test_get_issue_multi_jurisdiction_filters_correctly(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    jurisdictions = [
        Jurisdiction.objects.create(identifier="j%s" % x, name="j%s" % x)
        for x in range(4)
    ]
    for j in jurisdictions:
        for x in range(5):
            Issue.objects.create(
                jurisdiction=j,
                service=random_service,
                description=get_random_string(),
            )
    for j in jurisdictions:
        issues = get_data_from_response(
            mf_api_client.get(ISSUE_LIST_ENDPOINT, {'jurisdiction_id': j.identifier}),
        )
        assert_all_valid_issues(issues)
        # Only getting the Issues for the requested Jurisdiction:
        assert len(issues) == Issue.objects.filter(jurisdiction=j).count()
