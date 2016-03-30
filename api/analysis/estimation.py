import datetime

from django.db.models import ExpressionWrapper, F, fields

from api.services import get_feedbacks
from ..models import Feedback


def calc_fixing_time(service_code):
    return timedelta_milliseconds(get_median_duration(get_closed_by_service_code(service_code)))


# Return total number of feedbacks with either "open" or "closed" status-
def get_total_by_service(service_code):
    return Feedback.objects.filter(service_code=service_code, status__in=["open", "closed"]).count()


# return total number of feedbacks with "closed" status
def get_closed_by_service(service_code):
    return Feedback.objects.filter(service_code=service_code, status="closed").count()


def get_open_by_service(service_code):
    return Feedback.objects.filter(service_code=service_code, status="open").count()



def get_closed_by_service_code(service_code):
    return get_feedbacks(service_codes=service_code, statuses="closed")


# Returns average duration of closed feedbacks (updated_datetime - requested_datetime)
# from given category. Returns a tuple (days, hours)
def get_avg_duration(query_set):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = query_set.annotate(duration=duration).values_list("duration", flat=True)
    if not duration_list:
        return datetime.timedelta(0)
    return sum(duration_list, datetime.timedelta(0)) / len(duration_list)


# Returns median duration of closed feedbacks (updated_datetime - requested_datetime)
# from given category. Returns a tuple (days, hours)
def get_median_duration(query_set):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = sorted(query_set.annotate(duration=duration).values_list("duration", flat=True))
    if not duration_list:
        return datetime.timedelta(0)
    return duration_list[(len(duration_list) - 1) // 2]


# Concerts timedelta into millisoconds
def timedelta_milliseconds(td):
    return int(td.days * 86400000 + td.seconds * 1000 + td.microseconds / 1000)


# new departments

def get_total_by_agency(agency_responsible):
    return Feedback.objects.filter(agency_responsible=agency_responsible, status__in=["open", "closed"]).count()


# return total number of feedbacks with "closed" status
def get_closed_by_agency(agency_responsible):
    return Feedback.objects.filter(agency_responsible=agency_responsible, status="closed").count()

def get_open_by_agency(agency_responsible):
    return Feedback.objects.filter(agency_responsible=agency_responsible, status="open").count()

def get_closed_by_agency_responsible(agency_responsible):
    return Feedback.objects.filter(agency_responsible=agency_responsible, status="closed")


	# return total number of different emails
def get_emails():
    return Feedback.objects.values('email').distinct().exclude(email=None).count()

	
	