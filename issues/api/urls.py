from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views.statistics import (
    get_agencies_statistics, get_agency_responsible_list, get_agency_statistics, get_service_statistics,
    get_services_statistics
)
from .viewsets import IssueViewSet, ServiceViewSet

app_name = 'issues'

router = DefaultRouter()

router.register('requests', IssueViewSet, basename='issue')
router.register('services', ServiceViewSet, basename='service')

urlpatterns = router.urls + format_suffix_patterns([
    path('agencies/$', get_agency_responsible_list, name='agency-responsible-list'),
    path('statistics/services/$', get_services_statistics, name='statistics-services'),
    path('statistics/services/{service_code:int}/$', get_service_statistics, name='statistics-service'),
    path('statistics/agencies/$', get_agencies_statistics, name='statistics-agencies'),
    path('statistics/agencies/{agency}/$', get_agency_statistics, name='statistics-agency'),
])
