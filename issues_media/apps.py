from django.apps import AppConfig

from issues_media.extension import MediaExtension


class IssuesMediaConfig(AppConfig):
    name = 'issues_media'
    issue_extension = MediaExtension
    verbose_name = 'Issues: Media Extensions'
