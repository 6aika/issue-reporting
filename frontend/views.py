import json
import operator
import os
import urllib.request
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr, GEOSGeometry
from django.contrib.gis.measure import D
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, render_to_response
from formtools.wizard.views import SessionWizardView
from django.db.models import Count, Avg, Sum
import datetime
from datetime import timedelta
from api.models import Feedback, Service
from api.services import get_feedbacks
from api.analysis import calc_fixing_time
from api.geocoding.geocoding import reverse_geocode
from frontend.forms import FeedbackFormClosest, FeedbackForm2, FeedbackForm3
from django.db.models import F, ExpressionWrapper, fields

FORMS = [("closest", FeedbackFormClosest), ("category", FeedbackForm2), ("basic_info", FeedbackForm3)]
TEMPLATES = {"closest": "feedback_form/closest.html", "category": "feedback_form/step2.html",
             "basic_info": "feedback_form/step3.html"}


def mainpage(request):
    context = {}
    fixed_feedbacks = Feedback.objects.filter(status="closed")[0:4]
    fixed_feedbacks_count = Feedback.objects.filter(status="closed").count()
    recent_feedbacks = Feedback.objects.filter(status="open")[0:4]
    feedbacks_count = Feedback.objects.count()
    context["feedbacks_count"] = feedbacks_count
    context["fixed_feedbacks"] = fixed_feedbacks
    context["fixed_feedbacks_count"] = fixed_feedbacks_count
    context["recent_feedbacks"] = recent_feedbacks
    return render(request, "mainpage.html", context)


def locations_demo(request):
    point = fromstr('SRID=4326;POINT(%s %s)' % (24.821711, 60.186896))
    feedbacks = Feedback.objects.annotate(distance=Distance('location', point)) \
        .filter(location__distance_lte=(point, D(m=3000))).order_by('distance')
    return render(request, 'locations_demo.html', {'feedbacks': feedbacks})


def feedback_list(request):
    queries_without_page = request.GET.copy()
    if 'page' in queries_without_page:
        del queries_without_page['page']

    filter_start_date = request.GET.get("start_date")
    filter_end_date = request.GET.get("end_date")
    filter_status = request.GET.get("status")
    filter_order_by = request.GET.get("order_by")
    filter_service_code = request.GET.get("service_code")
    filter_description = request.GET.get("description")
    filter_lat = request.GET.get("lat")
    filter_lon = request.GET.get("lon")

    if filter_start_date:
        filter_start_date = datetime.datetime.strptime(filter_start_date, "%d.%m.%Y").isoformat()

    if filter_end_date:
        filter_end_date = datetime.datetime.strptime(filter_end_date, "%d.%m.%Y").isoformat()

    if filter_order_by is None:
        filter_order_by = "-requested_datetime"

    feedbacks = get_feedbacks(service_codes=filter_service_code, service_request_ids=None,
                              start_date=filter_start_date, end_date=filter_end_date,
                              statuses=filter_status, description=filter_description,
                              service_object_type=None, service_object_id=None,
                              updated_after=None, updated_before=None,
                              lat=filter_lat, lon=filter_lon, radius=None, order_by=filter_order_by)

    page = request.GET.get("page")

    context = {
        'feedbacks': paginate_query_set(feedbacks, 20, page),
        'services': Service.objects.all(),
        'queries': queries_without_page
    }

    return render(request, "feedback_list.html", context)


def feedback_details(request, feedback_id):
    try:
        feedback = Feedback.objects.get(pk=feedback_id)
    except Feedback.DoesNotExist:
        return render(request, "simple_message.html", {"title": "No such feedback!"})
    context = {'feedback': feedback, 'tasks': feedback.tasks.all(), 'media_urls': feedback.media_urls.all()}

    return render(request, 'feedback_details.html', context)


def vote_feedback(request):
    """Process vote requests. Increases vote count of a feedback if the session data
    does not contain the id for that feedback. Ie. let the user vote only once.
    """
    if request.method == "POST":
        try:
            id = request.POST["id"]
            feedback = Feedback.objects.get(pk=id)
        except KeyError:
            return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Väärä parametri!"})
        except Feedback.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})
        else:
            if "vote_id_list" in request.session:
                if id in request.session["vote_id_list"]:
                    return JsonResponse({"status": "error", "message": "Voit äänestää palautetta vain kerran!"})
            else:
                request.session["vote_id_list"] = []
            feedback.vote_counter += 1
            feedback.save()
            list = request.session["vote_id_list"]
            list.append(id)
            request.session["vote_id_list"] = list
            return JsonResponse({"status": "success", "message": "Kiitos, äänesi on rekisteröity!"})
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


