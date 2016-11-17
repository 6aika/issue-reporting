from jsonschema import Draft4Validator, RefResolver

from issues_geometry.schemata import GEOJSON_GEOMETRY_SCHEMA, GEOJSON_SCHEMA


class LocalRefResolver(RefResolver):

    def resolve_remote(self, uri):  # pragma: no cover
        # (this should never happen)
        raise NotImplementedError("remote refs not supported (uri: %s)" % uri)


Draft4Validator.check_schema(GEOJSON_SCHEMA)
Draft4Validator.check_schema(GEOJSON_GEOMETRY_SCHEMA)
resolver = LocalRefResolver.from_schema(GEOJSON_SCHEMA)
resolver.store[GEOJSON_GEOMETRY_SCHEMA['id']] = GEOJSON_GEOMETRY_SCHEMA
GeoJSONValidator = Draft4Validator(schema=GEOJSON_SCHEMA, resolver=resolver)
