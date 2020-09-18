from django.apps import apps


class IssueExtension:
    #: The identifier for the extension (as referred to in the `extensions` argument)
    identifier = None

    #: The `related_name` for this extension's Issue extension model. This will be added to
    #: `select_related` queries done over the API.
    related_name = None

    #: Like `related_name`, but for `prefetch_related`. (Used by the media and log extensions, for instance.)
    prefetch_name = None

    #: Additional fields to search over when the `search` query parameter is used to query
    search_fields = ()

    def filter_issue_queryset(self, request, queryset, view):  # pragma: no cover
        """
        Filter a queryset of Issues given a DRF Request and view.

        This allows extensions to hook into GET queries for requests.

        :param request: DRF request
        :type request: rest_framework.request.Request
        :param queryset: Queryset of issues
        :type queryset: QuerySet[Issue]
        :param view: The DRF view that was used for this request.
        :type view: rest_framework.views.APIView
        :return: The queryset -- even if it wasn't modified.
        :rtype: QuerySet[Issue]
        """
        return queryset

    def get_extended_attributes(self, issue, context=None):  # pragma: no cover
        """
        Get a dictionary of additional `extended_attributes` for a given issue.

        All extensions' `extended_attributes` will be merged into the issue's
        serialization output.

        :param issue: Issue
        :type issue: issues.models.Issue
        :param context: Serializer context.
        :type context: dict|None
        :return: New extended attributes (or none)
        :rtype: dict[str, object]|None
        """
        return None

    def post_create_issue(self, request, issue, data):  # pragma: no cover
        """
        Hook for after an issue is created through the API.

        The given issue has been saved already, naturally.

        :param request: The request that caused this issue to be created.
        :type request: rest_framework.request.Request
        :param issue: The issue that was created.
        :type issue: issues.models.Issue
        :param data: The data dict that was used to create the Issue
        :type data: dict
        """

    def parse_extended_attributes(self, issue, extended_attributes):  # pragma: no cover
        """
        Hook for parsing extension-specific data from an extended attributes dictionary.

        This is called by the GeoReport downloader.

        :param issue: The issue that was created.
        :type issue: issues.models.Issue
        :param extended_attributes: Extended attributes dict
        :type extended_attributes: dict[str, object]
        """

    def extend_issue_serializer(self, serializer):
        """
        Extend an issue serializer instance.

        For instance, one could add fields to `serializer.fields`.

        :param serializer: IssueSerializer
        :type serializer: issues.api.serializers.IssueSerializer
        """

    def validate_issue_data(self, serializer, data):
        """
        Extension hook to validate issue data.

        This is called by IssueSerializer.validate().

        :param serializer: IssueSerializer
        :type serializer: issues.api.serializers.IssueSerializer
        :param data: data dict
        :type data: dict
        :return: the data dict, possibly modified (or replaced wholesale?!)
        :rtype: dict
        """
        return data


def get_extensions():
    """
    :rtype: list[class[IssueExtension]]
    """
    for app_config in apps.get_app_configs():
        if hasattr(app_config, 'issue_extension'):
            yield app_config.issue_extension


def get_extension_ids():
    return {ex.identifier for ex in get_extensions()}


def get_extensions_from_request(request):
    """
    Get extension instances requested by the given request
    :param request: rest_framework.requests.Request
    :rtype: list[issues.extensions.IssueExtension]
    """
    if hasattr(request, '_issue_extensions'):  # Sneaky cache
        return request._issue_extensions
    extension_ids = _get_extension_ids_from_param(request.query_params.get('extensions'))
    if not extension_ids and request.method == 'POST':
        try:
            extension_ids = _get_extension_ids_from_param(request.data.get('extensions'))
        except (AttributeError, KeyError):
            pass

    extensions = {ex() for ex in get_extensions() if ex.identifier in extension_ids}
    request._issue_extensions = extensions
    return extensions


def _get_extension_ids_from_param(extensions_param):
    if extensions_param in ('true', 'all'):
        extension_ids = get_extension_ids()
    elif extensions_param:
        extension_ids = set(extensions_param.split(','))
    else:
        extension_ids = set()
    return extension_ids


def apply_select_and_prefetch(queryset, extensions):
    for extension in extensions:
        assert isinstance(extension, IssueExtension)
        if extension.related_name:
            queryset = queryset.select_related(extension.related_name)
        if extension.prefetch_name:
            queryset = queryset.prefetch_related(extension.prefetch_name)
    return queryset
