import pytest
from rest_framework import status

from issues.models import Issue
from issues.tests.api_utils import APIClientWrapper
from issues.tests.db_utils import execute_fixture


@pytest.fixture()
def testing_issues(db):
    execute_fixture('insert_requests')


@pytest.fixture()
def api_client():
    return APIClientWrapper()


def test_get_requests(testing_issues, api_client):
    response, content = api_client.get('api/v1:issue-list')
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == Issue.objects.count()


def test_get_by_service_request_id(testing_issues, api_client):
    response, content = api_client.get('api/v1:issue-list', {'service_request_id': '1982hglaqe8pdnpophff'})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == 1
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'


def test_get_by_service_request_ids(testing_issues, api_client):
    response, content = api_client.get('api/v1:issue-list',
                                       {'service_request_id': '1982hglaqe8pdnpophff,2981hglaqe8pdnpoiuyt'})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == 2
    assert content[0]['service_request_id'] == '1982hglaqe8pdnpophff'
    assert content[1]['service_request_id'] == '2981hglaqe8pdnpoiuyt'


def test_get_by_unexisting_request_id(testing_issues, api_client):
    response, content = api_client.get('api/v1:issue-list', {'service_request_id': 'unexisting_req_id'})
    assert response.status_code == status.HTTP_200_OK
    assert content == []


def test_get_by_service_code(testing_issues, api_client):
    service_code = '171'
    response, content = api_client.get('api/v1:issue-list', {'service_code': service_code})
    assert response.status_code == status.HTTP_200_OK
    for issue in content:
        assert issue['service_code'] == service_code


def test_get_by_start_date(testing_issues, api_client):
    start_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 3
    response, content = api_client.get('api/v1:issue-list', {'start_date': start_date})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['requested_datetime'] > start_date


def test_get_by_end_data(testing_issues, api_client):
    end_date = '2015-06-23T15:51:11Z'
    expected_number_of_requests = 1
    response, content = api_client.get('api/v1:issue-list', {'end_date': end_date})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests
    for request in content:
        assert request['requested_datetime'] < end_date


def test_get_by_status(testing_issues, api_client):
    issue_status = 'open'
    expected_number_of_requests = 2
    response, content = api_client.get('api/v1:issue-list', {'status': issue_status})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['status'] == issue_status


def test_by_description(testing_issues, api_client):
    search = 'some'
    response, content = api_client.get('api/v1:issue-list', {'search': search})
    assert response.status_code == 200
    assert search.lower() in content[0]['description'].lower()


def test_get_with_extensions(testing_issues, api_client):
    response, content = api_client.get(
        'api/v1:issue-list',
        {'service_request_id': '1982hglaqe8pdnpophff', 'extensions': 'true'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'extended_attributes' in content[0]


def test_get_without_extensions(testing_issues, api_client):
    response, content = api_client.get('api/v1:issue-list', {'service_request_id': '1982hglaqe8pdnpophff'})
    assert response.status_code == status.HTTP_200_OK
    assert 'extended_attributes' not in content[0]


def test_get_by_updated_after(testing_issues, api_client):
    updated_after = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 3
    response, content = api_client.get('api/v1:issue-list', {'updated_after': updated_after})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] > updated_after


def test_get_by_updated_before(testing_issues, api_client):
    updated_before = '2015-07-24T12:01:44Z'
    expected_number_of_requests = 1
    response, content = api_client.get('api/v1:issue-list', {'updated_before': updated_before})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests
    for issue in content:
        assert issue['updated_datetime'] < updated_before


def test_get_by_service_object(testing_issues, api_client):
    service_object_id = '10844'
    service_object_type = 'http://www.hel.fi/servicemap/v2'
    response, content = api_client.get(
        'api/v1:issue-list',
        {
            'extensions': 'true',
            'service_object_id': 'service_object_id',
            'service_object_type': 'service_object_type'
        }
    )
    assert response.status_code == status.HTTP_200_OK
    for issue in content:
        assert issue['extended_attributes']['service_object_id'] == service_object_id
        assert issue['extended_attributes']['service_object_type'] == service_object_type


def test_get_by_service_object_id_without_type(testing_issues, api_client):
    service_object_id = '10844'
    response, content = api_client.get('api/v1:issue-list', {'service_object_id': service_object_id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_within_radius(testing_issues, api_client):
    lat = 60.187394
    long = 24.940773
    radius = 1000
    expected_number_of_requests = 3
    response, content = api_client.get('api/v1:issue-list', {'lat': lat, 'long': long, 'radius': radius})
    assert response.status_code == status.HTTP_200_OK
    assert len(content) == expected_number_of_requests

    for issue in content:
        assert issue['distance'] < 1000
