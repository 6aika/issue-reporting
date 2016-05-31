import json
import os

import pytest

from issues.sync.down import update_local_issue


@pytest.mark.django_db
def test_import_taskful_georeport():
    with open(os.path.join(os.path.dirname(__file__), "taskful_request.json"), "r", encoding="utf8") as infp:
        data = json.load(infp)
    issue, created = update_local_issue(data, 'import')
    assert created
    assert issue.tasks.count() == 7
    issue, created = update_local_issue(data, 'import')
    assert not created
    assert issue.tasks.count() == 7
