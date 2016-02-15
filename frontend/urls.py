from django.conf.urls import url

from frontend.views import locations_demo

urlpatterns = [
    url(r'^$', locations_demo, name='locations_demo')
]
