from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from issues.gis import determine_gissiness
from issues_geometry.extension import GeometryExtension


class IssuesGeometryConfig(AppConfig):
    name = 'issues_geometry'
    issue_extension = GeometryExtension
    verbose_name = 'Issues: Geometry Extensions'

    def ready(self):
        if not determine_gissiness():  # pragma: no cover
            raise ImproperlyConfigured('the geometry extension requires a GIS-enabled database')
