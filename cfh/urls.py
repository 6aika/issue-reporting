from django.conf import settings
from django.conf.urls import include, url

urlpatterns = [
    url(r'^%s' % settings.GEOREPORT_API_ROOT, include('issues.api.urls', namespace='georeport/v2')),
]

if settings.DEBUG and "django.contrib.admin" in settings.INSTALLED_APPS:  # pragma: no cover
    from django.contrib.admin.sites import site

    urlpatterns.append(url(r'^admin/', site.urls))
