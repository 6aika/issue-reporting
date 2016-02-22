from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from formtools.wizard.views import SessionWizardView
from frontend.forms import FeedbackForm1, FeedbackForm2, FeedbackForm3
from api.models import Feedback

import urllib.request, json


FORMS = [("location", FeedbackForm1), ("category", FeedbackForm2), ("basic_info", FeedbackForm3)]
TEMPLATES = {"location": "feedback_form/step1.html", "category": "feedback_form/step2.html", "basic_info": "feedback_form/step3.html"}

def mainpage(request):
	context = {}
	fixed_feedbacks = Feedback.objects.filter(status="closed")[0:4]
	recent_feedbacks = Feedback.objects.filter(status="open")[0:4]
	context["fixed_feedbacks"] = fixed_feedbacks
	context["recent_feedbacks"]  = recent_feedbacks
	return render(request, "mainpage.html", context)

def locations_demo(request):
	feedbacks = Feedback.objects.all()
	return render(request, 'locations_demo.html', {'feedbacks': feedbacks})

def feedback_list(request):
	feedbacks = Feedback.objects.all()
	page = request.GET.get("page")
	feedbacks = paginate_query_set(feedbacks, 20, page)
	return render(request, "feedback_list.html", {"feedbacks": feedbacks})

	# Helper function. Paginates given queryset. Used for game list views.
def paginate_query_set(query_set, items_per_page, page):
	paginator = Paginator(query_set, items_per_page)
	try:
		paginate_set = paginator.page(page)
	except PageNotAnInteger:
		paginate_set = paginator.page(1)
	except EmptyPage:
		paginate_set = paginator.page(paginator.num_pages)
	return paginate_set

def map(request):
	feedbacks = Feedback.objects.all()
	return render(request, "map.html", {"feedbacks": feedbacks})


# Returns all Helsinki services as a python object
def get_services():
	url = "https://asiointi.hel.fi/palautews/rest/v1/services.json?locale=fi_FI"
	response = urllib.request.urlopen(url)
	data = json.loads(response.read().decode("utf8"))
	return data

class FeedbackWizard(SessionWizardView):
	def get_template_names(self):
		return [TEMPLATES[self.steps.current]]

	def get_context_data(self, form, **kwargs):
		context = super(FeedbackWizard, self).get_context_data(form=form, **kwargs)
		if self.steps.current == 'category':
			categories = []
			data = get_services()

			GLYPHICONS = ["glyphicon-wrench", "glyphicon-road", "glyphicon-euro", "glyphicon-music", "glyphicon-glass", "glyphicon-heart", "glyphicon-star", "glyphicon-user", "glyphicon-film", "glyphicon-home"]

			for idx, item in enumerate(data):
				category = {}
				category["name"] = item["service_name"]
				category["description"] = item["description"]
				category["src"] = "https://placehold.it/150x150"
				category["alt"] = "Category image"
				category["glyphicon"] = GLYPHICONS[idx]
				# category["code"] = item["service_code"]
				categories.append(category)

			context.update({'categories': categories})

		return context

	def done(self, form_list, **kwargs):
		return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list]})