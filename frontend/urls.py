from django.conf.urls import url

import frontend.views

urlpatterns = [
    url(r'^$', frontend.views.mainpage, name='mainpage'),
    url(r'^feedbacks/$', frontend.views.feedback_list, name="feedback_list"),
    url(r'^feedback_form/$', frontend.views.FeedbackWizard.as_view(frontend.views.FORMS), name="feedback_form"),
    url(r'^map/$', frontend.views.map, name="map"),
    url(r'^locations_demo/$', frontend.views.locations_demo, name="locations_demo"),
    url(r'^instructions/$', frontend.views.instructions, name="instructions"),
    url(r'^statistic/$', frontend.views.statistic_page, name="statistic"),
    url(r'^vote_feedback/$', frontend.views.vote_feedback, name="vote_feedback")
]
