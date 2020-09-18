from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path(settings.GEOREPORT_API_ROOT, include('issues.api.urls', namespace='georeport/v2')),
]

if 'issues_simple_ui' in settings.INSTALLED_APPS:
    urlpatterns.append(path(r'', include('issues_simple_ui.urls')))

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib.admin.sites import site

    urlpatterns.append(path('admin/', site.urls))

if settings.DEBUG:  # pragma: no cover
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
