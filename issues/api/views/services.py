from __future__ import absolute_import
from django.utils import translation
from rest_framework.generics import ListAPIView

from issues.api.serializers import ServiceSerializer
from issues.models import Service


class ServiceList(ListAPIView):
    item_tag_name = 'service'
    root_tag_name = 'services'
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()

    def dispatch(self, request, *args, **kwargs):
        locale = (request.GET.get("locale") or translation.get_language())
        with translation.override(locale):
            return super(ServiceList, self).dispatch(request, *args, **kwargs)
