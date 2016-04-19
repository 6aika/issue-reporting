from datetime import timedelta

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils import timezone

from issues.analysis import calc_fixing_time
from issues.models import Service

register = template.Library()


# Takes a timdelta object and returns a string indicating how many
# weeks, days, hours it is. Does not round, only truncates!
@register.filter
def td_humanize(diff):
    if diff.total_seconds() < 0:
        return "Meni jo!"
    days = diff.days
    if days >= 7:
        weeks, days = divmod(days, 7)
        result = str(weeks) + " vk"
        if days:
            result += " " + str(days) + " pv"
        return result
    elif days:
        hours, remainder = divmod(diff.seconds, 3600)
        result = str(days) + " pv"
        if hours:
            result += " " + str(hours) + " h"
        return result
    else:
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if minutes >= 30:
            hours += 1
        result = str(hours) + " h"
        return result


# Takes a datetime object and returns the difference between now and then
@register.filter
def time_from_now(datetime):
    now = timezone.now()
    if datetime != "Ei tiedossa":
        return td_humanize(datetime - now)
    else:
        return "Ei tiedossa"


# Check if the given service code is among supported service codes. If it is, return the same code.
# If not, return code "180".
@register.filter
def parse_service_code(service_code):
    if Service.objects.filter(service_code=service_code).exists():
        return service_code
    else:
        return "180"


# Returns the service name based on given service code. This is done because somtimes
# service_name is in the wrong language
@register.filter
def get_service_name(service_code):
    try:
        service = Service.objects.get(service_code=service_code)
    except ObjectDoesNotExist:
        return "Muu"
    return service.service_name


# Check if the feedback really is open or not. Return true if:
# 	- status == open/moderation
#	- detailed_status contains specified substrings
# If ALLOW_HELSINKI_SPECIFIC_FEATURES == False just return basic status
@register.filter
def is_open(feedback):
    if settings.ALLOW_HELSINKI_SPECIFIC_FEATURES:
        open_strings = ["PUBLIC_WORKS_NEW", "PUBLIC_WORKS_COMPLETED_SCHEDULED_LATER"]
        if feedback.status in ["open", "moderation"]:
            return True
        else:
            for string in open_strings:
                if string in feedback.detailed_status:
                    return True
            return False
    else:
        return (feedback.status in ["open", "moderation"])


# Returns the real status string of the feedback
@register.filter
def real_status(feedback):
    if is_open(feedback):
        return "Avoin"
    else:
        return "Suljettu"


# If the expected_datetime is empty, return median estimation
@register.filter
def get_expected_datetime(feedback):
    if feedback.expected_datetime:
        return feedback.expected_datetime
    else:
        time = calc_fixing_time(feedback.service_code)
        if time > 0:
            median = timedelta(milliseconds=time)
            return (feedback.requested_datetime + median)
        else:
            return "Ei tiedossa"


# Highlights the active navbar link
@register.simple_tag
def navbar_link_class(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return "active"
    return ""


# Checks if the user has already voted this feedback and returns a proper class. Uses session data.
@register.simple_tag
def feedback_vote_icon_status(request, item):
    if "vote_id_list" in request.session:
        if str(item.id) in request.session["vote_id_list"]:
            return "icon_disabled"
    return "icon_enabled"
