from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, render_to_response
from formtools.wizard.views import SessionWizardView

from api.models import Feedback
from frontend.forms import FeedbackForm1, FeedbackForm2, FeedbackForm3

FORMS = [("location", FeedbackForm1), ("category", FeedbackForm2), ("basic_info", FeedbackForm3)]
TEMPLATES = {"location": "feedback_form/step1.html", "category": "feedback_form/step2.html",
             "basic_info": "feedback_form/step3.html"}


def mainpage(request):
    fixed_feedbacks = Feedback.objects.all()[0:4]
    return render(request, "mainpage.html", {"fixed_feedbacks": fixed_feedbacks})


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


class FeedbackWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list]})
