import django.contrib.auth.views as auth_views
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from issues_simple_ui.views import SimpleContentView
from issues_simple_ui.views.admin_views import AdminDetailView, AdminListView

urlpatterns = [
    url(
        r'^admin/issues/(?P<pk>\d+)/$',
        staff_member_required(AdminDetailView.as_view()),
        name='admin-issue-detail',
    ),
    url(
        r'^admin/issues/$',
        staff_member_required(AdminListView.as_view()),
        name='admin-issue-list',
    ),
    url(
        r'^login/',
        view=auth_views.LoginView.as_view(),
        kwargs=dict(
            template_name='issues_simple_ui/login.html',
        ),
    ),

    url(
        r'^logout/',
        view=auth_views.LogoutView.as_view(),
        kwargs=dict(next_page='/'),
    ),
    url(r'^report/$', SimpleContentView.as_view(
        content_identifier='report',
        template_name='issues_simple_ui/report.html',
    ), name='report-issue'),
    url(r'^browse/$', SimpleContentView.as_view(
        content_identifier='browse',
        template_name='issues_simple_ui/browse.html',
    ), name='browse-issues'),
    url(r'^$', SimpleContentView.as_view(
        template_name='issues_simple_ui/index.html',
        content_identifier='index',
    )),
]
