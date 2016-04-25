import json
import logging
import time
import urllib.request
from datetime import datetime, timedelta
from urllib.error import URLError

from dateutil import parser as datetime_parser
from dateutil.parser import parse
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Max

from issues.analysis import calc_fixing_time
from issues.models import Issue, MediaURL, Task
from issues.services import issue_status_was_changed, send_email_notification

logger = logging.getLogger(__name__)


def get_existing_issue(service_request_id):
    try:
        return Issue.objects.get(service_request_id=service_request_id)
    except Issue.DoesNotExist:
        return None


@transaction.atomic
def save_issue(f):
    existing_issue = get_existing_issue(f['service_request_id'])

    expected_datetime = f.get('expected_datetime', None)
    requested_datetime = f.get('requested_datetime', None)
    if expected_datetime is None and requested_datetime is not None:
        requested_datetime = parse(requested_datetime)
        median = timedelta(milliseconds=calc_fixing_time(f.get('service_code', '')))
        if median.total_seconds() > 0:
            expected_datetime = requested_datetime + median

    updated_issue = Issue(
        service_request_id=f['service_request_id'],
        status_notes=f.get('status_notes', ''),
        status=f['status'],
        service_code=f.get('service_code', ''),
        service_name=f.get('service_name', ''),
        description=f.get('description', ''),
        agency_responsible=f.get('agency_responsible', ''),
        service_notice=f.get('service_notice', ''),
        requested_datetime=f.get('requested_datetime', ''),
        updated_datetime=f.get('updated_datetime', ''),
        expected_datetime=expected_datetime,
        address_string=f.get('address', ''),
        media_url=f.get('media_url', ''),

        email=f.get('email', ''),
        first_name=f.get('first_name', ''),
        last_name=f.get('last_name', ''),
        phone=f.get('phone', ''),

        # Extension information
        service_object_id=f.get('service_object_id', ''),
        service_object_type=f.get('service_object_type', ''),

        location=GEOSGeometry('SRID=4326;POINT(' + str(f.get('long', 0)) + ' ' + str(f.get('lat', 0)) + ')'),

        synchronized=True
    )

    if existing_issue:
        updated_issue.id = existing_issue.id
        Task.objects.filter(issue_id=existing_issue.id).delete()
        MediaURL.objects.filter(issue_id=existing_issue.id).delete()

    extended_attributes = f.get('extended_attributes', None)
    if extended_attributes:
        updated_issue.title = extended_attributes.get('title', '')
        updated_issue.detailed_status = extended_attributes.get('detailed_status', '')

    updated_issue.save()

    if extended_attributes:
        media_urls_json = extended_attributes.get('media_urls', None)
        if media_urls_json:
            for media_url_json in media_urls_json:
                media_url = MediaURL(issue_id=updated_issue.id, media_url=media_url_json)
                media_url.save()

        tasks_json = extended_attributes.get('tasks', None)
        if tasks_json:
            for task_json in tasks_json:
                task = Task(
                    issue_id=updated_issue.id,
                    task_state=task_json.get('task_state', ''),
                    task_type=task_json.get('task_type', ''),
                    owner_name=task_json.get('owner_name', ''),
                    task_modified=task_json.get('task_modified', ''),
                    task_created=task_json.get('task_created', '')
                )
                task.save()

    if settings.SEND_STATUS_UPDATE_NOTIFICATIONS \
            and existing_issue and issue_status_was_changed(existing_issue, updated_issue):
        send_email_notification(updated_issue)


def sync_open311_data(start_datetime):
    end_datetime = start_datetime + timedelta(settings.OPEN311_RANGE_LIMIT_DAYS)
    time_interval_days = settings.OPEN311_RANGE_LIMIT_DAYS

    while start_datetime < datetime.now():
        open_311_url = settings.OPEN311_URL + "/requests.json?extensions=true&updated_after=" \
            + start_datetime.isoformat() + "Z&updated_before=" + end_datetime.isoformat()
        logger.info('url to send: {}'.format(open_311_url))

        try:
            response = urllib.request.urlopen(open_311_url)
            content = response.read()
            json_data = json.loads(content.decode("utf8"))
        except ValueError:
            logger.exception('Decoding JSON has failed')
            return
        except URLError:
            logger.exception('Invalid URL: {}'.format(open_311_url))
            return

        issue_count = len(json_data)

        logger.info("Number of issues to synchronize: {}".format(len(json_data)))

        if issue_count >= settings.OPEN311_ISSUES_PER_RESPONSE_LIMIT:
            logger.info("Number of issues is more than API limit! Should send additional requests.")
            time_interval_days /= 2
            end_datetime = start_datetime + timedelta(days=int(time_interval_days))
            continue
        else:
            time_interval_days = settings.OPEN311_RANGE_LIMIT_DAYS

        for issue_json in json_data:
            save_issue(issue_json)

        start_datetime = end_datetime
        end_datetime = start_datetime + timedelta(days=settings.OPEN311_RANGE_LIMIT_DAYS)


def sync_with_id_file(path_to_ids):
    with open(path_to_ids) as f:
        for service_request_id in f:
            open_311_url = settings.OPEN311_URL + "/requests/{}.json?extensions=true".format(
                service_request_id.rstrip())
            logger.info('url to send: {}'.format(open_311_url))

            try:
                response = urllib.request.urlopen(open_311_url)
                content = response.read()
                json_data = json.loads(content.decode("utf8"))
            except ValueError:
                logger.exception('Decoding JSON has failed')
                return
            except URLError:
                logger.exception('Invalid URL: {}'.format(open_311_url))
                return

            for issue_json in json_data:
                save_issue(issue_json)

            time.sleep(1)


def sync_all_data():
    start_datetime = datetime_parser.parse(settings.SYNCHRONIZATION_START_DATETIME)
    sync_open311_data(start_datetime)


def sync_new_data():
    start_datetime = Issue.objects.all().aggregate(Max('updated_datetime'))['updated_datetime__max'] \
        .replace(tzinfo=None)
    sync_open311_data(start_datetime)


class Command(BaseCommand):
    help = 'Read and save data from Open311 Server provided in settings.py. ' \
           'To write issues to Open311 see \'pushdata\' command.'

    def add_arguments(self, parser):
        parser.add_argument('--path_to_ids', nargs='+', type=str)

    def handle(self, *args, **options):
        path_to_ids = options.get('path_to_ids')
        if path_to_ids is not None:
            sync_with_id_file(path_to_ids[0])
            return

        request_count = Issue.objects.filter(synchronized=True).count()
        if request_count == 0:
            sync_all_data()
        else:
            sync_new_data()

        logger.info("Synchronization complete")
