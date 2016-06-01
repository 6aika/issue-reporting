import random

import pytest
from django.utils.crypto import get_random_string

from issues.signals import issue_posted
from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.utils import close_enough
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


ROUNDTRIP_TEST_CASES = [  # TODO: Add more test cases!
    {
        "lat": random.uniform(-50, 50),
        "long": random.uniform(-50, 50),
        "description": get_random_string(),
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize('input_data', ROUNDTRIP_TEST_CASES)
def test_post_issue_roundtrip(mf_api_client, random_service, input_data):
    sig_issue = [None]

    def signal_handler(sender, issue, request, **kwargs):
        sig_issue[0] = issue

    issue_posted.connect(signal_handler)

    input_data = dict(input_data, service_code=random_service.service_code)
    issue = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, input_data),
        201,
        schema=ISSUE_SCHEMA
    )
    verify_issue(issue)

    # Test that the issue matches what we posted
    for key, input_value in input_data.items():
        output_value = issue[key]
        if isinstance(input_value, float):
            assert close_enough(input_value, float(output_value))
        else:
            assert input_value == output_value

    # Test that the issue_posted signal was fired and the last issue posted
    # is what we expect
    assert sig_issue[0].identifier == issue['service_request_id']
