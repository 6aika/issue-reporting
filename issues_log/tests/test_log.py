from datetime import timedelta

import pytest
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from issues.models import Issue
from issues.tests.conftest import mf_api_client, random_service  # noqa
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response
from issues_log.models import Issue_LogExtension


def test_get_with_log(random_service, mf_api_client):
    if mf_api_client.format != "json":
        pytest.xfail("logs are misrendered using the spark convention")  # TODO: Fix that

    # Simulate an issue going through a loggy flow:

    creation = now() - timedelta(days=7)
    issue = Issue.objects.create(
        service=random_service,
        description=get_random_string(12),
        requested_datetime=creation,
        address='Test Street 10',
    )
    issue.log_entries.create(
        time=creation + timedelta(days=2),
        status='allocated',
        handler='janne@hel.fi',
    )
    assert Issue_LogExtension.objects.get(issue=issue).last_handler == 'janne@hel.fi'
    issue.log_entries.create(
        time=creation + timedelta(days=5),
        status='handling',
        handler='jeppe@hel.fi',
        note="i'll deal with this",
    )
    assert Issue_LogExtension.objects.get(issue=issue).last_handler == 'jeppe@hel.fi'
    issue.log_entries.create(
        time=creation + timedelta(days=6),
        status='done',
        handler='',
    )
    issue.updated_datetime = now()
    issue.status = 'closed'
    issue.save()

    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'log',
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert len(content[0]['extended_attributes']['log']) == 3
    assert content[0]['extended_attributes']['handler'] == 'jeppe@hel.fi'  # last non-null handler


def test_handler_query(random_service, mf_api_client):
    handlerless_issue = Issue.objects.create(
        service=random_service,
        description=get_random_string(12),
        address='Test Street 10',
    )
    for x in range(3):
        handlerful_issue = Issue.objects.create(
            service=random_service,
            description=get_random_string(12),
            address='Test Street 10',
        )
        handlerful_issue.log_entries.create(
            status='allocated',
            handler='janne@hel.fi',
        )

    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'log',
                'handler': 'janne@hel.fi',
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    assert len(content) == 3
    assert all(i['extended_attributes']['handler'] == 'janne@hel.fi' for i in content)
