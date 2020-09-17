import pytest
from django.conf import settings

from issues.gis import determine_gissiness

GISSY = {
    'django.contrib.gis.db.backends.postgis': True,
    'django.db.backends.mysql': False,
    'django.db.backends.sqlite3': False,
}


def test_gissiness():
    """
    Test that determine_gissiness() correctly determines gissiness for known databases.
    :return:
    """
    engine = settings.DATABASES['default']['ENGINE']
    if engine not in GISSY:
        pytest.skip(f'I have no idea whether {engine} should be gissy')
    assert GISSY[engine] == determine_gissiness()
