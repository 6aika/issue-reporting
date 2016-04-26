import pytest
from rest_framework.test import APIClient


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
