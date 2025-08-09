from typing import List

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Perfume
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.recommendation.serializers.ai_recommendation_serializer import (
    RecommendationCreateSerializer,
)
from apps.recommendation.utils.ai_recommendation import call_clova_model


class RecommendationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_input: str = request.data.get("text")
        if not user_input:
            return Response({"detail": "text 필드는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # Clova 호출 → 향수 ID, 키워드, description, reason 수신
        clova_response = call_clova_model(user_input)
        perfume_ids: List[int] = clova_response.get("perfume_ids", []) or []
        keywords: List[str] = clova_response.get("keywords", []) or []
        description: str = clova_response.get("description", "") or ""
        reason: str = clova_response.get("reason", "") or ""

        # 2) 향수 선택 + products 프리패치
        if perfume_ids:
            perfumes = Perfume.objects.filter(id__in=perfume_ids).prefetch_related("products")
            # ID 매칭 0건일 때 폴백
            if not perfumes.exists():
                perfumes = (
                    Perfume.objects.filter(main_accords__name__in=keywords)
                    .distinct()
                    .prefetch_related("products")
                    .order_by("?")[:5]
                )
                if not perfumes.exists():
                    perfumes = Perfume.objects.all().prefetch_related("products").order_by("?")[:5]
        else:
            perfumes = (
                Perfume.objects.filter(main_accords__name__in=keywords)
                .distinct()
                .prefetch_related("products")
                .order_by("?")[:5]
            )
            if not perfumes.exists():
                perfumes = Perfume.objects.all().prefetch_related("products").order_by("?")[:5]

        # 3) Recommendation 저장
        payload = {
            "type": Recommendation.Type.AI,
            "context": ", ".join(keywords),
            "reason": reason,
        }
        serializer = RecommendationCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        recommendation: Recommendation = serializer.save(user=request.user)

        # 4) 추천 이력 저장 (bulk)
        RecommendationHistory.objects.bulk_create(
            [RecommendationHistory(recommendation=recommendation, perfume=p) for p in perfumes]
        )

        # 5) 응답 구성
        result = []
        for p in perfumes:
            product = p.products.first()  # 정책에 따라 선택 로직 변경 가능 (ex. 재고/가장 저렴한/특정 용량)
            result.append(
                {
                    "perfume": {
                        "id": p.id,
                        "name": p.name,
                        "brand": p.brand,
                        "price": float(product.price) if product else None,
                        "image_url": product.product_img_url if product else None,
                    },
                    "context": ", ".join(keywords),
                    "created_at": recommendation.created_at.isoformat(),
                }
            )

        return Response(
            {
                "recommendation_id": recommendation.id,
                "description": description,
                "reason": reason,
                "recommendations": result,
            },
            status=status.HTTP_201_CREATED,
        )
