import random

import pytest
from django.utils.crypto import get_random_string

from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.utils import get_data_from_response, ISSUE_LIST_ENDPOINT, verify_issue, close_enough

TEST_CASES = [
    {
        "lat": random.uniform(-50, 50),
        "long": random.uniform(-50, 50),
        "description": get_random_string(),
    },
]

# TODO: Add more test cases!


@pytest.mark.django_db
@pytest.mark.parametrize('input_data', TEST_CASES)
def test_post_issue_roundtrip(mf_api_client, random_service, input_data):
    input_data = dict(input_data, service_code=random_service.service_code)
    issue = get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, input_data),
        201,
        schema=ISSUE_SCHEMA
    )
    verify_issue(issue)
    for key, input_value in input_data.items():
        output_value = issue[key]
        if isinstance(input_value, float):
            assert close_enough(input_value, float(output_value))
        else:
            assert input_value == output_value
