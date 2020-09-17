from django.utils.crypto import get_random_string

from issues.tests.conftest import mf_api_client, random_service, testing_issues  # noqa
from issues.tests.schemata import ISSUE_SCHEMA, LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response, verify_issue
from issues_citysdk.models import Issue_CitySDK


def test_get_by_service_object(testing_issues, mf_api_client):
    issue = testing_issues.first()
    service_object_id = '10844'
    service_object_type = 'http://www.hel.fi/servicemap/v2'
    Issue_CitySDK.objects.create(
        issue=issue,
        service_object_id=service_object_id,
        service_object_type=service_object_type,
    )

    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'citysdk',
                'service_object_id': service_object_id,
                'service_object_type': service_object_type,
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )

    for issue in content:
        assert issue['extended_attributes']['service_object_id'] == service_object_id
        assert issue['extended_attributes']['service_object_type'] == service_object_type


def test_get_by_service_object_id_without_type(testing_issues, mf_api_client):
    get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'citysdk',
                'service_object_id': '10844',
            }
        ),
        status_code=400
    )


def test_by_description(testing_issues, mf_api_client):
    search = 'some'

    content = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT, {
            'extensions': 'citysdk',
            'search': search
        }),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert search.lower() in content[0]['description'].lower()


def test_post_service_object(random_service, mf_api_client):
    service_object_id = get_random_string(12)
    service_object_type = 'http://www.hel.fi/servicemap/v2'
    title = get_random_string(12)

    issues = get_data_from_response(
        mf_api_client.post(
            ISSUE_LIST_ENDPOINT + '?extensions=citysdk',
            {
                'service_code': random_service.service_code,
                'lat': 42,
                'long': 42,
                'description': 'hellote',
                'service_object_id': service_object_id,
                'service_object_type': service_object_type,
                'title': title,
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA,
        status_code=201
    )
    issue = issues[0]
    verify_issue(issue)
    iex = Issue_CitySDK.objects.get(issue__identifier=issue['service_request_id'])

    assert iex.service_object_id == issue['extended_attributes']['service_object_id'] == service_object_id
    assert iex.service_object_type == issue['extended_attributes']['service_object_type'] == service_object_type
    assert iex.title == issue['extended_attributes']['title'] == title
