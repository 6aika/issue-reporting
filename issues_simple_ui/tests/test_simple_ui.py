import pytest
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.crypto import get_random_string

from issues.models import Issue
from issues_simple_ui.models import Content

if 'issues_simple_ui' not in settings.INSTALLED_APPS:
    pytest.skip('app disabled')


@pytest.mark.django_db
def test_simple_ui_content(client):
    Content.objects.create(
        identifier='index',
        title='Hello!',
        content='World!',
    )
    content = client.get('/').content.decode('utf-8')
    assert 'Hello!' in content
    assert 'World!' in content


@pytest.mark.django_db
def test_simple_ui_admin(admin_client):
    issue = Issue.objects.create(
        description=get_random_string(),
    )
    list_content = admin_client.get(resolve_url('admin-issue-list')).content.decode('utf-8')
    assert issue.description in list_content
    detail_content = admin_client.get(resolve_url('admin-issue-detail', pk=issue.pk)).content.decode('utf-8')
    assert issue.description in detail_content
