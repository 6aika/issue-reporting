from django.utils import timezone
from django import template

register = template.Library()


# Takes a timdelta object and returns a string indicating how many
# weeks, days, hours it is  
@register.filter
def td_humanize(diff):
	if(diff.days > 7):
		weeks, days = divmod(diff.days, 7)
		if(diff.seconds//3600 >= 12):
			days += 1
		return str(weeks) + " vk, " + str(days) + " pv"
	elif(diff.days):
		days, hours = divmod(diff.days, 24)
		return str(days) + " pv, " + str(hours) + " h"
	else:
		hours, remainder = divmod(diff.seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		return str(hours) + " h, " + str(minutes) + " min"
