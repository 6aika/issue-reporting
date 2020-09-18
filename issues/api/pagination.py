from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.response import Response
from rest_framework.settings import api_settings


class GeoReportV2Pagination(PageNumberPagination):
    max_page_size = getattr(api_settings, 'MAX_PAGE_SIZE', 500)
    page_size_query_params = ('per_page', 'page_size')

    def get_paginated_response(self, data):
        return Response(
            data,
            headers={
                key: value
                for (key, value) in {
                    'X-Next-Page-URL': self.get_next_link(),
                    'X-Page-Count': self.page.paginator.num_pages,
                    'X-Page-Size': self.page.paginator.per_page,
                    'X-Previous-Page-URL': self.get_previous_link(),
                    'X-Result-Count': self.page.paginator.count,
                }.items()
                if (key and value)
            })

    def get_page_size(self, request):
        for param in self.page_size_query_params:
            try:
                return _positive_int(
                    request.query_params[param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size
