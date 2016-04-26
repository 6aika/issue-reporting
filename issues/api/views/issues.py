from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView

from issues.api.serializers import IssueDetailSerializer, IssueSerializer
from issues.models import MediaFile, Issue
from issues.services import attach_files_to_issue, get_issues, save_file_to_db


class IssueViewBase(GenericAPIView):
    item_tag_name = 'request'
    root_tag_name = 'requests'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['extensions'] = bool(self.request.query_params.get('extensions') == 'true')
        return ctx


class IssueList(IssueViewBase, ListCreateAPIView):
    def get_queryset(self):
        request = self.request
        service_object_id = request.query_params.get('service_object_id', None)
        service_object_type = request.query_params.get('service_object_type', None)

        if service_object_id is not None and service_object_type is None:
            raise ValidationError(
                "If service_object_id is included in the request, then service_object_type must be included.")

        return get_issues(
            service_request_ids=request.query_params.get('service_request_id', None),
            service_codes=request.query_params.get('service_code', None),
            start_date=request.query_params.get('start_date', None),
            end_date=request.query_params.get('end_date', None),
            statuses=request.query_params.get('status', None),
            service_object_type=service_object_type,
            service_object_id=service_object_id,
            lat=request.query_params.get('lat', None),
            lon=request.query_params.get('long', None),
            radius=request.query_params.get('radius', None),
            updated_after=request.query_params.get('updated_after', None),
            updated_before=request.query_params.get('updated_before', None),
            search=request.query_params.get('search', None),
            agency_responsible=request.query_params.get('agency_responsible', None),
            order_by=request.query_params.get('order_by', None),
            use_limit=True
        )

    def get_serializer(self, *args, **kwargs):
        if kwargs.get("data"):
            serializer_class = IssueDetailSerializer
        else:
            serializer_class = IssueSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        request = self.request
        new_issue = serializer.save()
        # save files in the same manner as it's done in issue form
        if request.FILES:
            for filename, file in request.FILES.items():
                save_file_to_db(file, new_issue.service_request_id)
            files = MediaFile.objects.filter(form_id=new_issue.service_request_id)
            if files:
                attach_files_to_issue(request, new_issue, files)
                # response_data = {
                #    'service_request_id': new_issue.service_request_id,
                #    'service_notice': ''
                # }
                # return Response(response_data, status=status.HTTP_201_CREATED)


class IssueDetail(RetrieveAPIView):
    lookup_url_kwarg = "service_request_id"
    serializer_class = IssueDetailSerializer

    def get_queryset(self):
        return Issue.objects.all()
