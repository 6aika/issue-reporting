import pytest
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from issues.models import Issue, Service
from issues.tests.db_utils import execute_fixture


def pytest_configure():
    # During tests, crypt passwords with MD5. This should make things run faster.
    from django.conf import settings
    settings.PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.CryptPasswordHasher',
    )


@pytest.fixture()
def admin_api_client(admin_user):
    api_client = APIClient()
    api_client.login(username=admin_user.username, password="password")
    api_client.user = admin_user
    return api_client


@pytest.fixture()
def api_client():
    return APIClient()


class FormatEnforcingAPIClient(APIClient):
    format = None  # Set by the fixture

    def get(self, path, data=None, follow=False, **extra):
        if not data:
            data = {}
        data["format"] = self.format
        resp = super().get(path, data, follow, **extra)
        self._check_response_format(resp)
        return resp

    def post(self, path, data=None, format=None, content_type=None, follow=False, **extra):
        assert not format
        assert not content_type
        resp = super().post(self._format_path(path), data=data, follow=follow, **extra)
        self._check_response_format(resp)
        return resp

    def _check_response_format(self, resp):
        if resp.status_code < 400:
            if self.format == "sjson":
                assert "json" in resp["Content-Type"]
            else:
                assert self.format in resp["Content-Type"]

    def _format_path(self, path):
        return '{}{}format={}'.format(
            path,
            ('&' if '?' in path else '?'),
            self.format
        )


@pytest.fixture(params=['xml', 'json', 'sjson'])
def mf_api_client(request):
    # mf_api_client is short for multiformat_api_client, fwiw. :)
    feac = FormatEnforcingAPIClient()
    feac.format = request.param
    return feac


@pytest.fixture()
def random_service(db):
    return Service.objects.create(
        service_code=get_random_string(),
        service_name="Test"
    )


@pytest.fixture()
def testing_issues(db):
    execute_fixture('insert_requests')
    return Issue.objects.all()
