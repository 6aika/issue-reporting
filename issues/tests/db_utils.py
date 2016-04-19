import os

from django.db import connection

from issues.models import Feedback

QUERY_ROOT_DIR = os.path.join(os.path.dirname(__file__), 'sql')


def clear_db():
    Feedback.objects.all().delete()


def read_query(query_name):
    with open(os.path.join(QUERY_ROOT_DIR, query_name + '.sql')) as sql:
        return sql.read()


def insert_feedbacks():
    query = read_query('insert_requests')
    cursor = connection.cursor()
    cursor.execute(query)


def insert_feedbacks_for_estimation():
    query = read_query('insert_requests_for_estimation')
    cursor = connection.cursor()
    cursor.execute(query)
