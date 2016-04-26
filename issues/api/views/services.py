from rest_framework.generics import ListAPIView

from issues.api.serializers import ServiceSerializer
from issues.models import Service


class ServiceList(ListAPIView):
    item_tag_name = 'service'
    root_tag_name = 'services'
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
