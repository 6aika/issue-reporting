from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('frontend.urls')),
    url(r'^api/v1/', include('issues.urls', namespace='api/v1')),
]
