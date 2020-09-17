import random

import pytest
from django.utils.crypto import get_random_string

from issues.models.applications import Application
from issues.signals import issue_posted
from issues.tests.schemata import ISSUE_SCHEMA, LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, close_enough, get_data_from_response, verify_issue


@pytest.mark.django_db
@pytest.mark.parametrize('status', ('public', 'unmoderated'))
def test_default_moderation_status(mf_api_client, random_service, settings, status):
    """
    Test that when the default mod status is not 'public',
    freshly created issues are not visible via the list endpoint
    """
    settings.ISSUES_DEFAULT_MODERATION_STATUS = status
    posted_issues = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, {
            "lat": 15,
            "long": 15,
            "description": get_random_string(12),
            "service_code": random_service.service_code,
        }),
        201,
        schema=LIST_OF_ISSUES_SCHEMA
    )
    verify_issue(posted_issues[0])

    listed_issues = get_data_from_response(
        mf_api_client.get(ISSUE_LIST_ENDPOINT),
        200,
    )
    assert bool(listed_issues) == (status == 'public')


ROUNDTRIP_TEST_CASES = [  # TODO: Add more test cases!
    {
        "lat": random.uniform(-50, 50),
        "long": random.uniform(-50, 50),
        "description": get_random_string(12),
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
    issues = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, input_data),
        201,
        schema=LIST_OF_ISSUES_SCHEMA,
    )
    issue = issues[0]
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


@pytest.mark.django_db
@pytest.mark.parametrize('api_key_mode', ('none', 'default-only', 'actual-apps'))
@pytest.mark.parametrize('pass_api_key', (False, True))
def test_post_issue_api_key(mf_api_client, random_service, api_key_mode, pass_api_key):
    expected_app = Application.autodetermine()
    expected_status = 201
    if api_key_mode == 'actual-apps':
        for x in range(5):
            expected_app = Application.objects.create(identifier='app%d' % (x + 1))
        if not pass_api_key:
            expected_status = 400

    input_data = dict(
        description=get_random_string(12),
        service_code=random_service.service_code,
        address='hello',
        api_key=(expected_app.key if pass_api_key else ''),
    )
    issues = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, input_data),
        status_code=expected_status,
        schema=LIST_OF_ISSUES_SCHEMA,
    )
    if expected_status >= 400:
        return  # Nothing more to do here
    issue = verify_issue(issues[0])
    assert issue.application == expected_app
