import pytest
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

from issues.models import Issue, Jurisdiction
from issues.tests.schemata import ISSUE_SCHEMA, LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response, verify_issue


@pytest.mark.django_db
def test_post_issue_no_jurisdiction(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()
    for attempt in [1, 2]:
        issues = get_data_from_response(
            mf_api_client.post(ISSUE_LIST_ENDPOINT, {
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
                "description": get_random_string(),
            }),
            201,
            schema=LIST_OF_ISSUES_SCHEMA
        )
        issue = issues[0]
        assert Issue.objects.filter(identifier=issue['service_request_id']).exists()
        assert Jurisdiction.objects.filter(identifier="default").exists()  # default Jurisdiction was created
        assert Jurisdiction.objects.count() == 1

        issues = get_data_from_response(
            mf_api_client.get(
                reverse('georeport/v2:issue-detail', kwargs={'identifier': issue['service_request_id']}),
            ), schema=LIST_OF_ISSUES_SCHEMA
        )
        verify_issue(issues[0])


@pytest.mark.django_db
def test_post_issue_multi_jurisdiction(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    Jurisdiction.objects.create(identifier="j1", name="j1")
    Jurisdiction.objects.create(identifier="j2", name="j2")
    # Can't post without a Jurisdiction when there are multiple
    get_data_from_response(
        mf_api_client.post(ISSUE_LIST_ENDPOINT, {
            "service_code": random_service.service_code,
            "lat": 30,
            "long": 30,
            "description": get_random_string(),
        }),
        400
    )
    for j in Jurisdiction.objects.all():
        # Can't post without a Jurisdiction when there are multiple
        issues = get_data_from_response(
            mf_api_client.post(ISSUE_LIST_ENDPOINT, {
                "jurisdiction_id": j.identifier,
                "service_code": random_service.service_code,
                "lat": 30,
                "long": 30,
                "description": get_random_string(),
            }),
            201,
            schema=LIST_OF_ISSUES_SCHEMA
        )

        assert Issue.objects.get(identifier=issues[0]["service_request_id"]).jurisdiction == j


@pytest.mark.django_db
def test_get_issue_multi_jurisdiction_filters_correctly(mf_api_client, random_service):
    assert not Jurisdiction.objects.exists()  # Precondition check
    jurisdictions = [
        Jurisdiction.objects.create(identifier="j%s" % x, name="j%s" % x)
        for x in range(4)
    ]
    for j in jurisdictions:
        for x in range(5):
            Issue.objects.create(
                jurisdiction=j,
                service=random_service,
                description=get_random_string(),
                address='Test Street 10',
            )
    for j in jurisdictions:
        issues = get_data_from_response(
            mf_api_client.get(ISSUE_LIST_ENDPOINT, {'jurisdiction_id': j.identifier}),
            schema=LIST_OF_ISSUES_SCHEMA
        )
        # Only getting the Issues for the requested Jurisdiction:
        assert len(issues) == Issue.objects.filter(jurisdiction=j).count()
