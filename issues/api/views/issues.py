from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from issues.api.serializers import IssueDetailSerializer, IssueSerializer
from issues.models import MediaFile
from issues.services import attach_files_to_issue, get_issues, save_file_to_db


class RequestBaseAPIView(APIView):
    item_tag_name = 'request'
    root_tag_name = 'requests'


class IssueList(RequestBaseAPIView):
    def get(self, request, format=None):
        service_object_id = request.query_params.get('service_object_id', None)
        service_object_type = request.query_params.get('service_object_type', None)

        if service_object_id is not None and service_object_type is None:
            raise ValidationError(
                "If service_object_id is included in the request, then service_object_type must be included.")

        queryset = get_issues(
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

        serializer = IssueSerializer(queryset, many=True,
                                     context={'extensions': request.query_params.get('extensions', 'false')})
        return Response(serializer.data)

    def post(self, request, format=None):
        # TODO: (for future releases) add API key rules
        serializer = IssueDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_issue = serializer.save()

            # save files in the same manner as it's done in issue form
            if request.FILES:
                for filename, file in request.FILES.items():
                    save_file_to_db(file, new_issue.service_request_id)
                files = MediaFile.objects.filter(form_id=new_issue.service_request_id)
                if files:
                    attach_files_to_issue(request, new_issue, files)

            response_data = {
                'service_request_id': new_issue.service_request_id,
                'service_notice': ''
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDetail(RequestBaseAPIView):
    def get(self, request, service_request_id, format=None):
        queryset = get_issues(
            service_request_ids=service_request_id,
            service_codes=request.query_params.get('service_code', None),
            start_date=request.query_params.get('start_date', None),
            end_date=request.query_params.get('end_date', None),
            statuses=request.query_params.get('status', None),
            lat=request.query_params.get('lat', None),
            lon=request.query_params.get('long', None),
            radius=request.query_params.get('radius', None),
            updated_after=request.query_params.get('updated_after', None),
            updated_before=request.query_params.get('updated_before', None),
            search=request.query_params.get('search', None),
            order_by=request.query_params.get('order_by', None)
        )

        serializer = IssueSerializer(queryset, many=True,
                                     context={'extensions': request.query_params.get('extensions', 'false')})
        return Response(serializer.data)
