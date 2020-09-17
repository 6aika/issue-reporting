import operator

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status

from issues import analysis
from issues.models import Issue, Service


def get_service_statistics(request, service_code):
    try:
        service = Service.objects.get(service_code=service_code)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'unknown service code'},
                            status=status.HTTP_404_NOT_FOUND)

    statistics = get_service_item_statistics(service)
    return JsonResponse(statistics)


def get_services_statistics(request):
    service_statistics = []
    for service in Service.objects.all():
        item = get_service_item_statistics(service)
        service_statistics.append(item)

    # Sort the rows by "total" column
    service_statistics.sort(key=operator.itemgetter('total'), reverse=True)

    return JsonResponse(service_statistics, safe=False)


def get_service_item_statistics(service):
    item = {}
    service_code = service.service_code

    avg = analysis.get_avg_duration(analysis.get_closed_by_service_code(service_code))
    median = analysis.get_median_duration(analysis.get_closed_by_service_code(service_code))

    item["service_code"] = service.service_code
    item["service_name"] = service.service_name
    item["total"] = analysis.get_total_by_service(service_code)
    item["closed"] = analysis.get_closed_by_service(service_code)
    item["avg_sec"] = int(avg.total_seconds())
    item["median_sec"] = int(median.total_seconds())

    return item


def get_agency_item_statistics(agency_responsible):
    item = {}

    avg = analysis.get_avg_duration(analysis.get_closed_by_agency_responsible(agency_responsible))
    median = analysis.get_median_duration(analysis.get_closed_by_agency_responsible(agency_responsible))

    item["agency_responsible"] = agency_responsible
    item["total"] = analysis.get_total_by_agency(agency_responsible)
    item["closed"] = analysis.get_closed_by_agency(agency_responsible)
    item["avg_sec"] = int(avg.total_seconds())
    item["median_sec"] = int(median.total_seconds())

    return item


def get_agency_statistics(request, agency):
    issues_with_agency = Issue.objects.filter(agency_responsible__iexact=agency).count()

    if issues_with_agency == 0:
        return JsonResponse({'status': 'error', 'message': 'unknown agency name'},
                            status=status.HTTP_404_NOT_FOUND)

    statistics = get_agency_item_statistics(agency)
    return JsonResponse(statistics)


def get_agencies_statistics(request):
    agency_statistics = []
    agencies = Issue.objects.all().distinct("agency_responsible")
    for agency in agencies:
        item = get_agency_item_statistics(agency.agency_responsible)
        agency_statistics.append(item)

    # Sort the rows by "total" column
    agency_statistics.sort(key=operator.itemgetter('total'), reverse=True)

    return JsonResponse(agency_statistics, safe=False)


def get_agency_responsible_list(request):
    issues = Issue.objects.all().distinct("agency_responsible").order_by('agency_responsible')
    agencies = [f.agency_responsible for f in issues]
    return JsonResponse(agencies, safe=False)
