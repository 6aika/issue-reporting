from django.db import connection

from api.models import Feedback


def clear_db():
    Feedback.objects.all().delete()


def read_query(query_name):
    with open('api/tests/sql/' + query_name + '.sql') as sql:
        return sql.read()


def insert_feedbacks():
    query = read_query('insert_requests')
    cursor = connection.cursor()
    cursor.execute(query)


def insert_feedbacks_for_estimation():
    query = read_query('insert_requests_for_estimation')
    cursor = connection.cursor()
    cursor.execute(query)
