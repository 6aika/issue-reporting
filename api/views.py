from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Feedback
from .serializers import FeedbackSerializer


def get_feedbacks(service_codes, service_request_ids):
    queryset = Feedback.objects.all()
    if service_request_ids:
        queryset = queryset.filter(service_request_id__in=service_request_ids.split(','))
    if service_codes:
        queryset = queryset.filter(service_code__in=service_codes.split(','))

    point = fromstr('SRID=4326;POINT(%s %s)' % (24.821711, 60.186896))
    queryset = Feedback.objects.annotate(distance=Distance('location', point)) \
        .filter(location__distance_lte=(point, D(m=3000))).order_by('distance')

    return queryset


class FeedbackViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def list(self, request):
        queryset = get_feedbacks(
                service_request_ids=request.query_params.get('service_request_id', None),
                service_codes=request.query_params.get('service_code', None),
        )
        serializer = FeedbackSerializer(queryset, many=True)
        return Response(serializer.data)
