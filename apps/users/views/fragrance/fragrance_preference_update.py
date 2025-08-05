from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FragrancePreference
from apps.users.serializers.fragrance.fragrance_preference_update import (
    FragrancePreferenceUpdateSerializer,
)


class FragrancePreferenceUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        try:
            # 향 노트 관련 필드를 미리 불러와 N+1 문제를 방지
            preference = FragrancePreference.objects.prefetch_related(
                "preferred_top_notes", "preferred_middle_notes", "preferred_base_notes"
            ).get(user=user)

        except FragrancePreference.DoesNotExist:
            return Response(
                {"detail": "사용자의 취향 정보가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # PATCH 데이터 적용
        serializer = FragrancePreferenceUpdateSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
