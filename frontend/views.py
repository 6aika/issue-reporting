from django.shortcuts import render

from api.models import Feedback


def locations_demo(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'locations_demo.html', {'feedbacks': feedbacks})
