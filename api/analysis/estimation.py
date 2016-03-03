import datetime

from ..models import Feedback
from django.db.models import ExpressionWrapper, F, fields

# def calc_fixing_time(service_code):
#     requests = Feedback.objects.filter(service_code=service_code, status='closed').all()

#     diffs = []
#     for request in requests:

#         if request.service_code == str(service_code):
#             a = request.requested_datetime
#             b = request.updated_datetime

#             diff = b - a
#             diffs.append(diff)

#     if len(diffs) == 0:
#         return 0

#     total_time = sum(diffs, datetime.timedelta())
#     average_time = total_time / len(diffs)
#     return timedelta_milliseconds(average_time)

def calc_fixing_time(service_code):
    return timedelta_milliseconds(get_avg_duration(service_code))

# Return total number of feedbacks with either "open" or "closed" status-
def get_total(service_code):
    return Feedback.objects.filter(service_code=service_code, status__in=["open", "closed"]).count()

# return total number of feedbacks with "closed" status
def get_closed(service_code):
    return Feedback.objects.filter(service_code=service_code, status="closed").count()

# TODO: This will be replaced with more generic get_feedbacks() taking a dict
def get_closed_by_service_code(service_code):
    return Feedback.objects.filter(service_code=service_code, status="closed")

# Returns average duration of closed feedbacks (updated_datetime - requested_datetime)
# from given category. Returns a tuple (days, hours)
def get_avg_duration(query_set):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = query_set.annotate(duration=duration).values_list("duration", flat=True)
    return sum(duration_list, datetime.timedelta(0)) / len(duration_list)

# Returns median duration of closed feedbacks (updated_datetime - requested_datetime)
# from given category. Returns a tuple (days, hours)
def get_median_duration(query_set):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = sorted(query_set.annotate(duration=duration).values_list("duration", flat=True))
    return duration_list[(len(duration_list)-1)//2]

# Converts timedelta into tuple (days, hours)
def timedelta_days_hours(td):
    return (td.days, td.seconds//3600)

# Concerts timedelta into millisoconds
def timedelta_milliseconds(td):
    return int(td.days * 86400000 + td.seconds * 1000 + td.microseconds / 1000)
