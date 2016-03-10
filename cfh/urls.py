from django.conf.urls import url, include

urlpatterns = [
    url(r'', include('frontend.urls')),
    url(r'^api/v1/', include('api.urls', namespace='api/v1')),
]
