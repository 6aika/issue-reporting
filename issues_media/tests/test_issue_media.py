from base64 import b64decode

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

from issues.models.issues import Issue
from issues.tests.conftest import mf_api_client, random_service  # noqa
from issues.tests.schemata import ISSUE_SCHEMA
from issues.tests.test_feedbacks_api import ISSUE_LIST_ENDPOINT
from issues.tests.utils import get_data_from_response
# https://raw.githubusercontent.com/mathiasbynens/small/master/jpeg.jpg
from issues_media.models import IssueMedia

VERY_SMALL_JPEG = b64decode(
    '/9j/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgK'
    'CgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/'
    'yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k='
)


def test_post_media(mf_api_client, random_service):
    files = [
        ContentFile(content=VERY_SMALL_JPEG, name="x%d.jpg" % x)
        for x in range(3)
    ]
    issue = get_data_from_response(
        mf_api_client.post(
            '%s?extensions=media' % ISSUE_LIST_ENDPOINT,
            data={
                'service_code': random_service.service_code,
                'lat': 30,
                'long': 30,
                'description': get_random_string(),
                'media': files,
            }
        ),
        status_code=201
    )
    id = issue['service_request_id']
    assert Issue.objects.filter(identifier=id).exists()
    assert IssueMedia.objects.filter(issue__identifier=id).count() == 3

    # Now see that we can actually get the media back
    issue = get_data_from_response(
        mf_api_client.get(
            reverse('georeport/v2:issue-detail', kwargs={"identifier": id}),
            {
                'extensions': 'media',
            }
        ),
        schema=ISSUE_SCHEMA
    )
    media_list = issue['extended_attributes']['media_urls']
    assert issue