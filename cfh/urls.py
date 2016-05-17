from django.conf.urls import include, url

urlpatterns = [
    url(r'^api/georeport/v2/', include('issues.api.urls', namespace='georeport/v2')),
]
