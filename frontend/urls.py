from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

import frontend.views

urlpatterns = [
    url(r'^$', frontend.views.mainpage, name='mainpage'),
    url(r'^issues/$', frontend.views.issue_list, name="issue_list"),
    url(r'^issues/(?P<issue_id>\d+)/$', frontend.views.issue_details, name='issue_details'),
    url(r'^issue_form/$', frontend.views.IssueWizard.as_view(frontend.views.FORMS), name="issue_form"),
    url(r'^media_upload/$', frontend.views.media_upload, name="media_upload"),
    url(r'^map/$', frontend.views.map, name="map"),
    url(r'^about/$', frontend.views.about, name="about"),
    url(r'^statistics/$', frontend.views.statistics, name="statistics"),
    url(r'^department/$', frontend.views.department, name="department"),
    url(r'^charts/$', frontend.views.charts, name="charts"),
    url(r'^vote_issue/$', frontend.views.vote_issue, name="vote_issue")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