def statistic_page(request):
    context = {}
    duration = ExpressionWrapper(Avg((F('updated_datetime') - F('requested_datetime'))),
                                 output_field=fields.DurationField())
    feedback_category = Feedback.objects.all().exclude(service_name__exact='').exclude(
            service_name__isnull=True).values('service_name').annotate(total=Count('service_name')).order_by('-total')
    closed = Feedback.objects.filter(status='closed').exclude(service_name__exact='').exclude(
            service_name__isnull=True).values('service_name').annotate(total=Count('service_name')).annotate(
            duration=duration).order_by('-total')

    context["feedback_category"] = feedback_category
    context["closed"] = closed
    return render(request, "statistic_page.html", context)

# Idea for statistic implementation.
def statistics2(request):
    data = []
    for service in Service.objects.all():
        item = {}
        service_code = service.service_code
        item["service_name"] = service.service_name
        item["total"] = get_total(service_code)
        item["closed"] = get_closed(service_code)
        item["avg"] = get_avg_duration(service_code)
        item["median"] = get_avg_median(service_code)
        data.append(item)

    data.sort(key=operator.itemgetter('total'), reverse=True)
    return render(request, "statistics2.html", {"data": data})

def get_total(service_code):
    return Feedback.objects.filter(service_code=service_code).count()

def get_closed(service_code):
    return Feedback.objects.filter(service_code=service_code, status="closed").count()

def get_avg_duration(service_code):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = Feedback.objects.filter(service_code=service_code, status="closed").annotate(duration=duration).values_list("duration", flat=True)
    average_timedelta = sum(duration_list, datetime.timedelta(0)) / len(duration_list)
    return (average_timedelta.days, average_timedelta.seconds//3600)

def get_avg_median(service_code):
    duration = ExpressionWrapper(F('updated_datetime') - F('requested_datetime'), output_field=fields.DurationField())
    duration_list = sorted(Feedback.objects.filter(service_code=service_code, status="closed").annotate(duration=duration).values_list("duration", flat=True))
    median_duration = duration_list[(len(duration_list)-1)//2]
    return (median_duration.days, median_duration.seconds//3600)


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
            data = Service.objects.all()

            GLYPHICONS = ["glyphicon-wrench", "glyphicon-road", "glyphicon-euro", "glyphicon-music", "glyphicon-glass",
                          "glyphicon-heart", "glyphicon-star", "glyphicon-user", "glyphicon-film", "glyphicon-home"]

            idx = 0
            for item in data:
                category = {}
                category["name"] = item.service_name
                category["description"] = item.description
                category["src"] = "https://placehold.it/150x150"
                category["alt"] = "Category image"
                category["glyphicon"] = GLYPHICONS[idx]
                category["service_code"] = item.service_code
                categories.append(category)
                context.update({'categories': categories})
                idx += 1
        return context

    def done(self, form_list, form_dict, **kwargs):
        data = {}
        data["status"] = "open"
        data["title"] = form_dict["basic_info"].cleaned_data["title"]
        data["description"] = form_dict["basic_info"].cleaned_data["description"]
        data["service_code"] = form_dict["category"].cleaned_data["service_code"]
        data["service_name"] = Service.objects.get(service_code=data["service_code"]).service_name
        latitude = form_dict["closest"].cleaned_data["latitude"]
        longitude = form_dict["closest"].cleaned_data["longitude"]
        data["location"] = GEOSGeometry('SRID=4326;POINT(' + str(longitude) + ' ' + str(latitude) + ')')
        data["address_string"] = reverse_geocode(latitude, longitude)
        image = form_dict["basic_info"].cleaned_data["image"]

        if image:
            handle_uploaded_file(image)
            data["media_url"] = "/media/" + image.name

        new_feedback = Feedback(**data)
        new_feedback.save()

        fixing_time = calc_fixing_time(data["service_code"])
        expected_datetime = new_feedback.requested_datetime + timedelta(milliseconds=fixing_time)
        new_feedback.expected_datetime = expected_datetime
        new_feedback.save()

        return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list],
                                                              'expected_datetime': expected_datetime})


def instructions(request):
    context = {}
    return render(request, "instructions.html", context)


# Now only saves the submitted file into MEDIA_ROOT directory
def handle_uploaded_file(file):
    with open(os.path.join(settings.MEDIA_ROOT, file.name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
