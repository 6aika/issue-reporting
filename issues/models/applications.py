from __future__ import absolute_import
from django.db import models
from django.utils.crypto import get_random_string

from issues.excs import InvalidAppError

DEFAULT_APP_DATA = {  # Used by `.autodetermine()` and the migration
    'identifier': 'default',
    'name': 'Default',
    'key': ''
}


def generate_api_key():
    return get_random_string(30)


class Application(models.Model):
    active = models.BooleanField(default=True, db_index=True)
    identifier = models.CharField(
        max_length=64,
        db_index=True,
        help_text='a machine-readable name for this app (a package identifier, for instance)',
    )
    name = models.CharField(
        max_length=64,
        help_text='a human-readable name for this app',
    )
    key = models.CharField(max_length=32, unique=True, default=generate_api_key, editable=False)

    @staticmethod
    def autodetermine():
        app_count = Application.objects.count()
        if app_count == 0:
            return Application.objects.create(**DEFAULT_APP_DATA)
        elif app_count == 1:
            return Application.objects.filter(key='').first()
        raise InvalidAppError('There are %d applications, so a valid API key must be passed in' % app_count)

    def __str__(self):
        return self.name
