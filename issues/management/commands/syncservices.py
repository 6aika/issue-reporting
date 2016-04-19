import json
import logging
import urllib
from urllib.error import URLError

from django.conf import settings
from django.core.management import BaseCommand

from issues.models import Service

logger = logging.getLogger(__name__)


def get_existing_service(service_code):
    try:
        return Service.objects.get(service_code=service_code)
    except Service.DoesNotExist:
        return None


def save_service(s):
    existing_service = get_existing_service(s['service_code'])
    service_data = Service(
        service_code=s.get('service_code'),
        service_name=s.get('service_name'),
        description=s.get('description'),
        metadata=s.get('metadata'),
        type=s.get('type'),
        keywords=s.get('keywords'),
        group=s.get('group')
    )

    if existing_service:
        service_data.id = existing_service.id

    service_data.save()


class Command(BaseCommand):
    help = 'Read and save service data from Open311 Server provided in settings.py.'

    def handle(self, *args, **options):
        open_311_url = settings.OPEN311_SERVICE_URL.format('fi')
        logger.info('url to send: {}'.format(open_311_url))

        try:
            response = urllib.request.urlopen(open_311_url)
            content = response.read()
            json_data = json.loads(content.decode("utf8"))
        except ValueError:
            logger.info('Decoding JSON has failed')
            return
        except URLError:
            logger.info('Invalid URL: {}'.format(open_311_url))
            return

        service_count = len(json_data)
        logger.info('Service count: {}'.format(service_count))

        for service in json_data:
            save_service(service)

        logger.info("Service synchronization complete")
