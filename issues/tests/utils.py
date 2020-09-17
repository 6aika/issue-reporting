import json

import jsonschema
from django.urls import reverse_lazy

from issues.api.transforms import transform_xml_to_json

ISSUE_LIST_ENDPOINT = reverse_lazy('georeport/v2:issue-list')


def get_data_from_response(response, status_code=200, schema=None):
    if status_code:  # pragma: no branch
        assert response.status_code == status_code, (
            f"Status code mismatch ({response.status_code} is not the expected {status_code})"
        )

    if response["Content-Type"].startswith("application/xml"):
        response.xml = response.content
        response.content = transform_xml_to_json(response.content)
        response["Content-Type"] = "application/json"

    data = json.loads(response.content.decode('utf-8'))
    if schema and response.status_code < 400:
        jsonschema.validate(data, schema)
    return data


ISSUE_VERIFICATION_FIELDS = [
    ('service_request_id', 'identifier'),
] + [(n, n) for n in [
    "description",
    "status",
    "status_notes",
    "agency_responsible",
    "service_notice",
    "address",
]]


def verify_issue(data, issue=None):
    """
    Verify the given data describes the issue passed in.

    If not issue is passed in, it's retrieved from the local database for convenience

    Does not do schema validation, though.

    :type issue: issues.models.Issue|None
    :type data: dict
    """
    if issue is None:
        from issues.models import Issue
        issue = Issue.objects.get(identifier=data['service_request_id'])

    for data_field, issue_field in ISSUE_VERIFICATION_FIELDS:
        if issue_field is None:
            issue_field = data_field
        if callable(issue_field):
            issue_value = issue_field(issue)
        else:
            issue_value = getattr(issue, issue_field, None)
        if data_field in data or issue_value:
            assert data[data_field] == issue_value

    if issue.location:
        lon, lat = issue.location
        assert close_enough(float(data["long"]), lon)
        assert close_enough(float(data["lat"]), lat)

    return issue  # for use in `assert verify_issue()`


def close_enough(a, b, epsilon=0.001):
    distance = abs(a - b)
    assert distance < epsilon, f"{a} and {b} have distance {distance} (should be < {epsilon})"
    return True  # for use in `assert close_enough()`
