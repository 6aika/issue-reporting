from django.apps import apps


class IssueExtension(object):
    # TODO: Document these args
    identifier = None
    related_name = None
    prefetch_name = None
    search_fields = ()

    def filter_issue_queryset(self, request, queryset, view):
        # TODO: Doc me
        return queryset

    def get_extended_attributes(self, issue, context=None):
        # TODO: Doc me
        return None

    def post_create_issue(self, request, issue):
        # TODO: Doc me
        pass

    def parse_extended_attributes(self, issue, extended_attributes):
        pass


def get_extensions():
    """
    :rtype: list[class[IssueExtension]]
    """
    for app_config in apps.get_app_configs():
        if hasattr(app_config, 'issue_extension'):
            yield app_config.issue_extension


def get_extension_ids():
    return set(ex.identifier for ex in get_extensions())


def get_extensions_from_request(request):
    """
    Get extension instances requested by the given request
    :param request: rest_framework.requests.Request
    :rtype: list[issues.extensions.IssueExtension]
    """
    if hasattr(request, '_issue_extensions'):  # Sneaky cache
        return request._issue_extensions
    extensions_param = request.query_params.get('extensions')
    if extensions_param in ('true', 'all'):
        extension_ids = get_extension_ids()
    elif extensions_param:
        extension_ids = set(extensions_param.split(','))
    else:
        extension_ids = ()
    extensions = set(ex() for ex in get_extensions() if ex.identifier in extension_ids)
    request._issue_extensions = extensions
    return extensions


def apply_select_and_prefetch(queryset, extensions):
    for extension in extensions:
        assert isinstance(extension, IssueExtension)
        if extension.related_name:
            queryset = queryset.select_related(extension.related_name)
        if extension.prefetch_name:
            queryset = queryset.prefetch_related(extension.prefetch_name)
    return queryset
