import json


def get_data_from_response(response, status_code=200):
    if status_code:  # pragma: no branch
        assert response.status_code == status_code, (
            "Status code mismatch (%s is not the expected %s)" % (response.status_code, status_code)
        )
    return json.loads(response.content.decode('utf-8'))
