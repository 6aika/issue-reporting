from django.apps import AppConfig
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

from issues_log.extension import LogExtension


class IssueLogConfig(AppConfig):
    name = 'issues_log'
    issue_extension = LogExtension
    verbose_name = 'Issues: Log Extension'

    def cache_last_handler(self, instance, **kwargs):
        from .models import Issue_LogExtension, LogEntry
        try:
            lx = Issue_LogExtension.objects.get(issue=instance.issue)
        except ObjectDoesNotExist:
            lx = Issue_LogExtension(issue=instance.issue)
        last_log_entry = LogEntry.objects.filter(issue=instance.issue).exclude(handler="").order_by("-time").first()
        if last_log_entry.handler != lx.last_handler:
            lx.last_handler = last_log_entry.handler
            lx.save()

    def ready(self):
        post_save.connect(
            self.cache_last_handler,
            sender='issues_log.LogEntry',
            weak=False,
            dispatch_uid='issues_log.cache_last_handler',
        )
