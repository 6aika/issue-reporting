from django.shortcuts import render

from api.models import Feedback


def mainpage(request):
	fixed_feedbacks = Feedback.objects.all()[0:4]
	return render(request, "mainpage.html", {"fixed_feedbacks": fixed_feedbacks})

def locations_demo(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'locations_demo.html', {'feedbacks': feedbacks})

def feedback_list(request):
	feedbacks = Feedback.objects.all()
	return render(request, "feedback_list.html", {"feedbacks": feedbacks})

def map(request):
	feedbacks = Feedback.objects.all()
	return render(request, "map.html", {"feedbacks": feedbacks})	