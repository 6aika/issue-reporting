import jsonschema
import pytest
from django.core.urlresolvers import reverse_lazy

from issues.models import Issue, Jurisdiction
from issues.tests.db_utils import execute_fixture
from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.utils import get_data_from_response

ISSUE_LIST_ENDPOINT = reverse_lazy('api/v1:issue-list')


def assert_all_valid_issues(issue_list):
    for obj in issue_list:
        jsonschema.validate(obj, ISSUE_SCHEMA)


@pytest.fixture()
def testing_issues(db):
    execute_fixture('insert_requests')


def test_get_requests(testing_issues, api_client):
    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT))
    assert len(content) == Issue.objects.count()
    assert_all_valid_issues(content)


def test_get_by_service_request_id(testing_issues, api_client):
    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': '1982hglaqe8pdnpophff'})
    )
    assert len(content) == 1
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'
    assert_all_valid_issues(content)


def test_get_by_service_request_ids(testing_issues, api_client):
    content = get_data_from_response(
        api_client.get(
            ISSUE_LIST_ENDPOINT,
            {'service_request_id': '1982hglaqe8pdnpophff,2981hglaqe8pdnpoiuyt'}
        )
    )
    assert len(content) == 2
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'
    assert content[1]['service_request_id'] == '2981hglaqe8pdnpoiuyt'
    assert_all_valid_issues(content)


def test_get_by_unexisting_request_id(testing_issues, api_client):
    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': 'unexisting_req_id'})
    )
    assert content == []


def test_get_by_service_code(testing_issues, api_client):
    service_code = '171'
    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'service_code': service_code})
    )

    for issue in content:
        assert issue['service_code'] == service_code
    assert_all_valid_issues(content)


def test_get_by_start_date(testing_issues, api_client):
    start_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 3

    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'start_date': start_date})
    )

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['requested_datetime'] > start_date


def test_get_by_end_data(testing_issues, api_client):
    end_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 1

    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT, {'end_date': end_date}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for request in content:
        assert request['requested_datetime'] < end_date


def test_get_by_status(testing_issues, api_client):
    issue_status = 'open'
    expected_number_of_requests = 2

    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT, {'status': issue_status}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['status'] == issue_status


def test_by_description(testing_issues, api_client):
    search = 'some'

    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT, {'search': search}))
    assert_all_valid_issues(content)
    assert search.lower() in content[0]['description'].lower()


def test_get_with_extensions(testing_issues, api_client):
    content = get_data_from_response(api_client.get(
        ISSUE_LIST_ENDPOINT,
        {'service_request_id': '1982hglaqe8pdnpophff', 'extensions': 'true'}
    ))

    assert_all_valid_issues(content)
    assert 'extended_attributes' in content[0]


def test_get_without_extensions(testing_issues, api_client):
    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'service_request_id': '1982hglaqe8pdnpophff'})
    )

    assert_all_valid_issues(content)
    assert 'extended_attributes' not in content[0]


def test_get_by_updated_after(testing_issues, api_client):
    updated_after = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 3

    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT, {'updated_after': updated_after}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] > updated_after


def test_get_by_updated_before(testing_issues, api_client):
    updated_before = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 1

    content = get_data_from_response(api_client.get(ISSUE_LIST_ENDPOINT, {'updated_before': updated_before}))

    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] < updated_before


def test_get_by_service_object(testing_issues, api_client):
    service_object_id = '10844'
    service_object_type = 'http://www.hel.fi/servicemap/v2'

    content = get_data_from_response(api_client.get(
        ISSUE_LIST_ENDPOINT,
        {
            'extensions': 'true',
            'service_object_id': 'service_object_id',
            'service_object_type': 'service_object_type'
        }
    ))

    assert_all_valid_issues(content)
    for issue in content:
        assert issue['extended_attributes']['service_object_id'] == service_object_id
        assert issue['extended_attributes']['service_object_type'] == service_object_type


def test_get_by_service_object_id_without_type(testing_issues, api_client):
    service_object_id = '10844'

    get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'service_object_id': service_object_id}),
        status_code=400
    )


def test_get_within_radius(testing_issues, api_client):
    lat = 60.187394
    long = 24.940773
    radius = 1000
    expected_number_of_requests = 3

    content = get_data_from_response(
        api_client.get(ISSUE_LIST_ENDPOINT, {'lat': lat, 'long': long, 'radius': radius})
    )
    assert_all_valid_issues(content)
    assert len(content) == expected_number_of_requests

    for issue in content:
        assert issue['distance'] < 1000


@pytest.mark.django_db
def test_post_issue_no_jurisdiction(api_client, random_service):
    assert not Jurisdiction.objects.exists()
    for attempt in [1, 2]:
        issue = get_data_from_response(
            api_client.post(ISSUE_LIST_ENDPOINT, {
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
            }),
            201
        )
        assert_all_valid_issues([issue])
        assert Jurisdiction.objects.filter(identifier="default").exists()  # default Jurisdiction was created
        assert Jurisdiction.objects.count() == 1


@pytest.mark.django_db
def test_post_issue_multi_jurisdiction(api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    Jurisdiction.objects.create(identifier="j1", name="j1")
    Jurisdiction.objects.create(identifier="j2", name="j2")
    # Can't post without a Jurisdiction when there are multiple
    get_data_from_response(
        api_client.post(ISSUE_LIST_ENDPOINT, {
            "service_code": random_service.service_code,
            "lat": 30,
            "long": 30,
        }),
        400
    )
    for j in Jurisdiction.objects.all():
        # Can't post without a Jurisdiction when there are multiple
        issue = get_data_from_response(
            api_client.post(ISSUE_LIST_ENDPOINT, {
                "jurisdiction_id": j.identifier,
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
            }),
            201
        )
        assert_all_valid_issues([issue])
        assert Issue.objects.get(service_request_id=issue["service_request_id"]).jurisdiction == j


@pytest.mark.django_db
def test_get_issue_multi_jurisdiction_filters_correctly(api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    jurisdictions = [
        Jurisdiction.objects.create(identifier="j%s" % x, name="j%s" % x)
        for x in range(4)
    ]
    for j in jurisdictions:
        for x in range(5):
            Issue.objects.create(
                jurisdiction=j,
                service=random_service
            )
    for j in jurisdictions:
        issues = get_data_from_response(
            api_client.get(ISSUE_LIST_ENDPOINT, {'jurisdiction_id': j.identifier}),
        )
        assert_all_valid_issues(issues)
        assert len(issues) == Issue.objects.filter(jurisdiction=j).count()  # Only getting the Issues for the requested Jurisdiction
