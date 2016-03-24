import json
import logging

import requests
from django.conf import settings
from django.core.management import BaseCommand

from api.models import Feedback

logger = logging.getLogger(__name__)


def send_feedback_to_open311(f):
    open_311_url = settings.OPEN311_URL + "/requests.json"

    data = dict(
            api_key=settings.OPEN311_API_KEY,
            service_code=f.service_code,
            description=f.description,
            title=f.title,
            lat=f.lat,
            long=f.lon,
            service_object_type=f.service_object_type,
            service_object_id=f.service_object_id,
            address_string=f.address_string,
            email=f.email,
            first_name=f.first_name,
            last_name=f.last_name,
            phone=f.phone,
            media_url=f.media_url
    )

    r = requests.post(open_311_url, data=data, allow_redirects=True)
    content = json.loads(r.content.decode('utf-8'))

    if r.status_code == 200:
        f.service_request_id = content[0]['service_request_id']
        f.service_notice = content[0]['service_notice']
        f.save()
    else:
        logger.info(content)


class Command(BaseCommand):
    help = 'Push new feedbacks to Open311 and save their service_request_id.'

    def handle(self, *args, **options):
        feedbacks = Feedback.objects.filter(service_request_id='')
        logger.info("Number of feedback to send: {}".format(len(feedbacks)))

        for feedback in feedbacks:
            send_feedback_to_open311(feedback)

        logger.info('Feedbacks are sent to remote system')
