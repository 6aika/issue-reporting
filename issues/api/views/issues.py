from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models.sql import DistanceField
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.db.models import Case, When
from rest_framework.exceptions import APIException
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView

from issues.api.serializers import IssueSerializer
from issues.signals import issue_posted
from issues.extensions import apply_select_and_prefetch, get_extensions_from_request
from issues.gis import determine_gissiness
from issues.models import Issue


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

        queryset = self._apply_citysdk_filter(request, queryset)
        queryset = apply_select_and_prefetch(queryset=queryset, extensions=extensions)

        for ex in extensions:
            queryset = ex.filter_issue_queryset(request, queryset, view)

        order_by = request.query_params.get('order_by')

        if order_by:
            queryset = queryset.order_by(order_by)

        # TODO: Implement pagination

        return queryset

    def _apply_citysdk_filter(self, request, queryset):
        # Strictly speaking these are not queries that should be possible with a GeoReport v2
        # core implementation, but as they do not require extra data in the models, it's worth it
        # to have them available "for free".

        lat = request.query_params.get('lat')
        lon = request.query_params.get('long')
        radius = request.query_params.get('radius')
        updated_after = request.query_params.get('updated_after')
        updated_before = request.query_params.get('updated_before')
        if updated_after:
            queryset = queryset.filter(updated_datetime__gt=updated_after)
        if updated_before:
            queryset = queryset.filter(updated_datetime__lt=updated_before)
        if lat and lon and radius:
            if not determine_gissiness():
                raise APIException('this installation is not capable of lat/lon/radius queries')
            point = fromstr('SRID=4326;POINT(%s %s)' % (lon, lat))
            empty_point = fromstr('POINT(0 0)', srid=4326)
            queryset = queryset.annotate(distance=Case(
                When(location__distance_gt=(empty_point, D(m=0.0)), then=Distance('location', point)),
                default=None,
                output_field=DistanceField('m')
            ))

            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))
        return queryset


class IssueList(IssueViewBase, ListCreateAPIView):
    serializer_class = IssueSerializer
    queryset = Issue.objects.filter(moderation='public')
    filter_backends = (
        IssueFilter,
    )

    def perform_create(self, serializer):
        request = self.request
        new_issue = serializer.save()
        extensions = get_extensions_from_request(request)
        for ex in extensions:
            ex.post_create_issue(request=request, issue=new_issue)
        issue_posted.send(sender=self, issue=new_issue, request=request)


class IssueDetail(IssueViewBase, RetrieveAPIView):
    lookup_url_kwarg = "identifier"
    lookup_field = "identifier"
    serializer_class = IssueSerializer

    def get_queryset(self):
        return apply_select_and_prefetch(
            queryset=Issue.objects.all(),
            extensions=get_extensions_from_request(self.request)
        )
