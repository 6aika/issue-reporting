import logging
import os
import uuid
from smtplib import SMTPException

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models.sql import DistanceField
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.core.mail import EmailMessage
from django.db.models import Case, When

from issues.models import Issue, MediaFile, MediaURL

logger = logging.getLogger(__name__)


def get_issues(
    jurisdiction_id=None,
    service_codes=None, service_request_ids=None,
    start_date=None, end_date=None,
    statuses=None, search=None,
    service_object_type=None, service_object_id=None,
    updated_after=None, updated_before=None,
    lat=None, lon=None, radius=None,
    order_by=None, agency_responsible=None, use_limit=False
):
    queryset = Issue.objects.all()

    if jurisdiction_id:
        queryset = queryset.filter(jurisdiction__identifier=jurisdiction_id)

    if service_request_ids:
        queryset = queryset.filter(service_request_id__in=service_request_ids.split(','))
    if service_codes:
        queryset = queryset.filter(service_code__in=str(service_codes).split(','))
    if start_date:
        queryset = queryset.filter(requested_datetime__gt=start_date)
    if end_date:
        queryset = queryset.filter(requested_datetime__lt=end_date)
    if statuses:
        queryset = queryset.filter(status__in=statuses.split(','))
    if agency_responsible:
        queryset = queryset.filter(agency_responsible__iexact=agency_responsible)

    # start CitySDK Helsinki specific filtration
    if search:
        queryset = queryset.filter(description__icontains=search) | queryset.filter(
            title__icontains=search) | queryset.filter(address_string__icontains=search) | queryset.filter(
            agency_responsible__icontains=search)
    if service_object_type:
        queryset = queryset.filter(service_object_type__icontains=service_object_type)
    if service_object_id:
        queryset = queryset.filter(service_object_id=service_object_id)
    if updated_after:
        queryset = queryset.filter(updated_datetime__gt=updated_after)
    if updated_before:
        queryset = queryset.filter(updated_datetime__lt=updated_before)

    if lat and lon:
        point = fromstr('SRID=4326;POINT(%s %s)' % (lon, lat))
        empty_point = fromstr('POINT(0 0)', srid=4326)
        queryset = queryset.annotate(distance=Case(
            When(location__distance_gt=(empty_point, D(m=0.0)), then=Distance('location', point)),
            default=None,
            output_field=DistanceField('m')
        ))

        if radius:
            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))

    # end CitySDK Helsinki specific filtration

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


def get_issues_count():
    queryset = Issue.objects
    return queryset.count()


def attach_files_to_issue(request, issue, files):
    for file in files:
        abs_url = ''.join([request.build_absolute_uri('/')[:-1], settings.MEDIA_URL, file.file.name])
        media_url = MediaURL(issue=issue, media_url=abs_url)
        media_url.save()
        issue.media_urls.add(media_url)
        # Attach the file to issue - not needed if using external Open311!
        issue.media_files.add(file)

    # Update the single media_url field to point to the 1st image
    issue.media_url = issue.media_urls.all()[0].media_url
    issue.save()


def save_file_to_db(file, form_id):
    # Create new unique random filename preserving extension
    original_filename = file.name
    size = file.size
    extension = os.path.splitext(file.name)[1]
    file.name = uuid.uuid4().hex + extension
    f_object = MediaFile(file=file, form_id=form_id, original_filename=original_filename, size=size)
    f_object.save()
    return file.name


def issue_status_was_changed(issue_old, issue_new):
    return issue_old.status != issue_new.status


# send email notification about status change with link to issue details
def send_email_notification(issue):
    if issue.email is None:
        logger.info('no email to send status update notification')
        return
    else:
        issue_details_url = settings.ISSUE_DETAILS_URL.format(issue.pk)
        email = EmailMessage(settings.EMAIL_SUBJECT, settings.EMAIL_TEXT
                             .replace('{{ issue URL }}', issue_details_url), to=[issue.email])
        email.content_subtype = "html"
        try:
            email.send(fail_silently=False)
            logger.info('email about issue {} status update was sent to {}'
                        .format(issue.service_request_id, issue.email))
        except SMTPException:
            logger.exception('cannot send email about issue {} status update was sent to {} due to error '
                             .format(issue.service_request_id, issue.email))
