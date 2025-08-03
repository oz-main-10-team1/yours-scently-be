from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FragrancePreference
from apps.users.serializers.fragrance.fragrance_preference import (
    FragrancePreferenceSerializer,
)


class FragrancePreferenceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.id != user_id:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(request.user, "fragrance_preference"):
            return Response({"detail": "이미 등록된 향기 취향이 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FragrancePreferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
