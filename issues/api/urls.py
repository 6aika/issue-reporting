from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.viewsets import ViewSet

from .views.issues import IssueDetail, IssueList
from .views.services import ServiceList
from .views.statistics import (
    get_agencies_statistics, get_agency_responsible_list, get_agency_statistics, get_service_statistics,
    get_services_statistics
)


class IssueViewSet(IssueList, IssueDetail, ViewSet):
    pass


class ServiceViewSet(ServiceList, ViewSet):
    pass


router = DefaultRouter()

router.register('requests', IssueViewSet, base_name='issue')
router.register('services', ServiceViewSet, base_name='service')

urlpatterns = router.urls + format_suffix_patterns([
    url(r'^agencies/$', get_agency_responsible_list, name='agency-responsible-list'),
    url(r'^statistics/services/$', get_services_statistics, name='statistics-services'),
    url(r'^statistics/services/(?P<service_code>\d+)/$', get_service_statistics, name='statistics-service'),
    url(r'^statistics/agencies/$', get_agencies_statistics, name='statistics-agencies'),
    url(r'^statistics/agencies/(?P<agency>\w+)/$', get_agency_statistics, name='statistics-agency'),
])
