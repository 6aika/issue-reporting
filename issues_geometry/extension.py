import json

import six
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from rest_framework import serializers

from issues.api.utils import JSONInXML
from issues.extensions import IssueExtension
from issues_geometry.validation import GeoJSONValidator


class GeoJSONField(serializers.JSONField):

    def to_internal_value(self, data):
        if isinstance(data, six.binary_type):  # pragma: no cover
            data = data.decode('utf-8')
        if isinstance(data, six.text_type):  # pragma: no branch
            data = json.loads(data)
        if not isinstance(data, dict):
            self.fail('invalid')
        errors = [e.message for e in GeoJSONValidator.iter_errors(data)]
        if errors:
            raise serializers.ValidationError("Invalid GeoJSON (%d validation errors):\n%s" % (
                len(errors),
                "\n".join(errors)
            ))
        return data


class GeometryExtension(IssueExtension):
    identifier = 'geometry'
    related_name = 'geometry'

    def get_extended_attributes(self, issue, context=None):
        try:
            geo_data = issue.geometry.geometry
            assert isinstance(geo_data, GEOSGeometry)
            return {
                'geometry': JSONInXML({
                    'srid': geo_data.srid,
                    'type': geo_data.__class__.__name__,
                    'coordinates': geo_data.coords,
                }),
            }
        except ObjectDoesNotExist:
            return {}

    def extend_issue_serializer(self, serializer):
        from issues_geometry.models import DEFAULT_SRID
        serializer.fields['geometry'] = GeoJSONField(write_only=True, required=False)
        serializer.fields['srid'] = serializers.IntegerField(write_only=True, required=False, default=DEFAULT_SRID)

    def validate_issue_data(self, serializer, data):
        from issues_geometry.models import DEFAULT_SRID
        geojson = data.pop('geometry', None)
        if geojson:
            if geojson.get('geometry'):  # Peel off a feature; otherwise trying to GEOS it will fail
                geojson = geojson['geometry']
            geometry = data['geometry'] = GEOSGeometry(
                json.dumps(geojson),
                srid=data.pop('srid', DEFAULT_SRID),
            )
            data['long'], data['lat'] = geometry.centroid

        return super(GeometryExtension, self).validate_issue_data(serializer, data)

    def post_create_issue(self, request, issue, data):
        from issues_geometry.models import IssueGeometry
        geometry = data.pop('geometry', None)
        if geometry:
            IssueGeometry.objects.create(issue=issue, geometry=geometry)
