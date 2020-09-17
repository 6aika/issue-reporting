from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models.fields import GeometryField
from six import python_2_unicode_compatible

DEFAULT_SRID = getattr(settings, 'ISSUES_GEOMETRY_SRID', 4326)


class ConfigurableGeometryField(GeometryField):

    def __init__(self, **kwargs):
        kwargs['srid'] = DEFAULT_SRID
        super().__init__(**kwargs)

    def deconstruct(self):  # pragma: no cover
        (name, path, args, kwargs) = super().deconstruct()
        kwargs.pop('srid', None)  # We deal with this in the ctor
        return (name, path, args, kwargs)


class IssueGeometry(models.Model):
    issue = models.OneToOneField('issues.Issue', on_delete=models.CASCADE, related_name='geometry')
    geometry = ConfigurableGeometryField()

    def __str__(self):  # pragma: no cover
        return "Geometry for %s" % self.issue
