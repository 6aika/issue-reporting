# -- encoding: UTF-8 --
import json
import re

from django.conf import settings
from django.core.urlresolvers import reverse

import pytest

if 'issue_geometry' not in settings.INSTALLED_APPS:
    pytest.skip('app disabled')

from issues.tests.conftest import mf_api_client, random_service  # noqa
from issues.tests.schemata import LIST_OF_ISSUES_SCHEMA
from issues.tests.utils import ISSUE_LIST_ENDPOINT, get_data_from_response, verify_issue
from issues_geometry.models import IssueGeometry
from issues_geometry.validation import GeoJSONValidator


AURAJOKIRANTA_GEOJSON = {
    "type": "Feature",
    "properties": {},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [
                    22.264137268066406,
                    60.440030997851935
                ],
                [
                    22.25804328918457,
                    60.43943818738373
                ],
                [
                    22.254438400268555,
                    60.44155531797
                ],
                [
                    22.251176834106445,
                    60.443799325795936
                ],
                [
                    22.25701332092285,
                    60.44617018455179
                ],
                [
                    22.265253067016598,
                    60.44824454404312
                ],
                [
                    22.268171310424805,
                    60.449599156297516
                ],
                [
                    22.27005958557129,
                    60.44875253025832
                ],
                [
                    22.273406982421875,
                    60.448837193855205
                ],
                [
                    22.27804183959961,
                    60.44998013081624
                ],
                [
                    22.281217575073242,
                    60.44735554905158
                ],
                [
                    22.27890014648437,
                    60.445492813989986
                ],
                [
                    22.268428802490234,
                    60.442656171363225
                ],
                [
                    22.264137268066406,
                    60.440030997851935
                ]
            ]
        ]
    }
}


@pytest.mark.parametrize('geometry_data', [None, AURAJOKIRANTA_GEOJSON, AURAJOKIRANTA_GEOJSON['geometry']])
def test_post_geometry(random_service, mf_api_client, geometry_data):
    post_data = {
        'extensions': 'geometry',
        'service_code': random_service.service_code,
        'description': 'Olut on loppu koko jokirannasta',
        'geometry': (
            json.dumps(geometry_data)
            if geometry_data
            else ''
        ),
    }
    if not post_data.get('geometry'):
        post_data['address'] = 'foo street'
    response = mf_api_client.post(ISSUE_LIST_ENDPOINT, data=post_data)

    content = get_data_from_response(
        response,
        status_code=201,
        schema=LIST_OF_ISSUES_SCHEMA,
    )
    issue_data = content[0]
    issue = verify_issue(issue_data)
    if not geometry_data:
        # This exercises the code path where one requests the geometry extension
        # but doesn't actually post geometry after all.
        return
    # No matter the format, we should always have a GeoJSON fragment, whether encoded or indented, in there:
    assert re.search(r'\\*"type\\*":\s*\\*"Polygon\\*"', response.content.decode('utf8'))
    assert IssueGeometry.objects.filter(issue=issue).exists()
    retrieved_issue_data = get_data_from_response(
        mf_api_client.get(
            reverse('georeport/v2:issue-detail', kwargs={'identifier': issue.identifier}),
            {'extensions': 'geometry'},
        )
    )

    for data in (issue_data, retrieved_issue_data):
        verify_issue(data)
        if mf_api_client.format == 'json':
            # We can't access the extended attribute correctly when it has been mangled by the
            # test harness, so only test it when doing native JSON.
            GeoJSONValidator.validate(data['extended_attributes']['geometry'])


def test_post_invalid_json(random_service, mf_api_client):
    response = get_data_from_response(
        mf_api_client.post(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'geometry',
                'service_code': random_service.service_code,
                'description': 'Miten tätä ajetaan?',
                'geometry': json.dumps(['oops']),
            }
        ),
        status_code=400
    )
    assert 'JSON' in str(response)  # Yeah, it complains about JSON, that's fine


def test_post_invalid_geojson(random_service, mf_api_client):
    response = get_data_from_response(
        mf_api_client.post(
            ISSUE_LIST_ENDPOINT,
            {
                'extensions': 'geometry',
                'service_code': random_service.service_code,
                'description': 'Miten tätä ajetaan?',
                'geometry': json.dumps({'tepe': 'palygon'}),
            },
        ),
        status_code=400
    )
    assert 'Invalid GeoJSON' in str(response)  # Complains about GeoJSON, that's nice
