from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured


class IssuesSimpleUiConfig(AppConfig):
    name = 'issues_simple_ui'
    verbose_name = 'Simple Issue UI'

    def ready(self):
        try:
            apps.get_model("issues_log.LogEntry")
        except LookupError:  # pragma: no cover
            raise ImproperlyConfigured("Using the Simple UI requires the log extension.")
