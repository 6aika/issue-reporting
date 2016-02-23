from django.conf.urls import url, include

from api.urls import router

urlpatterns = [
    url(r'', include('frontend.urls')),
    url(r'^api/v1/', include(router.urls)),
]
