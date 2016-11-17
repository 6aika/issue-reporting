# Schemata adapted from
# https://github.com/fge/sample-json-schemas/tree/master/geojson (licensed
# under either of the AFL or BSD license)

GEOJSON_GEOMETRY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "http://json-schema.org/geojson/geometry.json#",
    "title": "geometry",
    "description": "One geometry as defined by GeoJSON",
    "type": "object",
    "required": ["type", "coordinates"],
    "oneOf": [
        {
            "title": "Point",
            "properties": {
                "type": {"enum": ["Point"]},
                "coordinates": {"$ref": "#/definitions/position"}
            }
        },
        {
            "title": "MultiPoint",
            "properties": {
                "type": {"enum": ["MultiPoint"]},
                "coordinates": {"$ref": "#/definitions/positionArray"}
            }
        },
        {
            "title": "LineString",
            "properties": {
                "type": {"enum": ["LineString"]},
                "coordinates": {"$ref": "#/definitions/lineString"}
            }
        },
        {
            "title": "MultiLineString",
            "properties": {
                "type": {"enum": ["MultiLineString"]},
                "coordinates": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/lineString"}
                }
            }
        },
        {
            "title": "Polygon",
            "properties": {
                "type": {"enum": ["Polygon"]},
                "coordinates": {"$ref": "#/definitions/polygon"}
            }
        },
        {
            "title": "MultiPolygon",
            "properties": {
                "type": {"enum": ["MultiPolygon"]},
                "coordinates": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/polygon"}
                }
            }
        }
    ],
    "definitions": {
        "position": {
            "description": "A single position",
            "type": "array",
            "minItems": 2,
            "items": [{"type": "number"}, {"type": "number"}],
            "additionalItems": False
        },
        "positionArray": {
            "description": "An array of positions",
            "type": "array",
            "items": {"$ref": "#/definitions/position"}
        },
        "lineString": {
            "description": "An array of two or more positions",
            "allOf": [
                {"$ref": "#/definitions/positionArray"},
                {"minItems": 2}
            ]
        },
        "linearRing": {
            "description": "An array of four positions where the first equals the last",
            "allOf": [
                {"$ref": "#/definitions/positionArray"},
                {"minItems": 4}
            ]
        },
        "polygon": {
            "description": "An array of linear rings",
            "type": "array",
            "items": {"$ref": "#/definitions/linearRing"}
        }
    }
}

GEOJSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "http://json-schema.org/geojson/geojson.json#",
    "title": "Geo JSON object",
    "description": "Schema for a Geo JSON object",
    "type": "object",
    "required": ["type"],
    "oneOf": [
        {"$ref": "http://json-schema.org/geojson/geometry.json#"},
        {"$ref": "#/definitions/feature"},
    ],
    "definitions": {
        "feature": {
            "title": "Feature",
            "description": "A Geo JSON feature object",
            "required": ["geometry", "properties"],
            "properties": {
                "type": {"enum": ["Feature"]},
                "geometry": {
                    "oneOf": [
                        {"type": "null"},
                        {"$ref": "http://json-schema.org/geojson/geometry.json#"}
                    ]
                },
                "properties": {"type": ["object", "null"]},
                "id": {"FIXME": "may be there, type not known (string? number?)"}
            }
        },
    }
}
