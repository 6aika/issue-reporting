from django.apps import AppConfig

from issues_citysdk.extension import CitySDKExtension


class IssuesCitySDKConfig(AppConfig):
    name = 'issues_citysdk'
    issue_extension = CitySDKExtension
    verbose_name = 'Issues: CitySDK Extensions'
