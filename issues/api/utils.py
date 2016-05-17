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


class XMLDict(dict):

    def __init__(self, dict, xml_tag=None):
        super(XMLDict, self).__init__(dict)
        self.xml_tag = xml_tag


class XMLList(list):

    def __init__(self, list, xml_tag=None):
        super(XMLList, self).__init__(list)
        self.xml_tag = xml_tag
