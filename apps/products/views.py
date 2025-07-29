from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Perfume
from .serializers import PerfumeSerializer


class PerfumeListView(APIView):
    def get(self, request, *args, **kwargs):
        last_id = request.query_params.get('last_id')
        limit = request.query_params.get('limit', 10)
        brand = request.query_params.get('brand')
        search_keyword = request.query_params.get('search')
        gender = request.query_params.get('gender')

        try:
            limit = int(limit)
            if limit <= 0:
                return Response({"detail": "limit은 양의 정수여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "limit이 올바른 정수 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        perfumes = Perfume.objects.all()

        if last_id:
            try:
                last_id = int(last_id)
                perfumes = perfumes.filter(id__lt=last_id)
            except ValueError:
                return Response({"detail": "last_id가 올바른 정수 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        if brand:
            perfumes = perfumes.filter(brand__icontains=brand)

        if search_keyword:
            perfumes = perfumes.filter(
                Q(name__icontains=search_keyword) | Q(brand__icontains=search_keyword)
            )
        if gender:
            valid_genders = ['Men', 'Women', 'unisex']
            if gender not in valid_genders:
                return Response(
                    {"detail": "올바르지 않은 성별입니다.(예: 'Men', 'Women', 'unisex')"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            perfumes = perfumes.filter(gender=gender)

        # 요청된 limit보다 1개 더 조회하여 다음 페이지 유무 확인
        perfumes = perfumes[:limit + 1]

        has_more = len(perfumes) > limit
        if has_more:
            next_last_id = perfumes[limit - 1].id
            perfumes = perfumes[:limit]
        else:
            next_last_id = None

        serializer = PerfumeSerializer(perfumes, many=True)
        return Response({
            "perfumes": serializer.data,
            "next_last_id": next_last_id,
            "has_more": has_more
        }, status=status.HTTP_200_OK)
