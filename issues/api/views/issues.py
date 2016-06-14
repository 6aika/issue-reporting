from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from issues.api.serializers import IssueSerializer
from issues.extensions import apply_select_and_prefetch, get_extensions_from_request
from issues.gis import determine_gissiness
from issues.models import Issue
from issues.signals import issue_posted
from issues.utils import parse_bbox


class IssueViewBase(GenericAPIView):
    item_tag_name = 'request'
    root_tag_name = 'requests'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['extensions'] = get_extensions_from_request(self.request)
        return ctx


class IssueFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        extensions = get_extensions_from_request(request)

        agency_responsible = request.query_params.get('agency_responsible')
        end_date = request.query_params.get('end_date')
        identifiers = request.query_params.get('service_request_id')
        jurisdiction_id = request.query_params.get('jurisdiction_id')
        service_codes = request.query_params.get('service_code')
        start_date = request.query_params.get('start_date')
        statuses = request.query_params.get('status')
        updated_after = request.query_params.get('updated_after')
        updated_before = request.query_params.get('updated_before')

        if jurisdiction_id:
            queryset = queryset.filter(jurisdiction__identifier=jurisdiction_id)

        if identifiers:
            queryset = queryset.filter(identifier__in=identifiers.split(','))
        if service_codes:
            queryset = queryset.filter(service_code__in=str(service_codes).split(','))
        if start_date:
            queryset = queryset.filter(requested_datetime__gte=start_date)
        if end_date:
            queryset = queryset.filter(requested_datetime__lte=end_date)
        if statuses:
            queryset = queryset.filter(status__in=statuses.split(','))
        if agency_responsible:
            queryset = queryset.filter(agency_responsible__iexact=agency_responsible)

        if updated_after:  # CitySDK extension
            queryset = queryset.filter(updated_datetime__gt=updated_after)
        if updated_before:  # CitySDK extension
            queryset = queryset.filter(updated_datetime__lt=updated_before)

        queryset = self._apply_geo_filters(request, queryset)
        queryset = apply_select_and_prefetch(queryset=queryset, extensions=extensions)

        for ex in extensions:
            queryset = ex.filter_issue_queryset(request, queryset, view)

        order_by = (request.query_params.get('order_by') or '-pk')
        queryset = queryset.order_by(order_by)

        return queryset

    def _apply_geo_filters(self, request, queryset):
        # Strictly speaking these are not queries that should be possible with a GeoReport v2
        # core implementation, but as they do not require extra data in the models, it's worth it
        # to have them available "for free".
        bbox = request.query_params.get('bbox')
        if bbox:
            bbox = parse_bbox(bbox)
            (long1, lat1), (long2, lat2) = bbox
            queryset = queryset.filter(lat__range=(lat1, lat2))
            queryset = queryset.filter(long__range=(long1, long2))

        lat = request.query_params.get('lat')
        lon = request.query_params.get('long')
        radius = request.query_params.get('radius')
        if lat and lon and radius:
            try:
                lat = float(lat)
                lon = float(lon)
                radius = float(radius)
            except ValueError:
                raise APIException('lat/lon/radius must all be valid decimal numbers')
            if not determine_gissiness():
                raise APIException('this installation is not capable of lat/lon/radius queries')
            from django.contrib.gis.db.models.functions import Distance
            from django.contrib.gis.geos import Point
            from django.contrib.gis.measure import D
            point = Point(x=lon, y=lat, srid=4326)
            queryset = queryset.annotate(distance=Distance('location', point))
            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))
        return queryset


class IssueList(IssueViewBase, ListCreateAPIView):
    serializer_class = IssueSerializer
    queryset = Issue.objects.filter(moderation='public')
    filter_backends = (
        IssueFilter,
    )

    def perform_create(self, serializer):
        super(IssueList, self).perform_create(serializer)
        instance = serializer.instance
        issue_posted.send(sender=self, issue=instance, request=self.request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            [serializer.data],
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class IssueDetail(IssueViewBase, RetrieveAPIView):
    lookup_url_kwarg = "identifier"
    lookup_field = "identifier"
    serializer_class = IssueSerializer

    def get_queryset(self):
        return apply_select_and_prefetch(
            queryset=Issue.objects.all(),
            extensions=get_extensions_from_request(self.request)
        )
