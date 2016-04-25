from rest_framework.response import Response
from rest_framework.views import APIView

from issues.api.serializers import ServiceSerializer
from issues.models import Service


class ServiceList(APIView):
    item_tag_name = 'service'
    root_tag_name = 'services'

    def get(self, request, format=None):
        queryset = Service.objects.all()
        serializer = ServiceSerializer(queryset, many=True)

        return Response(serializer.data)
