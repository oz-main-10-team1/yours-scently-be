from typing import Dict

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FragrancePreference
from apps.users.serializers.fragrance.fragrance_preference import (
    FragrancePreferenceSerializer,
)


class FragrancePreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    # POST: 향기 취향 생성
    @extend_schema(
        request=FragrancePreferenceSerializer,
        responses=FragrancePreferenceSerializer,
        tags=["fragrance-preference"],
        summary="사용자 취향 등록",
    )
    def post(self, request):
        if hasattr(request.user, "fragrance_preference"):
            return Response({"detail": "이미 등록된 향기 취향이 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FragrancePreferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH: 향기 취향 수정
    @extend_schema(
        request=FragrancePreferenceSerializer,
        responses=FragrancePreferenceSerializer,
        tags=["fragrance-preference"],
        summary="사용자 취향 수정",
    )
    def patch(self, request):
        user = request.user
        try:
            preference = FragrancePreference.objects.prefetch_related(
                "preferred_top_notes", "preferred_middle_notes", "preferred_base_notes"
            ).get(user=user)
        except FragrancePreference.DoesNotExist:
            return Response({"detail": "사용자의 취향 정보가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FragrancePreferenceSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE: 향기 취향 삭제
    @extend_schema(
        request=None,
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["fragrance-preference"],
        summary="사용자 취향 삭제",
    )
    def delete(self, request):
        user = request.user
        try:
            preference = FragrancePreference.objects.get(user=user)
        except FragrancePreference.DoesNotExist:
            return Response({"detail": "사용자의 취향 정보가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        preference.delete()
        return Response({"message": "사용자 향기 취향이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
