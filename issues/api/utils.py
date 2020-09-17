import json
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.utils.encoders import JSONEncoder

from issues.excs import InvalidAppError


def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data = {
            'code': response.status_code,
            'detail': response.reason_phrase
        }
        if hasattr(exc, 'detail'):
            response.data['detail'] = exc.detail

    return response


class XMLDict(OrderedDict):
    def __init__(self, dict, xml_tag=None):
        super().__init__(dict)
        self.xml_tag = xml_tag


class XMLList(list):
    def __init__(self, list, xml_tag=None):
        super().__init__(list)
        self.xml_tag = xml_tag


class IWriteXML:
    def write_xml(self, xml):
        """
        Write this object to the given XMLGenerator.
        :type xml: xml.sax.saxutils.XMLGenerator
        """
        raise NotImplementedError("...")


class JSONInXML(IWriteXML, dict):
    """
    When rendering XML, write this object as JSON.

    This is meant for GeoJSON serialization, which should be "native"
    JSON when rendering JSON, and a string (instead of a horribly mangled
    XML representation) when rendering XML.
    """

    def write_xml(self, xml):
        xml.characters(json.dumps(self, cls=JSONEncoder))


def get_application_from_api_key(api_key):
    from issues.models import Application
    if api_key:
        try:
            app = Application.objects.get(key=api_key)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Invalid API key')
        if not app.active:
            raise serializers.ValidationError('The %s application is not active' % app)
    else:
        try:
            app = Application.autodetermine()
        except InvalidAppError as iae:
            raise serializers.ValidationError(iae.args[0])
    return app


def get_application_from_request(request):
    for value in (
        request.query_params.get('api_key'),
        (request.data.get('api_key') if request.method == 'POST' else None),
    ):
        if value is not None:
            return get_application_from_api_key(value)
