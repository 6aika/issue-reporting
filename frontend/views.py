import datetime
import operator
import os
import uuid
from datetime import timedelta

from django.contrib.gis.geos import GEOSGeometry
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView

from frontend.forms import IssueFormBasicInfo, IssueFormCategory, IssueFormClosest, IssueFormContact
from issues import analysis
from issues.geocoding import reverse_geocode
from issues.models import Issue, MediaFile, Service
from issues.services import attach_files_to_issue, get_issues, get_issues_count, save_file_to_db

FORMS = [("closest", IssueFormClosest), ("category", IssueFormCategory), ("basic_info", IssueFormBasicInfo),
         ("contact", IssueFormContact)]
TEMPLATES = {"closest": "issue_form/closest.html", "category": "issue_form/category.html",
             "basic_info": "issue_form/basic_info.html", "contact": "issue_form/contact.html"}


def mainpage(request):
    context = {}
    closed_issues = Issue.objects.filter(status="closed")
    fixed_issues = Issue.objects.filter(status="closed").order_by('-requested_datetime')[:4]
    fixed_issues_count = closed_issues.count()
    recent_issues = Issue.objects.filter(status="open").order_by('-requested_datetime')[:4]
    issues_count = get_issues_count()
    waiting_time = analysis.get_median_duration(closed_issues)
    emails = analysis.get_emails()
    context["emails"] = emails
    context["waiting_time"] = waiting_time
    context["issues_count"] = issues_count
    context["fixed_issues"] = fixed_issues
    context["fixed_issues_count"] = fixed_issues_count
    context["recent_issues"] = recent_issues
    return render(request, "mainpage.html", context)


def issue_list(request):
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

    if not filter_order_by:
        filter_order_by = "-requested_datetime"
        queries_without_page["order_by"] = filter_order_by

    filter_params = {
        'start_date': filter_start_date,
        'end_date': filter_end_date,
        'statuses': request.GET.get("status"),
        'order_by': filter_order_by,
        'service_codes': request.GET.get("service_code"),
        'search': request.GET.get("search"),
        'lat': request.GET.get("lat"),
        'lon': request.GET.get("lon"),
        'agency_responsible': request.GET.get('agency_responsible')
    }

    issues = get_issues(**filter_params)

    page = request.GET.get("page")

    context = {
        'issues': paginate_query_set(issues, 20, page),
        'services': Service.objects.all(),
        'queries': queries_without_page
    }

    return render(request, "issue_list.html", context)


def issue_details(request, issue_id):
    try:
        issue = Issue.objects.get(pk=issue_id)
    except Issue.DoesNotExist:
        return render(request, "simple_message.html", {"title": "No such issue!"})
    context = {'issue': issue, 'tasks': issue.tasks.all(), 'media_urls': issue.media_urls.all()}

    return render(request, 'issue_details.html', context)


def vote_issue(request):
    """Process vote requests. Increases vote count of a issue if the session data
    does not contain the id for that issue. Ie. let the user vote only once.
    """
    if request.method == "POST":
        try:
            id = request.POST["id"]
            if id:
                issue = Issue.objects.get(pk=id)
            else:
                return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})
        except KeyError:
            return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Väärä parametri!"})
        except Issue.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Ääntä ei voitu tallentaa. Palautetta ei löydetty!"})
        else:
            if "vote_id_list" in request.session:
                if id in request.session["vote_id_list"]:
                    return JsonResponse({"status": "error", "message": "Voit äänestää palautetta vain kerran!"})
            else:
                request.session["vote_id_list"] = []
            issue.vote_counter += 1
            issue.save()
            list = request.session["vote_id_list"]
            list.append(id)
            request.session["vote_id_list"] = list
            return JsonResponse({"status": "success", "message": "Kiitos, äänesi on rekisteröity!"})
    else:
        return redirect("issue_list")


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
    issues = Issue.objects.all().distinct("agency_responsible").order_by('agency_responsible')
    agencies = [f.agency_responsible for f in issues]
    context = {
        'issues': Issue.objects.all(),
        'services': Service.objects.all(),
        'agencies': agencies,
    }
    return render(request, "map.html", context)


# different departments
def department(request):
    data = []
    agencies = Issue.objects.filter(status__in=["open", "closed"]).distinct("agency_responsible")
    for agency in agencies:
        item = {}
        agency_responsible = agency.agency_responsible
        item["agency_responsible"] = agency_responsible
        item["total"] = analysis.get_total_by_agency(agency_responsible)
        item["closed"] = analysis.get_closed_by_agency(agency_responsible)
        item["open"] = analysis.get_open_by_agency(agency_responsible)
        item["avg"] = analysis.get_avg_duration(analysis.get_closed_by_agency_responsible(agency_responsible))
        item["median"] = analysis.get_median_duration(analysis.get_closed_by_agency_responsible(agency_responsible))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)

    return render(request, "department.html", {"data": data})


