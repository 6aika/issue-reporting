from django.core.exceptions import ObjectDoesNotExist

from issues.api.utils import XMLList
from issues.extensions import IssueExtension


class LogExtension(IssueExtension):
    identifier = 'log'
    prefetch_name = 'log_entries'
    related_name = 'log_ext'

    def get_extended_attributes(self, issue, context=None):
        from issues_log.serializers import LogEntrySerializer
        try:
            # TODO: check if this causes an extra query when log_ext does not exist
            last_handler = issue.log_ext.last_handler
        except ObjectDoesNotExist:
            last_handler = None
        return {
            'handler': (last_handler or None),
            'log': XMLList(
                LogEntrySerializer(many=True, read_only=True).to_representation(
                    issue.log_entries.all()  # `prefetch` should have made this fairly performant
                ),
                'log'
            ),
        }

    def filter_issue_queryset(self, request, queryset, view):
        handler = request.query_params.get('handler')
        if handler:
            queryset = queryset.filter(
                log_ext__last_handler=handler
            )
        return queryset
