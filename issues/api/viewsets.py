from rest_framework.viewsets import ViewSet

from issues.api.views.issues import IssueList, IssueDetail
from issues.api.views.services import ServiceList


class IssueViewSet(IssueList, IssueDetail, ViewSet):
    pass


class ServiceViewSet(ServiceList, ViewSet):
    pass
