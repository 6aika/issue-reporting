from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.models import Service
from api.services import get_feedbacks
from .serializers import FeedbackSerializer, ServiceSerializer


class FeedbackViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def list(self, request):
        service_object_id = request.query_params.get('service_object_id', None)
        service_object_type = request.query_params.get('service_object_type', None)

        if service_object_id is not None and service_object_type is None:
            raise ValidationError(
                    "If service_object_id is included in the request, then service_object_type must be included.")

        queryset = get_feedbacks(
                service_request_ids=request.query_params.get('service_request_id', None),
                service_codes=request.query_params.get('service_code', None),
                start_date=request.query_params.get('start_date', None),
                end_date=request.query_params.get('end_date', None),
                statuses=request.query_params.get('status', None),
                service_object_type=service_object_type,
                service_object_id=service_object_id,
                lat=request.query_params.get('lat', None),
                lon=request.query_params.get('long', None),
                radius=request.query_params.get('radius', None),
                updated_after=request.query_params.get('updated_after', None),
                updated_before=request.query_params.get('updated_before', None),
                search=request.query_params.get('search', None),
                order_by=request.query_params.get('order_by', None)
        )

        serializer = FeedbackSerializer(queryset, many=True,
                                        context={'extensions': request.query_params.get('extensions', 'false')})
        return Response(serializer.data)


class ServiceViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Service.objects.all()
        # TODO: add localization
        serializer = ServiceSerializer(queryset, many=True,
                                       context={'extensions': request.query_params.get('locale', 'en')})

        return Response(serializer.data)
