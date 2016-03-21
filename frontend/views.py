import operator
import os
import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr, GEOSGeometry
from django.contrib.gis.measure import D
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView

from api.analysis import *
from api.geocoding.geocoding import reverse_geocode
from api.models import Service, MediaFile, MediaURL
from api.services import get_feedbacks, get_feedbacks_count
from frontend.forms import FeedbackFormClosest, FeedbackFormCategory, FeedbackForm3, FeedbackFormContact

FORMS = [("closest", FeedbackFormClosest), ("category", FeedbackFormCategory), ("basic_info", FeedbackForm3), ("contact", FeedbackFormContact) ]
TEMPLATES = {"closest": "feedback_form/closest.html", "category": "feedback_form/category.html",
             "basic_info": "feedback_form/step3.html", "contact": "feedback_form/contact.html"}


def mainpage(request):
    context = {}
    closed_feedbacks = Feedback.objects.filter(status="closed")
    fixed_feedbacks = Feedback.objects.filter(status="closed").order_by('-requested_datetime')[:4]
    fixed_feedbacks_count = closed_feedbacks.count()
    recent_feedbacks = Feedback.objects.filter(status="open").order_by('-requested_datetime')[:4]
    feedbacks_count = get_feedbacks_count()
    waiting_time = get_median_duration(closed_feedbacks)
    emails = get_emails()
    context["emails"] = emails
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
    filter_order_by = request.GET.get("order_by")

    if filter_start_date:
        filter_start_date = datetime.datetime.strptime(filter_start_date, "%d.%m.%Y").isoformat()

    if filter_end_date:
        filter_end_date = datetime.datetime.strptime(filter_end_date, "%d.%m.%Y").isoformat()

    if filter_order_by is None:
        filter_order_by = "-requested_datetime"

    filter_params = {
        'start_date': filter_start_date,
        'end_date': filter_end_date,
        'statuses': request.GET.get("status"),
        'order_by': filter_order_by,
        'service_codes': request.GET.get("service_code"),
        'search': request.GET.get("search"),
        'lat': request.GET.get("lat"),
        'lon': request.GET.get("lon")
    }

    feedbacks = get_feedbacks(**filter_params)

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
    context = {
        'feedbacks': Feedback.objects.all(),
        'services': Service.objects.all(),
    }
    return render(request, "map.html", context)

#different departments
def department(request):
    data = []
    agencies = Feedback.objects.all().distinct("agency_responsible")
    for agency in agencies:
        item = {}
        agency_responsible = agency.agency_responsible
        item["agency_responsible"] = agency_responsible
        item["total"] = get_total_by_agency(agency_responsible)
        item["closed"] = get_closed_by_agency(agency_responsible)
        item["open"] = get_open_by_agency(agency_responsible)
        item["avg"] = get_avg_duration(get_closed_by_agency_responsible(agency_responsible))
        item["median"] = get_median_duration(get_closed_by_agency_responsible(agency_responsible))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)

    return render(request, "department.html", {"data": data})


def statistics2(request):
    data = []
    for service in Service.objects.all():
        item = {}
        service_code = service.service_code
        item["service_code"]= service_code
        item["service_name"] = service.service_name
        item["total"] = get_total_by_service(service_code)
        item["closed"] = get_closed_by_service(service_code)
        item["open"] = get_open_by_service(service_code)
        item["avg"] = get_avg_duration(get_closed_by_service_code(service_code))
        item["median"] = get_median_duration(get_closed_by_service_code(service_code))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)
    return render(request, "statistics2.html", {"data": data})


def heatmap(request):
    return render(request, "heatmap.html", {"services": Service.objects.all()})


def charts(request):
    return render(request, "charts.html")


class FeedbackWizard(SessionWizardView):
    # Set the default category
    initial_dict = {"category": {"service_code": "180"}}
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'closest':
            print('duplicates step')
            closest = get_feedbacks(
                    statuses='Open',
                    lat=60.17067,
                    lon=24.94152,
                    radius=3000,
                    order_by='distance')[:10]
            context.update({'closest': closest})
        elif self.steps.current == 'category':
            categories = []
            data = Service.objects.all()

            GLYPHICONS = ["glyphicon-fire", "glyphicon-trash", "glyphicon-tint", "glyphicon-road",
                          "glyphicon-warning-sign",
                          "glyphicon-picture", "glyphicon-tree-conifer", "glyphicon-cloud", "glyphicon-tree-deciduous",
                          "glyphicon-option-horizontal"]

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
            context.update({'form_id': uuid.uuid4().hex})
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

        data["service_object_id"] = form_dict["closest"].cleaned_data["service_object_id"]

        form_id = form_dict["basic_info"].cleaned_data["form_id"]

        new_feedback = Feedback(**data)

        fixing_time = calc_fixing_time(data["service_code"])
        waiting_time = timedelta(milliseconds=fixing_time)
        new_feedback.expected_datetime = new_feedback.requested_datetime + waiting_time
        new_feedback.save()

        # Attach media urls to the feedback
        files = MediaFile.objects.filter(form_id=form_id)
        if(files):
            for file in files:
                # Todo: Better way to build abs image URL
                abs_url = ''.join([self.request.build_absolute_uri('/')[:-1], settings.MEDIA_URL, file.file.name])
                media_url = MediaURL(feedback=new_feedback, media_url=abs_url)
                media_url.save()
                new_feedback.media_urls.add(media_url)
                # Attach the file to feedback - not needed if using external Open311!
                new_feedback.media_files.add(file)
            # Update the single media_url field to point to the 1st image
            new_feedback.media_url = new_feedback.media_urls.all()[0].media_url
            new_feedback.save()

        return render(self.request, 'feedback_form/done.html', {'form_data': [form.cleaned_data for form in form_list],
                                                              'waiting_time': waiting_time})

# This view handles media uploads from user during submitting a new feedback
# It receives files with a form_id, saves the file and saves the info to DB so
# the files can be processed when the form wizard is actually complete in done()
def media_upload(request):
    files = request.FILES.getlist("file")
    form_id = request.POST["form_id"]
    if(files):
        # Create new unique random filename preserving extension
        file = files[0]
        extension = os.path.splitext(file.name)[1]
        file.name = uuid.uuid4().hex + extension
        f_object = MediaFile(file=file, form_id=form_id)
        f_object.save()
    else:
        # Just return the filenames associated with the form_id
        mediafiles = MediaFile.objects.filter(form_id=form_id)
        files = []
        for item in mediafiles:
            files.append(item.file.name)
        return JsonResponse({"status": "success", "files": files})
    return JsonResponse({"status": "success"})

def about(request):
    context = {}
    return render(request, "about.html", context)
