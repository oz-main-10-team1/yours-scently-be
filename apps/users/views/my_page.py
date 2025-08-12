from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

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

        # 유효성 실패 시 우리 포맷으로만 반환( errors 키 없음 )
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(
                {"code": 400, "message": "입력 형식이 잘못되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        data = MyPageSerializer(user).data
        return Response(
            {"code": 200, "message": "마이페이지 정보 수정 성공", "data": data},
            status=status.HTTP_200_OK,
        )