from django.apps import AppConfig

from issues_hel.extension import HelExtension


class HelIssuesConfig(AppConfig):
    name = 'issues_hel'
    issue_extension = HelExtension
    verbose_name = 'Issues: City of Helsinki Extensions'
