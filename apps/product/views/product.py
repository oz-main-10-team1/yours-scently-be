# products/views.py

from rest_framework import generics, pagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

# --- 필수: 여기에 Product 모델과 ProductSerializer를 임포트하세요. ---
# 예시:
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
# ------------------------------------------------------------------

class CustomPagination(pagination.PageNumberPagination):

    # 한 페이지당 보여줄 항목 수
    page_size = 10
    # 클라이언트가 페이지당 항목 수
    page_size_query_param = 'page_size'
    # 클라이언트가 요청할 수 있는 최대 page_size
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        페이지네이션된 응답 형식을 정의합니다.
        """
        return Response({
            'next': self.get_next_link(),     # 다음 페이지의 URL
            'previous': self.get_previous_link(), # 이전 페이지의 URL
            'count': self.page.paginator.count,   # 전체 항목의 수
            'results': data                   # 현재 페이지의 실제 데이터
        })

class ProductListView(generics.ListAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        클라이언트의 'order_by' 쿼리 파라미터에 따라 쿼리셋을 필터링하고 정렬합니다.
        """
        queryset = super().get_queryset()

        # 'order_by' 쿼리 파라미터 값을 가져오고, 없으면 'latest'를 기본값으로 설정
        order_by = self.request.query_params.get('order_by', 'latest')

        # 각 정렬 기준에 따라 쿼리셋 정렬
        if order_by == 'latest':
            # 최신순: 'created_at' 필드를 내림차순으로 정렬
            queryset = queryset.order_by('-created_at')
        elif order_by == 'popular':
            # 인기순: 'views' 필드를 내림차순으로 정렬 (모델에 'views' 필드가 있어야 함)
            # 'views' 대신 실제 인기 기준 필드(예: sales_count, likes 등)를 사용하세요.
            queryset = queryset.order_by('-views')
        elif order_by == 'price_high':
            # 가격 높은 순: 'price' 필드를 내림차순으로 정렬
            queryset = queryset.order_by('-price')
        elif order_by == 'price_low':
            # 가격 낮은 순: 'price' 필드를 오름차순으로 정렬
            queryset = queryset.order_by('price')
        else:
            # 유효하지 않은 'order_by' 값이 들어오면 ValidationError 발생
            raise ValidationError(detail="유효하지 않은 'order_by' 파라미터입니다. 'latest', 'popular', 'price_high', 'price_low' 중 하나여야 합니다.")

        return queryset