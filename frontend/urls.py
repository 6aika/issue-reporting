from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
import frontend.views

urlpatterns = [
    url(r'^$', frontend.views.mainpage, name='mainpage'),
    url(r'^feedbacks/$', frontend.views.feedback_list, name="feedback_list"),
    url(r'^feedbacks/(?P<feedback_id>\d+)/$', frontend.views.feedback_details, name='feedback_details'),
    url(r'^feedback_form/$', frontend.views.FeedbackWizard.as_view(frontend.views.FORMS), name="feedback_form"),
    url(r'^media_upload/$', frontend.views.media_upload, name="media_upload"),
    url(r'^map/$', frontend.views.map, name="map"),
    url(r'^locations_demo/$', frontend.views.locations_demo, name="locations_demo"),
    url(r'^about/$', frontend.views.about, name="about"),
    url(r'^statistics/$', frontend.views.statistics2, name="statistics"),
    url(r'^heatmap/$', frontend.views.heatmap, name="heatmap"),
    url(r'^department/$', frontend.views.department, name="department"),
    url(r'^charts/$', frontend.views.charts, name="charts"),
    url(r'^vote_feedback/$', frontend.views.vote_feedback, name="vote_feedback")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
