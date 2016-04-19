from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from issues import views

urlpatterns = [
    url(r'^requests/$', views.FeedbackList.as_view(), name='feedback-list'),
    url(r'^requests/(?P<service_request_id>\w+)/$', views.FeedbackDetail.as_view(), name='feedback-details'),
    url(r'^services/$', views.ServiceList.as_view(), name='service-list'),
    url(r'^agencies/$', views.get_agency_responsible_list, name='agency-responsible-list'),
    url(r'^statistics/services/$', views.get_services_statistics, name='statistics-services'),
    url(r'^statistics/services/(?P<service_code>\d+)/$', views.get_service_statistics, name='statistics-service'),
    url(r'^statistics/agencies/$', views.get_agencies_statistics, name='statistics-agencies'),
    url(r'^statistics/agencies/(?P<agency>\w+)/$', views.get_agency_statistics, name='statistics-agency'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