def statistics(request):
    data = []
    for service in Service.objects.all():
        item = {}
        service_code = service.service_code
        item["service_code"] = service_code
        item["service_name"] = service.service_name
        item["total"] = analysis.get_total_by_service(service_code)
        item["closed"] = analysis.get_closed_by_service(service_code)
        item["open"] = analysis.get_open_by_service(service_code)
        item["avg"] = analysis.get_avg_duration(analysis.get_closed_by_service_code(service_code))
        item["median"] = analysis.get_median_duration(analysis.get_closed_by_service_code(service_code))
        data.append(item)

    # Sort the rows by "total" column
    data.sort(key=operator.itemgetter('total'), reverse=True)
    return render(request, "statistics.html", {"data": data})


def charts(request):
    return render(request, "charts.html")


class IssueWizard(SessionWizardView):
    # Set the default category
    initial_dict = {"category": {"service_code": "180"}}

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'closest':
            closest = get_issues(
                statuses='Open',
                lat=60.17067,
                lon=24.94152,
                radius=3000,
                order_by='distance')[:10]
            form_id = uuid.uuid4().hex
            context.update({'closest': closest, "form_id": form_id})
        elif self.steps.current == 'category':
            categories = []
            data = Service.objects.all()

            GLYPHICONS = ["glyphicon-fire", "glyphicon-trash", "glyphicon-tint", "glyphicon-road",
                          "glyphicon-warning-sign",
                          "glyphicon-picture", "glyphicon-tree-conifer", "glyphicon-cloud", "glyphicon-tree-deciduous",
                          "glyphicon-wrench"]

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
            prev = self.storage.get_step_data("closest")
            form_id = prev.get("closest-form_id", '')
            context.update({'form_id': form_id})
        return context

    def done(self, form_list, form_dict, **kwargs):
        data = {
            "status": "moderation",
            "title": form_dict["basic_info"].cleaned_data["title"],
            "description": form_dict["basic_info"].cleaned_data["description"],
            "service_code": form_dict["category"].cleaned_data["service_code"],
            "first_name": form_dict["contact"].cleaned_data["first_name"],
            "last_name": form_dict["contact"].cleaned_data["last_name"],
            "email": form_dict["contact"].cleaned_data["email"],
            "phone": form_dict["contact"].cleaned_data["phone"]
        }

        data["service_name"] = Service.objects.get(service_code=data["service_code"]).service_name

        latitude = form_dict["closest"].cleaned_data["latitude"]
        longitude = form_dict["closest"].cleaned_data["longitude"]
        data["location"] = GEOSGeometry('SRID=4326;POINT(' + str(longitude) + ' ' + str(latitude) + ')')
        data["address_string"] = reverse_geocode(latitude, longitude)

        service_object_id = form_dict["closest"].cleaned_data["service_object_id"]
        if service_object_id:
            data["service_object_id"] = service_object_id
            data["service_object_type"] = "http://www.hel.fi/servicemap/v2"

        form_id = form_dict["closest"].cleaned_data["form_id"]

        new_issue = Issue(**data)

        fixing_time = analysis.calc_fixing_time(data["service_code"])
        waiting_time = timedelta(milliseconds=fixing_time)
        if waiting_time.total_seconds() >= 0:
            new_issue.expected_datetime = new_issue.requested_datetime + waiting_time

        new_issue.save()

        # Attach media urls to the issue
        files = MediaFile.objects.filter(form_id=form_id)
        if files:
            attach_files_to_issue(self.request, new_issue, files)

        return render(self.request, 'issue_form/done.html', {'form_data': [form.cleaned_data for form in form_list],
                                                                'waiting_time': waiting_time})


# This view handles media uploads from user during submitting a new issue
# It receives files with a form_id, saves the file and saves the info to DB so
# the files can be processed when the form wizard is actually complete in done()
def media_upload(request):
    form_id = request.POST["form_id"]
    action = request.POST["action"]
    if action == "upload_file":
        files = request.FILES.getlist("file")
        if files:
            file_name = save_file_to_db(files[0], form_id)
            return JsonResponse({"status": "success", "filename": file_name})
        else:
            return HttpResponseBadRequest
    elif action == "get_files":
        # Just return the files (including size and original name) associated with the form_id
        mediafiles = MediaFile.objects.filter(form_id=form_id)
        files = []
        for item in mediafiles:
            entry = {
                "server_filename": (os.path.basename(item.file.name)),
                "original_filename": item.original_filename,
                "size": item.size
            }
            files.append(entry)
        return JsonResponse({"status": "success", "files": files})
    elif action == "delete_file":
        server_filename = "./" + request.POST["server_filename"]
        f_object = MediaFile.objects.filter(file=server_filename, form_id=form_id)
        if f_object:
            f_object[0].file.delete()
            f_object[0].delete()
        return JsonResponse({"status": "success"})
    else:
        return HttpResponseBadRequest


def about(request):
    context = {}
    return render(request, "about.html", context)
