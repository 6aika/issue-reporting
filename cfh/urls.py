from django.conf.urls import include, url

urlpatterns = [
    url(r'^api/v1/', include('issues.api.urls', namespace='api/v1')),
]
