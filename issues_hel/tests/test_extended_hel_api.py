from datetime import timedelta

import pytest
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from issues.models import Issue
from issues.tests.conftest import mf_api_client, random_service  # noqa
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.test_feedbacks_api import ISSUE_LIST_ENDPOINT
from issues.tests.utils import get_data_from_response


def test_get_with_tasks(random_service, mf_api_client):
    if mf_api_client.format != "json":
        pytest.xfail("tasks are misrendered using the spark convention")  # TODO: Fix that
    issue = Issue.objects.create(
        service=random_service,
        description=get_random_string(),
    )
    for x, time in enumerate((
            now() - timedelta(days=5),
            now() - timedelta(days=2),
    ), 1):
        id = 'foo%04d' % x
        issue.tasks.create(
            task_state=id,
            task_type=id,
            owner_name=id,
            task_created=time,
        )
    content = get_data_from_response(
        mf_api_client.get(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'hel',
            }
        ),
        schema=LIST_OF_ISSUES_SCHEMA
    )
    tasks = content[0]['extended_attributes']['tasks']
    assert tasks
