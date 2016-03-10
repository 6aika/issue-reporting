import json
import operator
import os
import urllib.request
import uuid
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr, GEOSGeometry
from django.contrib.gis.measure import D
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, render_to_response
from formtools.wizard.views import SessionWizardView
from django.db.models import Count, Avg
import datetime
from datetime import timedelta
from api.models import Feedback, Service, MediaFile
from api.services import get_feedbacks, get_feedbacks_count
from api.analysis import *
from api.geocoding.geocoding import reverse_geocode
from frontend.forms import FeedbackFormClosest, FeedbackFormCategory, FeedbackForm3, FeedbackFormContact
from django.db.models import F, ExpressionWrapper, fields

FORMS = [("closest", FeedbackFormClosest), ("category", FeedbackFormCategory), ("basic_info", FeedbackForm3), ("contact", FeedbackFormContact) ]
TEMPLATES = {"closest": "feedback_form/closest.html", "category": "feedback_form/category.html",
             "basic_info": "feedback_form/step3.html", "contact": "feedback_form/contact.html"}


def mainpage(request):
    context = {}
    fixed_feedbacks = Feedback.objects.filter(status="closed")[0:4]
    fixed_feedbacks_count = Feedback.objects.filter(status="closed").count()
    recent_feedbacks = Feedback.objects.filter(status="open")[0:4]
    feedbacks_count = get_feedbacks_count()
    #172 is dummy, to be fixed
    fixing_time = calc_fixing_time(172)
    waiting_time = timedelta(milliseconds=fixing_time)
    context["waiting_time"] = waiting_time
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
    filter_search = request.GET.get("search")
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
                              statuses=filter_status, search=filter_search,
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
            if(id):
                feedback = Feedback.objects.get(pk=id)
            else:
                return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})
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


def department(request):

    feedback_category = Feedback.objects.all().exclude(agency_responsible__exact='').exclude(
            agency_responsible__isnull=True).values('agency_responsible').annotate(total=Count('agency_responsible')).order_by('-total')



    return render(request, "department.html", {"feedbacks_category": feedback_category})

# Idea for statistic implementation.
def statistics2(request):
    data = []
    for service in Service.objects.all():
        item = {}
        service_code = service.service_code
        item["service_name"] = service.service_name
        item["total"] = get_total(service_code)
        item["closed"] = get_closed(service_code)
        item["avg"] = get_avg_duration(get_closed_by_service_code(service_code))
        item["median"] = get_median_duration(get_closed_by_service_code(service_code))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)
    return render(request, "statistics2.html", {"data": data})


def heatmap(request):
    return render(request, "heatmap.html", {"services": Service.objects.all()})


def charts(request):
    data = []
    for service in Service.objects.all():
        item = {}
        service_code = service.service_code
        item["service_name"] = service.service_name
        item["total"] = get_total(service_code)
        item["closed"] = get_closed(service_code)
        item["avg"] = get_avg_duration(get_closed_by_service_code(service_code))
        item["median"] = get_median_duration(get_closed_by_service_code(service_code))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)
    return render(request, "charts.html", {"data": data})


class FeedbackWizard(SessionWizardView):
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
                    search=None,
                    order_by='distance')[:10]
            context.update({'closest': closest})
        elif self.steps.current == 'category':
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
        elif self.steps.current == "basic_info":
            form_id = uuid.uuid4().hex
            context.update({'form_id': form_id})
        return context

    def done(self, form_list, form_dict, **kwargs):
        data = {}
        data["status"] = "moderation"
        data["title"] = form_dict["basic_info"].cleaned_data["title"]
        data["description"] = form_dict["basic_info"].cleaned_data["description"]
        data["service_code"] = form_dict["category"].cleaned_data["service_code"]
        data["service_name"] = Service.objects.get(service_code=data["service_code"]).service_name
        latitude = form_dict["closest"].cleaned_data["latitude"]
        longitude = form_dict["closest"].cleaned_data["longitude"]
        data["location"] = GEOSGeometry('SRID=4326;POINT(' + str(longitude) + ' ' + str(latitude) + ')')
        data["address_string"] = reverse_geocode(latitude, longitude)

        data["first_name"] = form_dict["contact"].cleaned_data["first_name"]
        data["last_name"] = form_dict["contact"].cleaned_data["last_name"]
        data["email"] = form_dict["contact"].cleaned_data["email"]
        data["phone"] = form_dict["contact"].cleaned_data["phone"]

        form_id = form_dict["basic_info"].cleaned_data["form_id"]

        # Attach media urls to the feedback and delete MediaFile object, leaving the file intact
        for file in MediaFile.objects.filter(form_id=form_id):
            # TODO: Add either media_url or create media_url objects, both?
            # Delete used MediaFile objects - spare the file itself
            file.delete()

        new_feedback = Feedback(**data)

        fixing_time = calc_fixing_time(data["service_code"])
        waiting_time = timedelta(milliseconds=fixing_time)
        new_feedback.expected_datetime = new_feedback.requested_datetime + waiting_time
        new_feedback.save()

        return render_to_response('feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list],
                                                              'waiting_time': waiting_time})

# This view handles media uploads from user during submitting a new feedback
# It receives files with a form_id, saves the file and saves the info to DB so
# the files can be processed when the form wizard is actually complete in done()
def media_upload(request):
    file = request.FILES.getlist("file")[0]
    form_id = request.POST["form_id"]
    if(file and form_id):
        # Create new unique random filename preserving extension
        extension = os.path.splitext(file.name)[1]
        file.name = uuid.uuid4().hex + extension
        f_object = MediaFile(file=file, form_id=form_id)
        f_object.save()
    return JsonResponse({"status": "success"});

def instructions(request):
    context = {}
    return render(request, "instructions.html", context)
