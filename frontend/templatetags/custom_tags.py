from api.models import Service
from django import template
from django.utils import timezone
register = template.Library()


# Takes a timdelta object and returns a string indicating how many
# weeks, days, hours it is. Does not round, only truncates!
@register.filter
def td_humanize(diff):
	if(diff.total_seconds() < 0):
		return "Meni jo!"
	days = diff.days
	if(days >= 7):
		weeks, days = divmod(days, 7)
		result = str(weeks) + " vk"
		if days:
			result += " " + str(days) + " pv"
		return result
	elif(days):
		hours, remainder = divmod(diff.seconds, 3600)
		result = str(days) + " pv"
		if hours:
			result += " " + str(hours) + " h"
		return result
	else:
		hours, remainder = divmod(diff.seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		result = str(hours) + " h"
		if minutes:
			result += " " + str(minutes) + " min"
		return result

# Takes a datetime object and returns the difference between now and then
@register.filter
def time_from_now(datetime):
	now = timezone.now()
	if(datetime):
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
