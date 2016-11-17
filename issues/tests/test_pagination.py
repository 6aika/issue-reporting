from __future__ import division
import pytest
from math import ceil

from issues.api.pagination import GeoReportV2Pagination
from issues.models import Issue
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response


@pytest.mark.django_db
@pytest.mark.parametrize('param', GeoReportV2Pagination.page_size_query_params)
@pytest.mark.parametrize('count', (7, 10, 12))
def test_pagination(mf_api_client, random_service, param, count):
    for i in range(30):
        Issue.objects.create(service=random_service, description=i)
    resp = mf_api_client.get(ISSUE_LIST_ENDPOINT, {param: count})
    assert resp['x-result-count'] == str(30)
    assert resp['x-page-count'] == str(int(ceil(30 / count)))
    content = get_data_from_response(resp, schema=LIST_OF_ISSUES_SCHEMA)
    assert len(content) == count
