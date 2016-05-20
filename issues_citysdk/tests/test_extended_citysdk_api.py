from issues.tests.conftest import mf_api_client, testing_issues  # noqa
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import get_data_from_response, ISSUE_LIST_ENDPOINT
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
