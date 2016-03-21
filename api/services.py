from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D

from api.models import Feedback


def get_feedbacks(service_codes=None, service_request_ids=None,
                  start_date=None, end_date=None,
                  statuses=None, search=None,
                  service_object_type=None, service_object_id=None,
                  updated_after=None, updated_before=None,
                  lat=None, lon=None, radius=None,
                  order_by=None):
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
        queryset = queryset.annotate(distance=Distance('location', point))

        if radius:
            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))

    # end CitySDK Helsinki specific filtration

    if order_by:
        queryset = queryset.order_by(order_by)

    # TODO: replace with conditional expression?
    feedback_list = list(queryset)
    for item in feedback_list:
        if hasattr(item, 'distance') and item.location.x == 0.0 and item.location.y == 0.0:
            del item.distance

    return feedback_list


def get_feedbacks_count():
    queryset = Feedback.objects
    if settings.SHOW_ONLY_MODERATED:
        queryset = queryset.exclude(status__iexact='MODERATION')
    return queryset.count()
