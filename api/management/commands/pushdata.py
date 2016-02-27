import json

import requests
from django.conf import settings
from django.core.management import BaseCommand

from api.models import Feedback


def send_feedback_to_open311(f):
    open_311_url = settings.OPEN311_URL

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
            media_url=f.media_url
    )

    r = requests.post(open_311_url, data=data, allow_redirects=True)
    content = json.loads(r.content.decode('utf-8'))

    if r.status_code == 200:
        f.service_request_id = content[0]['service_request_id']
        f.service_notice = content[0]['service_notice']
        f.save()
    else:
        print(content)


class Command(BaseCommand):
    help = 'Push new feedbacks to Open311 and save their service_request_id.'

    def handle(self, *args, **options):
        feedbacks = Feedback.objects.filter(service_request_id='')
        print("Number of feedback to send: {}".format(len(feedbacks)))

        for feedback in feedbacks:
            send_feedback_to_open311(feedback)

        print('Feedbacks are sent to remote system')
