from django.shortcuts import render, render_to_response
from formtools.wizard.views import SessionWizardView
from frontend.forms import FeedbackForm1, FeedbackForm2, FeedbackForm3
from api.models import Feedback

FORMS = [("location", FeedbackForm1), ("category", FeedbackForm2), ("basic_info", FeedbackForm3)]
TEMPLATES = {"location": "feedback_form/step1.html", "category": "feedback_form/step2.html", "basic_info": "feedback_form/step3.html"}

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

class FeedbackWizard(SessionWizardView):
	def get_template_names(self):
		return [TEMPLATES[self.steps.current]]

	def done(self, form_list, **kwargs):
		return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list]})