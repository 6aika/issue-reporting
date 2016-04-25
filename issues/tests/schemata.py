STRING_OR_NULL = {"anyOf": [{"type": "string"}, {"type": "null"}]}
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
        "service_notice": {"type": "string"},
        "requested_datetime": {"type": "string"},
        "updated_datetime": STRING_OR_NULL,
        "expected_datetime": STRING_OR_NULL,
        "address": {"type": "string"},
        "address_id": {"type": "string"},
        "zipcode": {"type": "string"},
        "lat": {"type": "number"},
        "long": {"type": "number"},
        "media_url": {"type": "string"},
        "extended_attributes": {"type": "object"}
    },
    "required": [
        "service_request_id",
        "status",
        "service_name",
        "service_code",
        "description",
        "agency_responsible",
        "service_notice",
        "requested_datetime",
        "updated_datetime",
        "expected_datetime",
    ]
}
