import pytest
from django.utils.crypto import get_random_string

from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.utils import get_data_from_response, ISSUE_LIST_ENDPOINT, verify_issue


@pytest.mark.django_db
@pytest.mark.parametrize('status', ('public', 'unmoderated'))
def test_default_moderation_status(mf_api_client, random_service, settings, status):
    """
    Test that when the default mod status is not 'public',
    freshly created issues are not visible via the list endpoint
    """
    settings.ISSUES_DEFAULT_MODERATION_STATUS = status
    issue = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, {
            "lat": 15,
            "long": 15,
            "description": get_random_string(),
            "service_code": random_service.service_code,
        }),
        201,
        schema=ISSUE_SCHEMA
    )
    verify_issue(issue)

    issues = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT),
        200,
    )
    assert bool(issues) == (status == 'public')
