from django.utils import translation
from rest_framework.generics import ListAPIView

from issues.api.serializers import ServiceSerializer
from issues.models import Service


class ServiceList(ListAPIView):
    item_tag_name = 'service'
    root_tag_name = 'services'
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()

    def initial(self, request, *args, **kwargs):
        super(ServiceList, self).initial(request, *args, **kwargs)
        locale = request.query_params.get("locale")
        if locale:
            translation.activate(locale)
