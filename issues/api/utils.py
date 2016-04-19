from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
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
