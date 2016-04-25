from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views.issues import IssueDetail, IssueList
from .views.services import ServiceList
from .views.statistics import (
    get_agencies_statistics, get_agency_responsible_list, get_agency_statistics, get_service_statistics,
    get_services_statistics
)

urlpatterns = [
    url(r'^requests/$', IssueList.as_view(), name='issue-list'),
    url(r'^requests/(?P<service_request_id>\w+)/$', IssueDetail.as_view(), name='issue-details'),
    url(r'^services/$', ServiceList.as_view(), name='service-list'),
    url(r'^agencies/$', get_agency_responsible_list, name='agency-responsible-list'),
    url(r'^statistics/services/$', get_services_statistics, name='statistics-services'),
    url(r'^statistics/services/(?P<service_code>\d+)/$', get_service_statistics, name='statistics-service'),
    url(r'^statistics/agencies/$', get_agencies_statistics, name='statistics-agencies'),
    url(r'^statistics/agencies/(?P<agency>\w+)/$', get_agency_statistics, name='statistics-agency'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
