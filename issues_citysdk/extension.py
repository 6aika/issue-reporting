from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from issues.extensions import IssueExtension


class CitySDKExtension(IssueExtension):
    identifier = 'citysdk'
    related_name = 'citysdk'

    def filter_issue_queryset(self, request, queryset, view):
        search = request.query_params.get('search')

        service_object_id = request.query_params.get('service_object_id')
        service_object_type = request.query_params.get('service_object_type')

        if bool(service_object_id) ^ bool(service_object_type):
            raise ValidationError(
                "Both service_object_id and service_object_type or neither of them must be included in a request."
            )

        if search:
            queryset = (
                queryset.filter(description__icontains=search) |
                queryset.filter(citysdk__title__icontains=search) |
                queryset.filter(address__icontains=search) |
                queryset.filter(agency_responsible__icontains=search)
            )

        if service_object_type:
            queryset = queryset.filter(citysdk__service_object_type__icontains=service_object_type)
        if service_object_id:
            queryset = queryset.filter(citysdk__service_object_id=service_object_id)

        return queryset

    def get_extended_attributes(self, issue, context=None):
        try:
            cs_ext = issue.citysdk
        except ObjectDoesNotExist:
            return None
        return {
            'service_object_type': cs_ext.service_object_type,
            'service_object_id': cs_ext.service_object_id,
            'detailed_status': cs_ext.detailed_status,
            'title': cs_ext.title,
        }

    def extend_issue_serializer(self, serializer):
        serializer.fields['service_object_id'] = serializers.CharField(write_only=True, required=False)
        serializer.fields['service_object_type'] = serializers.CharField(write_only=True, required=False)
        serializer.fields['title'] = serializers.CharField(write_only=True, required=False)

    def validate_issue_data(self, serializer, data):
        if bool(data.get('service_object_id')) ^ bool(data.get('service_object_type')):
            raise ValidationError('both service_object_id and service_object_type must be set if one is')
        return data

    def post_create_issue(self, request, issue, data):
        from issues_citysdk.models import Issue_CitySDK
        service_object_id = data.pop('service_object_id', None)
        service_object_type = data.pop('service_object_type', None)

        ext_data = {}
        if service_object_id and service_object_type:
            ext_data.update(
                service_object_id=service_object_id,
                service_object_type=service_object_type,
            )

        title = data.pop('title', None)
        if title:
            ext_data['title'] = title

        if ext_data:
            Issue_CitySDK.objects.create(issue=issue, **ext_data)
