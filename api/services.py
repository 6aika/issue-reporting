from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D

from api.models import Feedback


def get_feedbacks(service_codes, service_request_ids,
                  start_date, end_date,
                  statuses, description,
                  service_object_type, service_object_id,
                  updated_after, updated_before,
                  lat, lon, radius,
                  order_by):
    queryset = Feedback.objects.all()
    if service_request_ids:
        queryset = queryset.filter(service_request_id__in=service_request_ids.split(','))
    if service_codes:
        queryset = queryset.filter(service_code__in=service_codes.split(','))
    if start_date:
        queryset = queryset.filter(requested_datetime__gt=start_date)
    if end_date:
        queryset = queryset.filter(requested_datetime__lt=end_date)
    if statuses:
        queryset = queryset.filter(status__in=statuses.split(','))

    # start CitySDK Helsinki specific filtration
    if description:
        queryset = queryset.filter(description__icontains=description)
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
        queryset = Feedback.objects.annotate(distance=Distance('location', point))

        if radius:
            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))

    # end CitySDK Helsinki specific filtration

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset
