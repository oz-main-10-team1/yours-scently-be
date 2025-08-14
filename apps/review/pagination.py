from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "total_count": self.page.paginator.count,
                "page": self.page.number,
                "limit": self.get_page_size(self.request),
                "reviews": data,
            }
        )
