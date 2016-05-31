import json
from copy import deepcopy

import requests
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.db.models.fields import DateTimeField
from django.db.transaction import atomic
from django.utils import translation

from issues.api.transforms import transform_xml_to_json
from issues.extensions import get_extensions
from issues.models import Issue
from iso8601 import parse_date


@atomic
def update_local_issue(
    gr_issue,
    id_namespace='',
    service_namespace='',
):
    """
    :param gr_issue: GeoReportv2 Issue structure (as a dict)
    :param id_namespace: String to prepend to request identifiers
    :param service_namespace: String to prepend to service codes
    :return: The created/updated Issue and a `created` flag
    """

    gr_issue = deepcopy(gr_issue)
    identifier = gr_issue.pop('service_request_id')
    if id_namespace:
        identifier = '%s:%s' % (id_namespace, identifier)
    issue = Issue.objects.filter(identifier=identifier).first()
    if not issue:
        issue = Issue(identifier=identifier)
        created = True
    else:
        created = False
    for field in Issue._meta.get_fields():
        if field.name in gr_issue:
            value = gr_issue.pop(field.name)
            if isinstance(field, DateTimeField):
                value = parse_date(value)
            setattr(issue, field.attname, value)
    if "long" in gr_issue and "lat" in gr_issue:
        issue.location = GEOSGeometry(
            'SRID=4326;POINT(%s %s)' % (gr_issue.pop('long'), gr_issue.pop('lat'))
        )
    if 'service_code' in gr_issue:
        gr_issue['service_code'] = '%s%s' % (service_namespace, gr_issue['service_code'])
    # This has no direct mapping in our schema, but it can be used by implicit autocreation of services
    issue.service_name = gr_issue.pop('service_name', None)
    issue._cache_data()
    issue.full_clean()
    issue.save()

    extended_attributes = gr_issue.pop('extended_attributes', {})
    for ex_class in get_extensions():
        ex = ex_class()
        ex.parse_extended_attributes(issue, extended_attributes)
    if gr_issue:
        print(gr_issue)
    issue.source = gr_issue
    return (issue, created)


def update_from_georeport_v2_url(
    url,
    params=None,
    id_namespace='',
):  # pragma: no cover

    if not translation.get_language():  # For interactive (shell) use: ensure a language is set
        translation.activate(settings.LANGUAGE_CODE)

    resp = requests.get(url, params)
    if 'xml' in resp.headers['Content-Type']:
        json_data = transform_xml_to_json(resp.content)
    else:
        json_data = resp.text
    issue_datas = json.loads(json_data)

    return [
        update_local_issue(issue_data, id_namespace=id_namespace)
        for issue_data
        in issue_datas
        ]
