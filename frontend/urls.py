from django.conf.urls import url

import frontend.views

urlpatterns = [
    url(r'^$', frontend.views.mainpage, name='mainpage'),
    url(r'^feedbacks/$', frontend.views.feedback_list, name="feedback_list"),
    url(r'^map/$', frontend.views.map, name="map")
]
