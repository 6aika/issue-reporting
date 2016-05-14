STRING_OR_NULL = {"anyOf": [{"type": "string"}, {"type": "null"}]}
NUMERIC_STRING = {
    "type": "string",
    "pattern": "^-?[0-9]*(\.[0-9]+)?$"
}

ISSUE_SCHEMA = {
    "type": "object",
    "properties": {
        "service_request_id": {"type": "string"},
        "status": {"type": "string"},
        "status_notes": {"type": "string"},
        "service_name": {"type": "string"},
        "service_code": {"type": "string"},
        "description": {"type": "string"},
        "agency_responsible": {"type": "string"},
        "service_notice": STRING_OR_NULL,
        "requested_datetime": {"type": "string"},
        "updated_datetime": STRING_OR_NULL,
        "expected_datetime": STRING_OR_NULL,
        "address": {"type": "string"},
        "address_id": {"type": "string"},
        "zipcode": {"type": "string"},
        "lat": NUMERIC_STRING,
        "long": NUMERIC_STRING,
        "media_url": STRING_OR_NULL,
        "extended_attributes": {"type": "object"},
        "distance": NUMERIC_STRING,  # Not in the actual schema
    },
    "additionalProperties": False,
    "required": [
        "service_request_id",
        "status",
        "service_name",
        "service_code",
        "description",
        "requested_datetime",
        "updated_datetime",
        "expected_datetime",
    ]
}
