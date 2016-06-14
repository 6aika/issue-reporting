from jsonschema import RefResolver, Draft4Validator

from issues_geometry.schemata import GEOJSON_SCHEMA, GEOJSON_GEOMETRY_SCHEMA


class LocalRefResolver(RefResolver):

    def resolve_remote(self, uri):  # pragma: no cover
        # (this should never happen)
        raise NotImplementedError("remote refs not supported (uri: %s)" % uri)


Draft4Validator.check_schema(GEOJSON_SCHEMA)
Draft4Validator.check_schema(GEOJSON_GEOMETRY_SCHEMA)
resolver = LocalRefResolver.from_schema(GEOJSON_SCHEMA)
resolver.store[GEOJSON_GEOMETRY_SCHEMA['id']] = GEOJSON_GEOMETRY_SCHEMA
GeoJSONValidator = Draft4Validator(schema=GEOJSON_SCHEMA, resolver=resolver)
