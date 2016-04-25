import os

from django.core import serializers
from django.db import connections

from issues.models import Issue

FIXTURE_DIR = os.path.dirname(__file__)


def clear_db():
    Issue.objects.all().delete()


def execute_fixture(name):
    filename = os.path.join(FIXTURE_DIR, name + '.json')
    connection = connections["default"]
    with connection.constraint_checks_disabled():
        with open(filename, "r") as stream:
            objects = serializers.deserialize("json", stream)
            for obj in objects:
                obj.save()


def insert_issues():
    execute_fixture('insert_requests')


def insert_issues_for_estimation():
    execute_fixture('insert_requests_for_estimation')
