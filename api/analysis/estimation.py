import datetime

from ..models import Feedback


def calc_fixing_time(service_code):
    requests = Feedback.objects.filter(service_code=service_code, status='closed').all()

    diffs = []
    for request in requests:

        if request.service_code == str(service_code):
            a = request.requested_datetime
            b = request.updated_datetime

            diff = b - a
            diffs.append(diff)

    if len(diffs) == 0:
        return 0

    total_time = sum(diffs, datetime.timedelta())
    average_time = total_time / len(diffs)
    return timedelta_milliseconds(average_time)


def timedelta_milliseconds(td):
    return int(td.days * 86400000 + td.seconds * 1000 + td.microseconds / 1000)
