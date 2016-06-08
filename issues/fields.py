import re

from django.db.models import CharField
from six import string_types

from issues.gis import determine_gissiness

try:
    from django.contrib.gis.geos import Point
except:
    Point = None

GEOS_POINT_EXPRESSION_RE = re.compile(r'.*POINT \((?P<lon>.+?) (?P<lat>.+?)\)')


def _string_value_to_coords(value):
    geos_match = GEOS_POINT_EXPRESSION_RE.match(value)
    if geos_match:
        value = "%(lon)s;%(lat)s" % geos_match.groupdict()
    latlng = tuple(float(c) for c in value.split(";"))
    assert len(latlng) == 2
    assert all(-180 < c < 180 for c in latlng)
    return latlng


class GeoPointFieldFallback(CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 128)
        kwargs['db_index'] = False
        kwargs.pop('srid', False)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return None
        latlng = _string_value_to_coords(value)
        return latlng

    def to_python(self, value):
        if (Point and isinstance(value, Point)) or isinstance(value, (list, tuple)):
            value = "%s;%s" % (value[0], value[1])

        return self.from_db_value(value, None, None, None)

    def get_prep_value(self, value):
        if not value:
            return None
        if isinstance(value, string_types):
            lat, lng = _string_value_to_coords(value)
        else:
            lat, lng = [float(c) for c in value]
        return "%r;%r" % (lat, lng)


if determine_gissiness():
    from django.contrib.gis.db.models.fields import PointField as _GISPointField

    class GeoPointField(_GISPointField):
        def __init__(self, verbose_name=None, dim=2, **kwargs):
            kwargs['geography'] = True
            kwargs['srid'] = 4326
            super().__init__(verbose_name, dim, **kwargs)
else:
    class GeoPointField(GeoPointFieldFallback):
        pass
