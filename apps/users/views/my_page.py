from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.user import User
from apps.users.serializers.my_page import MyPageSerializer, MyPageUpdateSerializer


class MyPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.prefetch_related("perfumes__main_accords").get(pk=request.user.pk)
        serializer = MyPageSerializer(user)
        return Response(
            {"code": 200, "message": "마이페이지 정보 조회 성공", "data": serializer.data}, status=status.HTTP_200_OK
        )

class MyPageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = MyPageUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"code": 400, "message": "입력 형식이 잘못되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        data = {
            "user_id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "phone_number": user.phone_number,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "gender": user.gender,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
        return Response(
            {"code": 200, "message": "마이페이지 정보 수정 성공", "data": data},
            status=status.HTTP_200_OK,
        )