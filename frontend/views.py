import json
import os
import urllib.request
import urllib.request
import urllib.request

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, render_to_response
from formtools.wizard.views import SessionWizardView
from django.db.models import Count
import datetime
from api.models import Feedback
from api.views import get_feedbacks
from frontend.forms import FeedbackFormClosest, FeedbackForm2, FeedbackForm3

FORMS = [("closest", FeedbackFormClosest), ("category", FeedbackForm2), ("basic_info", FeedbackForm3)]
TEMPLATES = {"closest": "feedback_form/closest.html", "category": "feedback_form/step2.html",
             "basic_info": "feedback_form/step3.html"}


def mainpage(request):
    context = {}
    fixed_feedbacks = Feedback.objects.filter(status="closed")[0:4]
    recent_feedbacks = Feedback.objects.filter(status="open")[0:4]
    context["fixed_feedbacks"] = fixed_feedbacks
    context["recent_feedbacks"] = recent_feedbacks
    return render(request, "mainpage.html", context)


def locations_demo(request):
    point = fromstr('SRID=4326;POINT(%s %s)' % (24.821711, 60.186896))
    feedbacks = Feedback.objects.annotate(distance=Distance('location', point)) \
        .filter(location__distance_lte=(point, D(m=3000))).order_by('distance')
    return render(request, 'locations_demo.html', {'feedbacks': feedbacks})


def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by("-requested_datetime")
    page = request.GET.get("page")
    feedbacks = paginate_query_set(feedbacks, 20, page)
    return render(request, "feedback_list.html", {"feedbacks": feedbacks})


def vote_feedback(request):
    if request.method == "POST":
        try:
            id = request.POST["id"]
            feedback = Feedback.objects.get(service_request_id=id)
        except KeyError:
            return JsonResponse({'status': 'No id parameter!'})
        except Feedback.DoesNotExist:
            return JsonResponse({'status': 'No such feedback!'})
        else:
            feedback.vote_counter += 1
            feedback.save()
            return JsonResponse({'status': 'success'})
    else:
        return redirect("feedback_list")


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
##############################################

def statistic_page(request):

    feedback_category = Feedback.objects.exclude(service_name__exact='').exclude(service_name__isnull=True).values('service_name').annotate(total=Count('service_name')).order_by('-total')
    closed = Feedback.objects.filter(status='closed').exclude(service_name__exact='').exclude(service_name__isnull=True).values('service_name').annotate(total=Count('service_name')).order_by('-total')


    zipped = zip(feedback_category,closed)
    return render(request, "statistic_page.html",{'feedback':zipped})
#####################################################

class FeedbackWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(FeedbackWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'closest':
            print('duplicates step')
            closest = get_feedbacks(
                    service_request_ids=None,
                    service_codes=None,
                    start_date=None,
                    end_date=None,
                    statuses='Open',
                    service_object_type=None,
                    service_object_id=None,
                    lat=60.17067,
                    lon=24.94152,
                    radius=3000,
                    updated_after=None,
                    updated_before=None,
                    description=None,
                    order_by='distance')[:10]

            context.update({'closest': closest})

        if self.steps.current == 'category':
            categories = []
            data = get_services()

            GLYPHICONS = ["glyphicon-wrench", "glyphicon-road", "glyphicon-euro", "glyphicon-music", "glyphicon-glass",
                          "glyphicon-heart", "glyphicon-star", "glyphicon-user", "glyphicon-film", "glyphicon-home"]

            for idx, item in enumerate(data):
                category = {}
                category["name"] = item["service_name"]
                category["description"] = item["description"]
                category["src"] = "https://placehold.it/150x150"
                category["alt"] = "Category image"
                category["glyphicon"] = GLYPHICONS[idx]
                category["service_code"] = item["service_code"]
                categories.append(category)
                context.update({'categories': categories})
        return context

    def done(self, form_list, form_dict, **kwargs):
        handle_uploaded_file(form_dict["basic_info"].cleaned_data["image"])
        return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list]})

def instructions(request):
    context = {}
    return render(request, "instructions.html", context)

def handle_uploaded_file(file):
    if file:
        with open(os.path.join(settings.MEDIA_ROOT,file.name), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
