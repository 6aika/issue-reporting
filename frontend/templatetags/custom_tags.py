from django import template
from django.utils import timezone
register = template.Library()


# Takes a timdelta object and returns a string indicating how many
# weeks, days, hours it is  
# TODO: Handle negative values
@register.filter
def td_humanize(diff):
	if(diff.total_seconds() < 0):
		return "Meni jo!"
	if(diff.days >= 7):
		weeks, days = divmod(diff.days, 7)
		if(diff.seconds//3600 >= 12):
			days += 1
		return str(weeks) + "vk  " + str(days) + "pv"
	elif(diff.days):
		hours, remainder = divmod(diff.seconds, 3600)
		if(remainder >= 1800):
			hours += 1
		return str(diff.days) + "pv  " + str(hours) + "h"
	else:
		hours, remainder = divmod(diff.seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		return str(hours) + " h, " + str(minutes) + " min"

# Takes a datetime object and returns the difference between now and then
@register.filter
def time_from_now(datetime):
	now = timezone.now()
	return td_humanize(datetime - now)

