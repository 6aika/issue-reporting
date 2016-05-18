import json

import jsonschema

from issues.api.transforms import transform_xml_to_json


def get_data_from_response(response, status_code=200, schema=None):
    if status_code:  # pragma: no branch
        assert response.status_code == status_code, (
            "Status code mismatch (%s is not the expected %s)" % (response.status_code, status_code)
        )

    if response["Content-Type"].startswith("application/xml"):
        response.xml = response.content
        response.content = transform_xml_to_json(response.content)
        response["Content-Type"] = "application/json"

    data = json.loads(response.content.decode('utf-8'))
    if schema:
        jsonschema.validate(data, schema)
    return data
