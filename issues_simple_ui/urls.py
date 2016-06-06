from django.conf.urls import url

from issues_simple_ui.views import SimpleContentView

urlpatterns = [
    url(r'^$', SimpleContentView.as_view(
        template_name='issues_simple_ui/index.html',
        content_identifier='index',
    )),
    url(r'^report/$', SimpleContentView.as_view(
        content_identifier='report',
        template_name='issues_simple_ui/report.html',
    ), name='report-issue'),
    url(r'^browse/$', SimpleContentView.as_view(
        content_identifier='browse',
        template_name='issues_simple_ui/browse.html',
    ), name='browse-issues'),
]
