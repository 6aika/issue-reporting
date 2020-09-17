from django.utils import translation
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import ListAPIView

from issues.api.serializers import ServiceSerializer
from issues.models import Service


class ServiceFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        jurisdiction_id = request.query_params.get('jurisdiction_id')
        if jurisdiction_id:
            queryset = queryset.filter(jurisdictions__identifier=jurisdiction_id)
        return queryset


class ServiceList(ListAPIView):
    item_tag_name = 'service'
    root_tag_name = 'services'
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    filter_backends = (
        ServiceFilter,
    )

    def dispatch(self, request, *args, **kwargs):
        locale = (request.GET.get("locale") or translation.get_language())
        with translation.override(locale):
            return super().dispatch(request, *args, **kwargs)
