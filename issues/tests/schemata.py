STRING_OR_NULL = {"anyOf": [{"type": "string"}, {"type": "null"}]}
NUMERIC_STRING = {
    "type": "string",
    "pattern": r"^-?[0-9]*(\.[0-9]+)?$"
}

NUMBER_OR_NUMERIC_STRING = {
    "anyOf": [
        {"type": "number"},
        NUMERIC_STRING
    ]
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
        "lat": NUMBER_OR_NUMERIC_STRING,
        "long": NUMBER_OR_NUMERIC_STRING,
        "media_url": STRING_OR_NULL,
        "extended_attributes": {"type": "object"},
        "distance": NUMBER_OR_NUMERIC_STRING,  # Not in the actual schema
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

LIST_OF_ISSUES_SCHEMA = {
    "type": "array",
    "items": ISSUE_SCHEMA
}
