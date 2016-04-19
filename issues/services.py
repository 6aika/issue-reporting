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

from issues.models import Feedback, MediaFile, MediaURL

logger = logging.getLogger(__name__)


def get_feedbacks(service_codes=None, service_request_ids=None,
                  start_date=None, end_date=None,
                  statuses=None, search=None,
                  service_object_type=None, service_object_id=None,
                  updated_after=None, updated_before=None,
                  lat=None, lon=None, radius=None,
                  order_by=None, agency_responsible=None, use_limit=False):
    queryset = Feedback.objects.all()

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

    if settings.SHOW_ONLY_MODERATED:
        queryset = queryset.exclude(status__iexact='MODERATION')

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

    if use_limit is True \
            and start_date is None and end_date is None and updated_before is None and updated_after is None:
        queryset = queryset[:settings.FEEDBACK_LIST_LIMIT]

    return queryset


def get_feedbacks_count():
    queryset = Feedback.objects
    if settings.SHOW_ONLY_MODERATED:
        queryset = queryset.exclude(status__iexact='MODERATION')
    return queryset.count()


def attach_files_to_feedback(request, feedback, files):
    for file in files:
        abs_url = ''.join([request.build_absolute_uri('/')[:-1], settings.MEDIA_URL, file.file.name])
        media_url = MediaURL(feedback=feedback, media_url=abs_url)
        media_url.save()
        feedback.media_urls.add(media_url)
        # Attach the file to feedback - not needed if using external Open311!
        feedback.media_files.add(file)

    # Update the single media_url field to point to the 1st image
    feedback.media_url = feedback.media_urls.all()[0].media_url
    feedback.save()


def save_file_to_db(file, form_id):
    # Create new unique random filename preserving extension
    original_filename = file.name
    size = file.size
    extension = os.path.splitext(file.name)[1]
    file.name = uuid.uuid4().hex + extension
    f_object = MediaFile(file=file, form_id=form_id, original_filename=original_filename, size=size)
    f_object.save()
    return file.name


def feedback_status_was_changed(feedback_old, feedback_new):
    return feedback_old.status != feedback_new.status


# send email notification about status change with link to feedback details
def send_email_notification(feedback):
    if feedback.email is None:
        logger.info('no email to send status update notification')
        return
    else:
        feedback_details_url = settings.FEEDBACK_DETAILS_URL.format(feedback.pk)
        email = EmailMessage(settings.EMAIL_SUBJECT, settings.EMAIL_TEXT
                             .replace('{{ feedback URL }}', feedback_details_url), to=[feedback.email])
        email.content_subtype = "html"
        try:
            email.send(fail_silently=False)
            logger.info('email about feedback {} status update was sent to {}'
                        .format(feedback.service_request_id, feedback.email))
        except SMTPException:
            logger.exception('cannot send email about feedback {} status update was sent to {} due to error '
                             .format(feedback.service_request_id, feedback.email))
